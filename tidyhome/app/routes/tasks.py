from datetime import date, timedelta
from html import escape

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_persons
from models import Task
from reminders import send_task_reminder
from render import (INTERVALS, _base, _icon, _icon_chooser, _selected, _task_icon,
                    comments_card, format_date_de, interval_label, person_suffix,
                    render, resolve_person, urgency_class)
from storage import (add_comment, create_task, delete_task, edit_task, filter_tasks_by_role,
                     get_admins, get_person_settings, get_task, get_vacation_mode,
                     is_vacation_mode_active, list_people_by_role, list_tasks,
                     mark_done, snooze_task)

router = APIRouter(prefix="/tasks")

_EFFORT_LABELS = {"low": "Wenig", "medium": "Mittel", "high": "Viel"}
_EFFORT_BADGE  = {"low": "ok", "medium": "today", "high": "overdue"}


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

    base = _base(request)

    def _task_row(t: Task) -> str:
        due = t.days_until_due()
        paused = _is_paused_for_view(t)

        if due < 0:
            badge_text, badge_cls = "Überfällig", "overdue"
            date_text = f"{abs(due)}d überfällig"
        elif due == 0:
            badge_text, badge_cls = "Heute", "today"
            date_text = "Heute"
        else:
            badge_text, badge_cls = "Geplant", "ok"
            date_text = "Morgen" if due == 1 else f"In {due} Tagen"

        # Snooze-Hinweis überschreibt den Datumstext
        if t.snooze_until:
            try:
                snooze_d = date.fromisoformat(t.snooze_until)
                if snooze_d > date.today():
                    date_text = f"Verschoben bis {snooze_d.strftime('%-d. %b')}"
                    badge_text, badge_cls = "Verschoben", "ok"
            except ValueError:
                pass

        if paused:
            badge_text, badge_cls = "Pausiert", "ok"
            date_text = (
                f"Pausiert bis {format_date_de(vacation_until)}"
                if vacation_until else
                "Pausiert"
            )

        important_cls = " important" if t.important else ""
        star = f'{_icon("star", 13, "var(--warning)", 2.5)}' if t.important else ""
        onetime_badge = (
            '<span class="badge" style="background:var(--muted);color:#fff;'
            'font-size:0.62rem;flex-shrink:0">1×</span>'
        ) if t.onetime else ""
        effort_badge = (
            f'<span class="badge {_EFFORT_BADGE[t.effort]}" '
            f'style="font-size:0.62rem;flex-shrink:0">{_EFFORT_LABELS[t.effort]}</span>'
        ) if t.effort in _EFFORT_LABELS else ""
        sub_badges = f'<div class="task-badge-subrow">{effort_badge}{onetime_badge}</div>' if effort_badge or onetime_badge else ""

        assigned_txt = ""
        if t.assigned_to and show_grouped:
            assigned_txt = (
                f'<span class="task-meta" style="font-size:0.72rem">'
                f'→ {", ".join(t.assigned_to)}</span>'
            )
        task_meta_inline = f'<span class="task-name-meta"> · {date_text}</span>'

        done_btn = (
            f'<form class="inline" method="post" action="tasks/{t.id}/done">'
            + (f'<input type="hidden" name="done_by" value="{p}">' if p else "")
            + (f'<input type="hidden" name="return_p" value="{p}">' if p else "")
            + f'<button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>'
            f'</form>'
        )
        snooze_btn = (
            f'<a class="icon-btn" href="tasks/{t.id}/snooze{person_suffix(p)}" '
            f'title="Verschieben">{_icon("clock", 16)}</a>'
        )
        remind_btn = (
            f'<a class="icon-btn" href="tasks/{t.id}/remind{person_suffix(p)}" '
            f'title="Erinnern">{_icon("bell", 16)}</a>'
        )
        edit_btn = (
            f'<a class="icon-btn" href="tasks/{t.id}/edit{person_suffix(p)}" title="Bearbeiten">'
            f'{_icon("edit", 16)}</a>'
        )
        del_btn = (
            f'<a class="icon-btn danger" href="tasks/{t.id}/delete{person_suffix(p)}" '
            f'onclick="return confirm(\'Aufgabe löschen?\')" title="Löschen">'
            f'{_icon("trash", 16)}</a>'
        )

        return f"""
        <div class="task-row{important_cls}">
          {_task_icon(t.name, t.room, icon=t.icon, size=40)}
          <div class="task-body">
            <div class="task-header">
              <span class="task-name">{star}{t.name}{task_meta_inline}</span>
              <div class="task-badges">
                <span class="badge {badge_cls}">{badge_text}</span>
                {sub_badges}
              </div>
            </div>
            {f'<div class="task-date">{assigned_txt}</div>' if assigned_txt else ''}
          </div>
          <div class="task-actions">
            {done_btn}{snooze_btn}{remind_btn}{edit_btn}{del_btn}
          </div>
        </div>"""

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
                rows += _task_row(t)
    else:
        for t in tasks:
            rows += _task_row(t)

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


@router.get("/new", response_class=HTMLResponse)
async def task_new_form(request: Request, p: str = ""):
    p = resolve_person(request, p)
    return await _task_form(request, "Neue Aufgabe", "tasks", "Aufgabe anlegen", person=p)


