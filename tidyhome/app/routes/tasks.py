from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_persons
from models import Task
from render import (INTERVALS, _base, _icon, _icon_chooser, _selected, _task_icon,
                    interval_label, person_suffix, render, resolve_person, urgency_class)
from storage import (create_task, delete_task, edit_task, filter_tasks_by_role,
                     get_admins, get_person_settings, get_task, list_people_by_role,
                     list_tasks, mark_done)

router = APIRouter(prefix="/tasks")


@router.get("", response_class=HTMLResponse)
async def tasks_list(request: Request, room: str = None, person: str = None,
                     overdue: str = None, mine: str = None, p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    tasks = list_tasks(room=room, assigned_to=person,
                       overdue_only=(overdue == "1"))

    # "Meine" filter
    if mine == "1" and p:
        tasks = [t for t in tasks if p in t.assigned_to]

    # Hidden rooms
    if p:
        hidden = set(get_person_settings(p).get("hidden_rooms", []))
        if hidden:
            tasks = [t for t in tasks if t.room not in hidden]

    areas = await get_areas()
    psuffix = f"&p={p}" if p else ""

    # Filter bar
    all_active = not room and not overdue and not mine
    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if all_active else ""}" href="tasks{("?p="+p) if p else ""}">Alle</a>'
    if p:
        filters += f'<a class="filter-btn {"active" if mine == "1" else ""}" href="tasks?mine=1{psuffix}">Meine</a>'
    filters += f'<a class="filter-btn {"active" if overdue == "1" else ""}" href="tasks?overdue=1{psuffix}">Überfällig</a>'
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

    cal = _icon("calendar", 13, "var(--muted)")

    def _task_row(t: Task) -> str:
        due = t.days_until_due()

        # Badge: Status-Label (was) – Datum: konkretes Timing (wann)
        if due < 0:
            badge_text, badge_cls = "Überfällig", "overdue"
            date_text = f"{abs(due)}d überfällig"
        elif due == 0:
            badge_text, badge_cls = "Heute", "today"
            date_text = "Heute"
        else:
            badge_text, badge_cls = "Geplant", "ok"
            date_text = "Morgen" if due == 1 else f"In {due} Tagen"

        important_cls = " important" if t.important else ""
        star = (
            f'{_icon("star", 13, "var(--warning)", 2.5)}'
        ) if t.important else ""
        onetime_badge = (
            '<span class="badge" style="background:var(--muted);color:#fff;'
            'font-size:0.62rem;flex-shrink:0">1×</span>'
        ) if t.onetime else ""

        assigned_txt = ""
        if t.assigned_to and not show_grouped:
            assigned_txt = (
                f'<span class="task-meta" style="font-size:0.72rem">'
                f'→ {", ".join(t.assigned_to)}</span>'
            )

        done_btn = (
            f'<form class="inline" method="post" action="tasks/{t.id}/done">'
            + (f'<input type="hidden" name="done_by" value="{p}">' if p else "")
            + (f'<input type="hidden" name="return_p" value="{p}">' if p else "")
            + f'<button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>'
            f'</form>'
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
          {_task_icon(t.name, t.room, icon=t.icon)}
          <div class="task-body">
            <div class="task-header">
              <span class="task-name">{star}{t.name}</span>
              <div style="display:flex;align-items:center;gap:0.3rem;flex-shrink:0">
                {onetime_badge}
                <span class="badge {badge_cls}">{badge_text}</span>
              </div>
            </div>
            <div class="task-date">{cal}
              <span class="task-meta">{date_text}</span>
              {assigned_txt}
            </div>
            <div class="task-actions">
              {done_btn}
              <div style="display:flex">{edit_btn}{del_btn}</div>
            </div>
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
    content = f"""
    <div class="page-header">
      <h2>Aufgaben <span class="muted" style="font-weight:400">({len(tasks)})</span></h2>
      <a class="btn btn-primary btn-sm" href="tasks/new{psuffix_q}"
         style="display:flex;align-items:center;gap:0.3rem">
        {_icon("plus", 14, "white")} Neu
      </a>
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
                    icon: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    if not edit_task(task_id, name=name, room=room, interval_days=interval_days,
                     assigned_to=assigned_to, points=points,
                     important=(important == "1"), onetime=(onetime == "1"),
                     icon=icon):
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    return RedirectResponse(_base(request) + f"tasks{person_suffix(return_p)}", status_code=303)


@router.post("")
async def task_create(request: Request, name: str = Form(...), room: str = Form(...),
                      interval_days: int = Form(...), points: int = Form(10),
                      important: str = Form(""), onetime: str = Form(""),
                      icon: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    task = Task(name=name, room=room, interval_days=interval_days,
                assigned_to=assigned_to, points=points,
                important=(important == "1"), onetime=(onetime == "1"),
                icon=icon)
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


@router.get("/{task_id}/delete")
async def task_delete(task_id: str, request: Request, p: str = ""):
    delete_task(task_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"tasks{person_suffix(p)}", status_code=303)


async def _task_form(request: Request, title: str, action: str,
                     submit_label: str, task=None, person: str = "") -> HTMLResponse:
    areas   = await get_areas()
    persons = await get_persons()
    cur_room      = task.room if task else ""
    cur_interval  = task.interval_days if task else 7
    cur_persons   = task.assigned_to if task else ([person] if person else [])
    cur_points    = task.points if task else 10
    cur_name      = task.name if task else ""
    cur_important = task.important if task else False
    cur_onetime   = task.onetime if task else False
    cur_icon      = task.icon if task else ""

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

    important_checked = "checked" if cur_important else ""
    onetime_checked   = "checked" if cur_onetime   else ""
    from render import _icon as _i
    star_svg = _i("star", 15, "var(--warning)")

    psuffix_q = f"?p={person}" if person else ""
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
        <button class="btn btn-primary btn-full" type="submit">{submit_label}</button>
        <a class="btn btn-ghost btn-full" href="tasks{psuffix_q}"
           style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="tasks", person=person)
