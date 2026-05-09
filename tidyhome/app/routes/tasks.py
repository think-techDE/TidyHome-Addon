from datetime import date, timedelta
from html import escape
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_persons
from models import Task
from reminders import (send_task_assignment_notifications, send_task_reminders,
                       task_reminder_recipients)
from render import (INTERVALS, _base, _icon, _icon_chooser, _selected,
                    _task_icon, comments_card, format_date_de, interval_label,
                    person_suffix, photos_card, render, resolve_person,
                    task_row)
from storage import (add_comment, add_photo, create_task, delete_photo, delete_task,
                     edit_task, filter_tasks_by_role,
                     get_admins, get_person_settings, get_task, get_vacation_mode,
                     is_vacation_mode_active, list_people_by_role,
                     list_task_history, list_tasks, mark_done, reactivate_task,
                     snooze_task)
from uploads import selected_photo_upload

router = APIRouter(prefix="/tasks")

_EFFORT_LABELS = {"low": "Wenig", "medium": "Mittel", "high": "Viel"}
_EFFORT_BADGE  = {"low": "ok", "medium": "today", "high": "overdue"}
_ONETIME_INTERVAL = "once"


def _parse_interval_choice(value: str, legacy_onetime: str = "") -> tuple[int, bool]:
    value = str(value or _ONETIME_INTERVAL).strip()
    if value == _ONETIME_INTERVAL:
        return 0, True
    try:
        days = int(value)
    except ValueError:
        return 0, True
    if days <= 0:
        return 0, True
    return days, legacy_onetime == "1"


def _task_return_path(return_to: str = "") -> str:
    return "tasks/history" if return_to == "history" else "tasks"


def _save_initial_task_note(task: Task, note: str, author: str = "") -> bool:
    return bool(add_comment("task", task.id, note, author=author))


async def _save_initial_task_photo(task: Task, author: str = "",
                                   photo: UploadFile | None = None,
                                   photo_camera: UploadFile | None = None,
                                   photo_file: UploadFile | None = None) -> bool:
    selected_photo, data = await selected_photo_upload(photo, photo_camera, photo_file)
    if not selected_photo:
        return False
    return bool(add_photo("task", task.id, "before", selected_photo.filename or "",
                          selected_photo.content_type or "", data, author=author))