@router.get("/{task_id}/edit", response_class=HTMLResponse)
async def task_edit_form(task_id: str, request: Request, p: str = ""):
    p = resolve_person(request, p)
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)
    return await _task_form(request, "Aufgabe bearbeiten", f"tasks/{task_id}/edit",
                            "Speichern", task=task, person=p)


@router.post("/{task_id}/edit")
async def task_edit(task_id: str, request: Request,
                    name: str = Form(...), room: str = Form(...),
                    interval_days: int = Form(...), points: int = Form(10),
                    important: str = Form(""), onetime: str = Form(""),
                    icon: str = Form(""), effort: str = Form(""),
                    start_date: str = Form(""), snooze_until: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    if not edit_task(task_id, name=name, room=room, interval_days=interval_days,
                     assigned_to=assigned_to, points=points,
                     important=(important == "1"), onetime=(onetime == "1"),
                     icon=icon, effort=effort,
                     start_date=start_date, snooze_until=snooze_until):
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


@router.post("")
async def task_create(request: Request, name: str = Form(...), room: str = Form(...),
                      interval_days: int = Form(...), points: int = Form(10),
                      important: str = Form(""), onetime: str = Form(""),
                      icon: str = Form(""), effort: str = Form(""),
                      start_date: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    task = Task(name=name, room=room, interval_days=interval_days,
                assigned_to=assigned_to, points=points,
                important=(important == "1"), onetime=(onetime == "1"),
                icon=icon, effort=effort,
                start_date=start_date or None)
    create_task(task)
    return_p = str(form.get("return_p") or "")
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


@router.post("/{task_id}/done")
async def task_done(task_id: str, request: Request):
    form = await request.form()
    if not mark_done(task_id, done_by=form.get("done_by") or None):
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


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

    people = task.assigned_to or await get_persons()
    person_opts = "".join(
        f'<option value="{pn}"{_selected(pn, p)}>{pn}</option>'
        for pn in people
    )
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
          <select name="target_person">{person_opts}</select>
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
                           target_person: str = Form(...),
                           message: str = Form(...),
                           return_p: str = Form("")):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)

    sender = resolve_person(request, return_p)
    await send_task_reminder(task, target_person, message, sender=sender)
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


@router.post("/{task_id}/comments")
async def task_comment_add(task_id: str, request: Request,
                           text: str = Form(...), return_p: str = Form("")):
    if not get_task(task_id):
        raise HTTPException(404)
    author = resolve_person(request, return_p)
    add_comment("task", task_id, text, author=author)
    return RedirectResponse(_base(request) + f"tasks/{task_id}/edit{person_suffix(return_p)}", status_code=303)


@router.get("/{task_id}/delete")
async def task_delete(task_id: str, request: Request, p: str = ""):
    delete_task(task_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"tasks{person_suffix(p)}", status_code=303)


async def _task_form(request: Request, title: str, action: str,
                     submit_label: str, task=None, person: str = "") -> HTMLResponse:
    areas   = await get_areas()
    persons = await get_persons()
    cur_room       = task.room if task else ""
    cur_interval   = task.interval_days if task else 7
    cur_persons    = task.assigned_to if task else ([person] if person else [])
    cur_points     = task.points if task else 10
    cur_name       = task.name if task else ""
    cur_important  = task.important if task else False
    cur_onetime    = task.onetime if task else False
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
    interval_opts = "".join(
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
    onetime_checked   = "checked" if cur_onetime   else ""
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
    comments = (
        comments_card("task", task.id, f"tasks/{task.id}/comments", person,
                      margin_top=True)
        if task else ""
    )

    content = f"""
    <div class="page-header">
      <h2>{title}</h2>
      <a class="icon-btn" href="tasks{psuffix_q}" title="Abbrechen">{_i("chevron_l", 20)}</a>
    </div>
    <div class="card">
      <form method="post" action="{action}">
        <input type="hidden" name="return_p" value="{person}">
        <div class="form-group">
          <label>Was ist zu erledigen?</label>
          <input name="name" required placeholder="z.B. Staubsaugen" value="{cur_name}">
        </div>
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
        <div class="form-group">
          <label>Zugewiesen an</label>
          <div style="display:flex;flex-wrap:wrap;gap:0.45rem">{person_boxes}</div>
        </div>
        {_icon_chooser(cur_icon)}
        <div class="form-group">
          <label class="option-card">
            <input type="checkbox" name="important" value="1" {important_checked}>
            <span style="display:flex;align-items:center;gap:0.4rem">
              {star_svg} Als wichtig markieren
            </span>
          </label>
        </div>
        <div class="form-group">
          <label class="option-card">
            <input type="checkbox" name="onetime" value="1" {onetime_checked}>
            <span style="display:flex;align-items:center;gap:0.4rem">
              <span class="badge ok" style="font-size:0.62rem;padding:0.15rem 0.4rem">1×</span>
              Einmalige Aufgabe (nach Erledigung archiviert)
            </span>
          </label>
        </div>
        {snooze_section}
        <button class="btn btn-primary btn-full" type="submit">{submit_label}</button>
        <a class="btn btn-ghost btn-full" href="tasks{psuffix_q}"
           style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>
    {comments}"""
    return render(content, request, page="tasks", person=person)
