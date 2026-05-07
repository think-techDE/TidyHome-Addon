from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_persons
from models import Task
from render import INTERVALS, _base, _selected, interval_label, render, resolve_person, urgency_class
from storage import (create_task, delete_task, edit_task, filter_tasks_by_role,
                     get_admins, get_person_settings, get_task, list_tasks, mark_done)

router = APIRouter(prefix="/tasks")


@router.get("", response_class=HTMLResponse)
async def tasks_list(request: Request, room: str = None, person: str = None,
                     overdue: str = None, p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    tasks = list_tasks(room=room, assigned_to=person, overdue_only=(overdue == "1"))
    areas = await get_areas()

    # Räume ausblenden für aktive Person
    if p:
        hidden = set(get_person_settings(p).get("hidden_rooms", []))
        if hidden:
            tasks = [t for t in tasks if t.room not in hidden]

    # Rollenbasierte Sichtbarkeit
    tasks = filter_tasks_by_role(tasks, p, admins)

    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if not room and not overdue else ""}" href="tasks">Alle</a>'
    filters += f'<a class="filter-btn {"active" if overdue == "1" else ""}" href="tasks?overdue=1">Überfällig</a>'
    for r in areas:
        filters += f'<a class="filter-btn {"active" if room == r else ""}" href="tasks?room={r}">{r}</a>'
    filters += '</div>'

    # Grouped view für Elternteil/Admin im Raum-Filter
    cfg_p = get_person_settings(p) if p else {}
    role_p = cfg_p.get("role", "member")
    show_grouped = room and p and (p in admins or role_p == "parent")

    def _task_row(t):
        due = t.days_until_due()
        uc = urgency_class(due)
        if due < 0:    due_text = f"{abs(due)}d überfällig"
        elif due == 0: due_text = "Heute"
        elif due == 1: due_text = "Morgen"
        else:          due_text = f"In {due}d"
        assigned = (f"<span class='task-meta'>→ {', '.join(t.assigned_to)}</span>"
                    if t.assigned_to and not show_grouped else "")
        star = '<span title="Wichtig" style="font-size:1rem">⭐</span>' if t.important else ""
        onetime_badge = '<span class="badge" style="background:var(--muted);color:#fff;font-size:0.65rem">1×</span>' if t.onetime else ""
        border = "border-left:3px solid var(--warning);" if t.important else ""
        return f"""
        <div class="task-row" style="{border}">
          <div style="flex:1;min-width:0">
            <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
              {star}<span class="task-name">{t.name}</span>
              <span class="badge {uc}">{due_text}</span>{onetime_badge}
            </div>
            <div class="task-meta" style="margin-top:0.2rem">
              {t.room} · {interval_label(t.interval_days)} · {t.points} Pkt {assigned}
            </div>
          </div>
          <form class="inline" method="post" action="tasks/{t.id}/done">
            <button class="btn btn-success btn-sm" title="Erledigt">✓</button>
          </form>
          <a class="btn btn-ghost btn-sm" href="tasks/{t.id}/edit" title="Bearbeiten">✎</a>
          <a class="btn btn-danger btn-sm" href="tasks/{t.id}/delete"
             onclick="return confirm('Löschen?')" title="Löschen">✕</a>
        </div>"""

    rows = ""
    if not tasks:
        rows = '<div class="empty">Keine Aufgaben gefunden.</div>'
    elif show_grouped:
        from collections import defaultdict
        grouped = defaultdict(list)
        for t in tasks:
            if t.assigned_to:
                for pn in t.assigned_to:
                    grouped[pn].append(t)
            else:
                grouped["— Nicht zugeordnet —"].append(t)
        for person_name, ptasks in sorted(grouped.items()):
            rows += f'<div style="padding:0.6rem 1.25rem 0.2rem;font-size:0.75rem;font-weight:700;color:var(--primary-dark);text-transform:uppercase;letter-spacing:0.05em;background:var(--primary-light)">👤 {person_name}</div>'
            for t in ptasks:
                rows += _task_row(t)
    else:
        for t in tasks:
            rows += _task_row(t)

    content = f"""
    <div class="page-header">
      <h2>Aufgaben ({len(tasks)})</h2>
      <a class="btn btn-primary btn-sm" href="tasks/new">+ Neu</a>
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
                    important: str = Form(""), onetime: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    if not edit_task(task_id, name=name, room=room, interval_days=interval_days,
                     assigned_to=assigned_to, points=points,
                     important=(important == "1"), onetime=(onetime == "1")):
        raise HTTPException(404)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


@router.post("")
async def task_create(request: Request, name: str = Form(...), room: str = Form(...),
                      interval_days: int = Form(...), points: int = Form(10),
                      important: str = Form(""), onetime: str = Form("")):
    form = await request.form()
    assigned_to = list(form.getlist("assigned_to"))
    task = Task(name=name, room=room, interval_days=interval_days,
                assigned_to=assigned_to, points=points,
                important=(important == "1"), onetime=(onetime == "1"))
    create_task(task)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


@router.post("/{task_id}/done")
async def task_done(task_id: str, request: Request):
    form = await request.form()
    if not mark_done(task_id, done_by=form.get("done_by") or None):
        raise HTTPException(404)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


@router.get("/{task_id}/delete")
async def task_delete(task_id: str, request: Request):
    delete_task(task_id)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


async def _task_form(request: Request, title: str, action: str,
                     submit_label: str, task=None, person: str = "") -> HTMLResponse:
    areas = await get_areas()
    persons = await get_persons()
    cur_room = task.room if task else ""
    cur_interval = task.interval_days if task else 7
    cur_persons = task.assigned_to if task else ([person] if person else [])
    cur_points = task.points if task else 10
    cur_name = task.name if task else ""
    cur_important = task.important if task else False
    cur_onetime = task.onetime if task else False

    room_opts = "".join(
        f'<option value="{r}"{_selected(r, cur_room)}>{r}</option>' for r in areas)
    person_boxes = "".join(
        f'<label style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;'
        f'cursor:pointer;font-size:0.88rem">'
        f'<input type="checkbox" name="assigned_to" value="{pn}"'
        f'{" checked" if pn in cur_persons else ""}'
        f' style="width:1rem;height:1rem;accent-color:var(--primary)">{pn}</label>'
        for pn in persons
    )
    interval_opts = "".join(
        f'<option value="{d}"{_selected(d, cur_interval)}>{label}</option>'
        for d, label in INTERVALS.items())

    important_checked = "checked" if cur_important else ""
    onetime_checked = "checked" if cur_onetime else ""

    content = f"""
    <h2>{title}</h2>
    <div class="card">
      <form method="post" action="{action}">
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
            <label>Zugewiesen an</label>
            <div style="display:flex;flex-wrap:wrap;gap:0 1.5rem;padding:0.4rem 0">{person_boxes}</div>
          </div>
          <div class="form-group">
            <label>Punkte</label>
            <input name="points" type="number" value="{cur_points}" min="1" max="100">
          </div>
        </div>
        <div class="form-group">
          <label style="display:flex;align-items:center;gap:0.6rem;cursor:pointer;
                        text-transform:none;font-size:0.9rem;letter-spacing:0;font-weight:500">
            <input type="checkbox" name="important" value="1" {important_checked}
                   style="width:1.1rem;height:1.1rem;accent-color:var(--primary)">
            ⭐ Als wichtig markieren (wird oben in der Liste angezeigt)
          </label>
        </div>
        <div class="form-group">
          <label style="display:flex;align-items:center;gap:0.6rem;cursor:pointer;
                        text-transform:none;font-size:0.9rem;letter-spacing:0;font-weight:500">
            <input type="checkbox" name="onetime" value="1" {onetime_checked}
                   style="width:1.1rem;height:1.1rem;accent-color:var(--primary)">
            1× Einmalige Aufgabe (wird nach Erledigung automatisch archiviert)
          </label>
        </div>
        <button class="btn btn-primary btn-full" type="submit">{submit_label}</button>
        <a class="btn btn-ghost btn-full" href="tasks" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="tasks", person=person)