@router.get("", response_class=HTMLResponse)
async def tasks_list(request: Request, room: str = None, person: str = None,
                     overdue: str = None, effort: str = None,
                     p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    tasks = list_tasks(room=room, assigned_to=person,
                       overdue_only=(overdue == "1"), effort=effort or None)

    # Hidden rooms
    if p:
        hidden = set(get_person_settings(p).get("hidden_rooms", []))
        if hidden:
            tasks = [t for t in tasks if t.room not in hidden]

    areas = await get_areas()
    psuffix = f"&p={p}" if p else ""

    # Filter bar
    all_active = not room and not overdue and not effort
    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if all_active else ""}" href="tasks{("?p="+p) if p else ""}">Alle</a>'
    filters += f'<a class="filter-btn" href="tasks/history{("?p="+p) if p else ""}">Historie</a>'
    filters += f'<a class="filter-btn {"active" if overdue == "1" else ""}" href="tasks?overdue=1{psuffix}">Überfällig</a>'
    for ef, label in _EFFORT_LABELS.items():
        filters += f'<a class="filter-btn {"active" if effort == ef else ""}" href="tasks?effort={ef}{psuffix}">{label}</a>'
    for r in areas:
        filters += f'<a class="filter-btn {"active" if room == r else ""}" href="tasks?room={r}{psuffix}">{r}</a>'
    filters += '</div>'

    # Grouped view for parent/admin + room filter
    cfg_p = get_person_settings(p) if p else {}
    role_p = cfg_p.get("role", "member")
    show_grouped = room and p and (p in admins or role_p == "parent")

    if show_grouped and role_p == "parent" and p not in admins:
        child_persons = list_people_by_role("child")
        tasks = [
            t for t in tasks
            if p in t.assigned_to or any(pn in child_persons for pn in t.assigned_to)
        ]
    elif not show_grouped:
        tasks = filter_tasks_by_role(tasks, p, admins)

    vacation_active = is_vacation_mode_active(p)
    vacation_until = get_vacation_mode(p).get("until", "") if vacation_active else ""

    def _is_paused_for_view(t: Task) -> bool:
        return bool(vacation_active and p and p in t.assigned_to)

    rows = ""
    if not tasks:
        rows = (
            '<div class="empty">'
            '<div class="empty-icon">✅</div>'
            '<div style="font-weight:600">Keine Aufgaben gefunden</div>'
            '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            'Alle erledigt oder kein Filter passend.</div>'
            '</div>'
        )
    elif show_grouped:
        from collections import defaultdict
        grouped: dict[str, list[Task]] = defaultdict(list)
        for t in tasks:
            if t.assigned_to:
                for pn in t.assigned_to:
                    grouped[pn].append(t)
            else:
                grouped["— Nicht zugeordnet —"].append(t)
        for person_name, ptasks in sorted(grouped.items()):
            rows += (
                f'<div style="padding:0.5rem 1.25rem;font-size:0.72rem;font-weight:700;'
                f'color:var(--primary-dark);text-transform:uppercase;letter-spacing:0.06em;'
                f'background:var(--primary-light);display:flex;align-items:center;gap:0.4rem">'
                f'{_icon("person", 13, "var(--primary-dark)")} {person_name}</div>'
            )
            for t in ptasks:
                rows += task_row(
                    t, person=p, show_assigned=show_grouped,
                    paused=_is_paused_for_view(t), vacation_until=vacation_until
                )
    else:
        for t in tasks:
            rows += task_row(
                t, person=p, show_assigned=show_grouped,
                paused=_is_paused_for_view(t), vacation_until=vacation_until
            )

    psuffix_q = f"?p={p}" if p else ""
    active_tasks = [t for t in tasks if not _is_paused_for_view(t)]
    overdue_count = len([t for t in active_tasks if t.days_until_due() < 0])
    today_count = len([t for t in active_tasks if t.days_until_due() == 0])
    planned_count = len(active_tasks) - overdue_count - today_count
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">Heute im Blick</div>
        <div class="hero-title">Aufgaben</div>
      </div>
      <div class="page-hero-actions">
        <a class="btn btn-primary btn-sm" href="tasks/new{psuffix_q}">
          {_icon("plus", 14, "white")} Neu
        </a>
      </div>
    </div>
    <div class="today-grid" style="margin-bottom:1rem">
      <div class="today-stat">
        <div class="today-value">{today_count}</div>
        <div class="today-label">Heute</div>
      </div>
      <div class="today-stat">
        <div class="today-value">{overdue_count}</div>
        <div class="today-label">Offen spät</div>
      </div>
      <div class="today-stat">
        <div class="today-value">{planned_count}</div>
        <div class="today-label">Geplant</div>
      </div>
    </div>
    {filters}
    <div class="card card-flush">{rows}</div>"""

    return render(content, request, page="tasks", person=p)


def _task_history_row(task: Task, person: str = "") -> str:
    psuffix = person_suffix(person)
    qs = f"{psuffix}{'&' if psuffix else '?'}return_to=history"
    assigned = ", ".join(task.assigned_to) if task.assigned_to else "Nicht zugeordnet"
    done_label = format_date_de(task.last_done or "")
    if task.active:
        status_badge = '<span class="badge ok">Erledigt</span>'
        action_label = "Erneut öffnen"
    else:
        status_badge = '<span class="badge today">Archiviert</span>'
        action_label = "Wieder aktivieren"
    interval = "Einmalig" if task.onetime else interval_label(task.interval_days)
    done_meta = f"Erledigt am {done_label}" if done_label else "Archiviert"
    return f"""
    <div class="task-row history-row">
      {_task_icon(task.name, task.room, icon=task.icon, size=40)}
      <div class="task-body">
        <div class="task-header">
          <span class="task-name">{escape(task.name)}</span>
          <div class="task-badges">{status_badge}</div>
        </div>
        <div class="task-date">
          <span>{escape(done_meta)}</span>
          <span>· {escape(task.room)}</span>
          <span>· {escape(assigned)}</span>
          <span>· {escape(interval)}</span>
        </div>
      </div>
      <div class="task-actions">
        <a class="icon-btn" href="tasks/{task.id}/edit{qs}"
           title="Bearbeiten">{_icon("edit", 16)}</a>
        <form class="inline" method="post" action="tasks/{task.id}/reactivate">
          <input type="hidden" name="return_p" value="{escape(person)}">
          <input type="hidden" name="return_to" value="history">
          <button class="icon-btn success" title="{action_label}">{_icon("plus", 17)}</button>
        </form>
        <a class="icon-btn danger" href="tasks/{task.id}/delete{qs}"
           onclick="return confirm('Aufgabe endgültig löschen?')" title="Löschen">
          {_icon("trash", 16)}
        </a>
      </div>
    </div>"""


@router.get("/history", response_class=HTMLResponse)
async def tasks_history(request: Request, p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    tasks = list_task_history()
    if p:
        hidden = set(get_person_settings(p).get("hidden_rooms", []))
        if hidden:
            tasks = [t for t in tasks if t.room not in hidden]
    tasks = filter_tasks_by_role(tasks, p, admins)
    rows = "".join(_task_history_row(t, p) for t in tasks)
    if not rows:
        rows = (
            '<div class="empty">'
            '<div class="empty-icon">↺</div>'
            '<div style="font-weight:600">Noch keine erledigten Aufgaben</div>'
            '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            'Sobald Aufgaben erledigt oder archiviert wurden, erscheinen sie hier.</div>'
            '</div>'
        )

    psuffix_q = f"?p={p}" if p else ""
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">Nacharbeiten und reaktivieren</div>
        <div class="hero-title">Aufgaben-Historie</div>
      </div>
      <div class="page-hero-actions">
        <a class="btn btn-ghost btn-sm" href="tasks{psuffix_q}">
          {_icon("chevron_l", 14)} Aktive
        </a>
      </div>
    </div>
    <div class="filters">
      <a class="filter-btn" href="tasks{psuffix_q}">Aktive Aufgaben</a>
      <a class="filter-btn active" href="tasks/history{psuffix_q}">Historie</a>
    </div>
    <div class="card card-flush">{rows}</div>"""
    return render(content, request, page="tasks", person=p)


@router.get("/new", response_class=HTMLResponse)
async def task_new_form(request: Request, p: str = ""):
    p = resolve_person(request, p)
    return await _task_form(request, "Neue Aufgabe", "tasks", "Aufgabe anlegen", person=p)


@router.get("/{task_id}/edit", response_class=HTMLResponse)
async def task_edit_form(task_id: str, request: Request, p: str = "",
                         return_to: str = ""):
    p = resolve_person(request, p)
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)
    return await _task_form(request, "Aufgabe bearbeiten", f"tasks/{task_id}/edit",
                            "Speichern", task=task, person=p,
                            return_to=return_to)


@router.post("/{task_id}/edit")
async def task_edit(task_id: str, request: Request,
                    name: str = Form(...), room: str = Form(...),
                    interval_days: str = Form(_ONETIME_INTERVAL), points: int = Form(10),
                    important: str = Form(""), onetime: str = Form(""),
                    icon: str = Form(""), effort: str = Form(""),
                    start_date: str = Form(""), snooze_until: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    parsed_interval, parsed_onetime = _parse_interval_choice(interval_days, onetime)
    if not edit_task(task_id, name=name, room=room, interval_days=parsed_interval,
                     assigned_to=assigned_to, points=points,
                     important=(important == "1"), onetime=parsed_onetime,
                     icon=icon, effort=effort,
                     start_date=start_date, snooze_until=snooze_until):
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    return_to = str(form.get("return_to") or "")
    return RedirectResponse(
        _base(request) + f"{_task_return_path(return_to)}{person_suffix(return_p)}",
        status_code=303
    )


@router.post("")
async def task_create(request: Request, name: str = Form(...), room: str = Form(...),
                      interval_days: str = Form(_ONETIME_INTERVAL), points: int = Form(10),
                      important: str = Form(""), onetime: str = Form(""),
                      icon: str = Form(""), effort: str = Form(""),
                      start_date: str = Form(""),
                      photo: UploadFile | None = File(None),
                      photo_camera: UploadFile | None = File(None),
                      photo_file: UploadFile | None = File(None)):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    parsed_interval, parsed_onetime = _parse_interval_choice(interval_days, onetime)
    task = Task(name=name, room=room, interval_days=parsed_interval,
                assigned_to=assigned_to, points=points,
                important=(important == "1"), onetime=parsed_onetime,
                icon=icon, effort=effort,
                start_date=start_date or None)
    create_task(task)
    return_p = str(form.get("return_p") or "")
    creator = resolve_person(request, return_p)
    _save_initial_task_note(task, str(form.get("initial_note") or ""), author=creator)
    await _save_initial_task_photo(task, author=creator, photo=photo,
                                   photo_camera=photo_camera, photo_file=photo_file)
    await send_task_assignment_notifications(task, sender=creator)
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


@router.post("/{task_id}/done")
async def task_done(task_id: str, request: Request):
    form = await request.form()
    task = mark_done(task_id, done_by=form.get("done_by") or None)
    if not task:
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    done_by = str(form.get("done_by") or "") or (task.assigned_to[0] if task.assigned_to else "")
    msg = (
        f"+{task.points} Punkte für {task.name}"
        if done_by else
        f"{task.name} erledigt"
    )
    sep = "&" if return_p else "?"
    return RedirectResponse(
        _base(request) + f"tasks{person_suffix(return_p)}{sep}msg={quote(msg)}",
        status_code=303
    )


@router.get("/{task_id}/snooze", response_class=HTMLResponse)
async def task_snooze_form(task_id: str, request: Request, p: str = ""):
    p = resolve_person(request, p)
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)
    base = _base(request)
    psuffix_q = f"?p={p}" if p else ""
    today = date.today()

    quick_btns = ""
    for days, label in [(1, "+1 Tag"), (3, "+3 Tage"), (7, "+1 Woche"), (14, "+2 Wochen"), (30, "+1 Monat")]:
        d = (today + timedelta(days=days)).isoformat()
        quick_btns += (
            f'<button type="submit" name="until" value="{d}" class="btn btn-ghost btn-sm">'
            f'{label}</button>'
        )

    cur_snooze = task.snooze_until or ""
    clear_btn = ""
    if task.snooze_until:
        clear_btn = (
            f'<form method="post" action="tasks/{task_id}/snooze" style="margin-top:0.5rem">'
            f'<input type="hidden" name="return_p" value="{p}">'
            f'<input type="hidden" name="until" value="">'
            f'<button class="btn btn-ghost btn-sm btn-full" type="submit">'
            f'Verschiebung aufheben</button></form>'
        )

    content = f"""
    <div class="page-header">
      <h2>Verschieben</h2>
      <a class="icon-btn" href="tasks{psuffix_q}" title="Abbrechen">{_icon("chevron_l", 20)}</a>
    </div>
    <div class="card" style="margin-bottom:0.75rem">
      <div style="font-weight:600;margin-bottom:0.2rem">{task.name}</div>
      <div class="task-meta">{task.room} · Fällig: {task.next_due().strftime('%-d. %b %Y')}</div>
    </div>
    <div class="card">
      <div style="font-size:0.8rem;font-weight:650;color:var(--muted);
                  margin-bottom:0.65rem;text-transform:uppercase;letter-spacing:0.05em">
        Schnell verschieben
      </div>
      <form method="post" action="tasks/{task_id}/snooze">
        <input type="hidden" name="return_p" value="{p}">
        <div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:1rem">
          {quick_btns}
        </div>
        <div style="font-size:0.8rem;font-weight:650;color:var(--muted);
                    margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.05em">
          Eigenes Datum
        </div>
        <div style="display:flex;gap:0.5rem;align-items:center">
          <input type="date" name="until" value="{cur_snooze}"
                 min="{(today + timedelta(days=1)).isoformat()}"
                 style="flex:1">
          <button class="btn btn-primary btn-sm" type="submit">OK</button>
        </div>
      </form>
      {clear_btn}
    </div>"""

    return render(content, request, page="tasks", person=p)


@router.post("/{task_id}/snooze")
async def task_snooze(task_id: str, request: Request):
    form = await request.form()
    until = str(form.get("until") or "")
    if not snooze_task(task_id, until):
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


@router.get("/{task_id}/remind", response_class=HTMLResponse)
async def task_remind_form(task_id: str, request: Request, p: str = ""):
    p = resolve_person(request, p)
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)

    recipients = task_reminder_recipients(task, p)
    if not recipients:
        msg = quote("Keine anderen Empfänger für diese Aufgabe")
        sep = "&" if p else "?"
        return RedirectResponse(_base(request) + f"tasks{person_suffix(p)}{sep}msg={msg}", status_code=303)

    recipient_label = ", ".join(recipients)
    default_message = f"Kannst du bitte an {task.name} denken?"
    psuffix_q = f"?p={p}" if p else ""
    content = f"""
    <div class="page-header">
      <h2>Erinnerung senden</h2>
      <a class="icon-btn" href="tasks{psuffix_q}" title="Abbrechen">{_icon("chevron_l", 20)}</a>
    </div>
    <div class="card" style="margin-bottom:0.75rem">
      <div style="font-weight:600;margin-bottom:0.2rem">{task.name}</div>
      <div class="task-meta">{task.room} · {", ".join(task.assigned_to) if task.assigned_to else "Nicht zugeordnet"}</div>
    </div>
    <div class="card">
      <form method="post" action="tasks/{task_id}/remind">
        <input type="hidden" name="return_p" value="{p}">
        <div class="form-group">
          <label>Erinnerung an</label>
          <div style="padding:0.7rem 0.8rem;border:1px solid var(--border);
                      border-radius:8px;background:var(--bg-soft);font-weight:600">
            {recipient_label}
          </div>
        </div>
        <div class="form-group">
          <label>Nachricht</label>
          <textarea name="message" rows="3" required>{escape(default_message)}</textarea>
        </div>
        <button class="btn btn-primary btn-full" type="submit">Erinnerung senden</button>
        <a class="btn btn-ghost btn-full" href="tasks{psuffix_q}" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="tasks", person=p)


@router.post("/{task_id}/remind")
async def task_remind_send(task_id: str, request: Request,
                           message: str = Form(...),
                           return_p: str = Form("")):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)

    sender = resolve_person(request, return_p)
    recipients = task_reminder_recipients(task, sender)
    sent = False
    if recipients:
        sent = await send_task_reminders(task, recipients, message, sender=sender)
    target_label = ", ".join(recipients)
    msg = (
        f"Erinnerung an {target_label} gesendet"
        if sent else
        f"Erinnerung für {target_label or 'niemanden'} als Notiz gespeichert"
    )
    sep = "&" if return_p else "?"
    return RedirectResponse(
        _base(request) + f"tasks{person_suffix(return_p)}{sep}msg={quote(msg)}",
        status_code=303
    )


@router.post("/{task_id}/comments")
async def task_comment_add(task_id: str, request: Request,
                           text: str = Form(...), return_p: str = Form("")):
    if not get_task(task_id):
        raise HTTPException(404)
    author = resolve_person(request, return_p)
    add_comment("task", task_id, text, author=author)
    return RedirectResponse(_base(request) + f"tasks/{task_id}/edit{person_suffix(return_p)}", status_code=303)


@router.post("/{task_id}/photos")
async def task_photo_add(task_id: str, request: Request,
                         photo_type: str = Form("before"),
                         return_p: str = Form(""),
                         photo: UploadFile | None = File(None),
                         photo_camera: UploadFile | None = File(None),
                         photo_file: UploadFile | None = File(None)):
    if not get_task(task_id):
        raise HTTPException(404)
    selected_photo, data = await selected_photo_upload(photo, photo_camera, photo_file)
    if not selected_photo:
        raise HTTPException(400, "Kein Foto ausgewählt")
    author = resolve_person(request, return_p)
    add_photo("task", task_id, photo_type, selected_photo.filename or "",
              selected_photo.content_type or "", data, author=author)
    return RedirectResponse(_base(request) + f"tasks/{task_id}/edit{person_suffix(return_p)}", status_code=303)


@router.get("/{task_id}/photos/{photo_id}/delete")
async def task_photo_delete(task_id: str, photo_id: str, request: Request, p: str = ""):
    delete_photo(photo_id, "task", task_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"tasks/{task_id}/edit{person_suffix(p)}", status_code=303)


@router.post("/{task_id}/reactivate")
async def task_reactivate(task_id: str, request: Request):
    form = await request.form()
    if not reactivate_task(task_id):
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    return_to = str(form.get("return_to") or "")
    sep = "&" if return_p else "?"
    return RedirectResponse(
        _base(request)
        + f"{_task_return_path(return_to)}{person_suffix(return_p)}"
        + f"{sep}msg={quote('Aufgabe wieder aktiviert')}",
        status_code=303
    )


@router.get("/{task_id}/delete")
async def task_delete(task_id: str, request: Request, p: str = "",
                      return_to: str = ""):
    delete_task(task_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(
        _base(request) + f"{_task_return_path(return_to)}{person_suffix(p)}",
        status_code=303
    )


async def _task_form(request: Request, title: str, action: str,
                     submit_label: str, task=None, person: str = "",
                     return_to: str = "") -> HTMLResponse:
    areas   = await get_areas()
    persons = await get_persons()
    cur_room       = task.room if task else ""
    cur_interval   = task.interval_days if task else 0
    cur_persons    = task.assigned_to if task else ([person] if person else [])
    cur_points     = task.points if task else 10
    cur_name       = task.name if task else ""
    cur_important  = task.important if task else False
    cur_onetime    = task.onetime if task else True
    cur_icon       = task.icon if task else ""
    cur_effort     = task.effort if task else ""
    cur_start_date = task.start_date or "" if task else ""
    cur_snooze     = task.snooze_until or "" if task else ""

    room_opts = "".join(
        f'<option value="{r}"{_selected(r, cur_room)}>{r}</option>' for r in areas)
    person_boxes = "".join(
        f'<label class="option-card" style="padding:0.55rem 0.7rem">'
        f'<input type="checkbox" name="assigned_to" value="{pn}"'
        f'{" checked" if pn in cur_persons else ""}'
        f'><span>{pn}</span></label>'
        for pn in persons
    )
    cur_interval_choice = _ONETIME_INTERVAL if cur_onetime else str(cur_interval)
    interval_opts = (
        f'<option value="{_ONETIME_INTERVAL}"'
        f'{_selected(_ONETIME_INTERVAL, cur_interval_choice)}>'
        'Einmalig (nach Erledigung archiviert)</option>'
    )
    interval_opts += "".join(
        f'<option value="{d}"{_selected(d, cur_interval)}>{label}</option>'
        for d, label in INTERVALS.items())

    effort_btns = ""
    for ef, label in _EFFORT_LABELS.items():
        effort_btns += (
            f'<label class="effort-choice effort-{ef}">'
            f'<input type="radio" name="effort" value="{ef}"'
            f'{" checked" if cur_effort == ef else ""}>'
            f'<span>{label}</span>'
            f'</label>'
        )
    effort_btns += (
        f'<label class="effort-choice effort-none">'
        f'<input type="radio" name="effort" value=""'
        f'{" checked" if not cur_effort else ""}>'
        f'<span>Ohne</span>'
        f'</label>'
    )

    important_checked = "checked" if cur_important else ""
    from render import _icon as _i
    star_svg = _i("star", 15, "var(--warning)")

    # Snooze-Sektion nur beim Bearbeiten anzeigen
    snooze_section = ""
    if task:
        snooze_section = f"""
        <div class="form-group">
          <label>Fälligkeit einmalig verschieben</label>
          <input type="date" name="snooze_until" value="{cur_snooze}"
                 min="{(date.today() + timedelta(days=1)).isoformat()}">
          <div class="task-meta" style="margin-top:0.3rem">
            Leer lassen = keine Verschiebung aktiv
          </div>
        </div>"""

    psuffix_q = f"?p={person}" if person else ""
    back_path = _task_return_path(return_to)
    back_url = f"{back_path}{psuffix_q}"
    comments = (
        comments_card("task", task.id, f"tasks/{task.id}/comments", person,
                      margin_top=True)
        if task else ""
    )
    photos = (
        photos_card("task", task.id, f"tasks/{task.id}/photos", person,
                    title="Aufgaben-Fotos", margin_top=True)
        if task else ""
    )
    initial_note = "" if task else """
        <div class="form-group">
          <label>Notiz (optional)</label>
          <textarea name="initial_note" rows="3"
                    placeholder="Hinweis oder Absprache direkt mit anlegen"></textarea>
        </div>"""
    initial_photo = ""
    if not task:
        live_input_id = "task-new-photo-live"
        camera_input_id = "task-new-photo-camera"
        file_input_id = "task-new-photo-file"
        initial_photo = f"""
        <div class="task-form-section">
          <div class="task-form-section-title">Vorher-Foto</div>
          <div class="task-create-photo-card photos-card photo-pending-card">
            <input id="{live_input_id}" class="photo-file-input photo-live-input" type="file"
                   name="photo" accept="image/*">
            <input id="{camera_input_id}" class="photo-file-input" type="file"
                   name="photo_camera" accept="image/*,android/force-camera-workaround"
                   capture="environment">
            <input id="{file_input_id}" class="photo-file-input" type="file"
                   name="photo_file" accept="image/*">
            <div class="photo-actions">
              <label class="btn btn-ghost btn-sm camera-native-button" for="{camera_input_id}">
                {_i("camera", 14)} Kamera öffnen
              </label>
              <button class="btn btn-ghost btn-sm camera-start" type="button" hidden>
                {_i("camera", 14)} Kamera öffnen
              </button>
              <label class="btn btn-outline btn-sm photo-file-button" for="{file_input_id}">
                {_i("plus", 14)} Datei auswählen
              </label>
            </div>
            <div class="camera-panel" hidden>
              <video class="camera-preview" playsinline autoplay muted></video>
              <div class="camera-actions">
                <button class="btn btn-primary btn-sm camera-shot" type="button">
                  {_i("camera", 14, "white")} Aufnehmen
                </button>
                <button class="btn btn-ghost btn-sm camera-stop" type="button">Schließen</button>
              </div>
            </div>
            <div class="camera-msg muted"></div>
            <div class="muted photo-upload-hint">
              Optional. Das Vorher-Foto wird zusammen mit der Aufgabe gespeichert.
            </div>
          </div>
        </div>"""
    priority_option = f"""
        <label class="option-card task-priority-card">
          <input type="checkbox" name="important" value="1" {important_checked}>
          <span class="task-priority-main">
            <span class="task-priority-title">
              {star_svg} Als wichtig markieren
            </span>
            <span class="task-priority-hint">
              Wichtige Aufgaben werden in Listen hervorgehoben und weiter oben einsortiert.
            </span>
          </span>
        </label>"""

    content = f"""
    <div class="page-header">
      <h2>{title}</h2>
      <a class="icon-btn" href="{back_url}" title="Abbrechen">{_i("chevron_l", 20)}</a>
    </div>
    <div class="card task-form-card">
      <form method="post" action="{action}" enctype="multipart/form-data">
        <input type="hidden" name="return_p" value="{person}">
        <input type="hidden" name="return_to" value="{return_to}">
        <div class="task-form-section">
          <div class="task-form-section-title">Aufgabe</div>
          <div class="form-group">
            <label>Was ist zu erledigen?</label>
            <input name="name" required placeholder="z.B. Staubsaugen" value="{escape(cur_name)}">
          </div>
          {priority_option}
          {initial_note}
        </div>
        {initial_photo}

        <div class="task-form-section">
          <div class="task-form-section-title">Planung</div>
          <div class="grid-2">
            <div class="form-group">
              <label>Raum</label>
              <select name="room">{room_opts}</select>
            </div>
            <div class="form-group">
              <label>Intervall</label>
              <select name="interval_days">{interval_opts}</select>
            </div>
            <div class="form-group">
              <label>Punkte</label>
              <input name="points" type="number" value="{cur_points}" min="1" max="100">
            </div>
            <div class="form-group">
              <label>Startdatum (optional)</label>
              <input type="date" name="start_date" value="{cur_start_date}">
            </div>
          </div>
          <div class="form-group">
            <label>Aufwand</label>
            <div class="effort-picker">{effort_btns}</div>
          </div>
          {snooze_section}
        </div>

        <div class="task-form-section">
          <div class="task-form-section-title">Zuständigkeit</div>
          <div class="form-group">
            <label>Zugewiesen an</label>
            <div class="task-assignee-grid">{person_boxes}</div>
          </div>
        </div>

        <div class="task-form-section">
          <div class="task-form-section-title">Darstellung</div>
          {_icon_chooser(cur_icon)}
        </div>

        <div class="form-actions">
          <button class="btn btn-primary btn-full" type="submit">{submit_label}</button>
          <a class="btn btn-ghost btn-full" href="{back_url}">Abbrechen</a>
        </div>
      </form>
    </div>
    {photos}
    {comments}"""
    return render(content, request, page="tasks", person=person)
