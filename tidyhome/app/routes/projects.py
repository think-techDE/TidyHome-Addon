from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_persons
from models import Project, Step
from render import _base, _icon, _icon_chooser, _proj_icon, _selected, render, resolve_person
from storage import (add_step, assign_step, complete_step, create_project,
                     delete_project, delete_step, get_admins, get_person_settings,
                     get_project, list_projects, list_steps, update_project)

router = APIRouter(prefix="/projects")


def _step_assignee(step: Step, project: Project) -> str:
    return step.assigned_to or project.assigned_to or ""


def _can_see_project(project: Project, steps: list[Step], person: str, admins: list[str]) -> bool:
    if not person:
        return True
    return project.assigned_to == person or any(_step_assignee(s, project) == person for s in steps)


def _visible_steps(project: Project, steps: list[Step], person: str, admins: list[str]) -> list[Step]:
    if not person:
        return steps
    return [s for s in steps if _step_assignee(s, project) == person]


def _steps_for_person(project: Project, steps: list[Step], person: str) -> list[Step]:
    return [s for s in steps if _step_assignee(s, project) == person]


def _project_people(project: Project, steps: list[Step]) -> list[str]:
    people = {project.assigned_to} if project.assigned_to else set()
    people.update(_step_assignee(s, project) for s in steps if _step_assignee(s, project))
    return sorted(people) or ["— Nicht zugeordnet —"]


@router.get("", response_class=HTMLResponse)
async def projects_list(request: Request, room: str = None, show: str = "active",
                        scope: str = "mine", p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    areas = await get_areas()
    all_projects = list_projects(room=room)

    grouped_by_person = p in admins and scope == "people"

    if p:
        hidden = set(get_person_settings(p).get("hidden_rooms", []))
        if hidden:
            all_projects = [pr for pr in all_projects if pr.room not in hidden]
        if not grouped_by_person:
            all_projects = [
                pr for pr in all_projects
                if _can_see_project(pr, list_steps(pr.id), p, admins)
            ]

    active_projects = [pr for pr in all_projects if not pr.completed]
    done_projects   = [pr for pr in all_projects if pr.completed]
    projects = done_projects if show == "done" else active_projects

    psuffix = f"&p={p}" if p else ""
    scope_suffix = "&scope=people" if grouped_by_person else ""

    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if show == "active" and not room and not grouped_by_person else ""}" href="projects{("?p="+p) if p else ""}">Meine</a>'
    if p in admins:
        filters += f'<a class="filter-btn {"active" if grouped_by_person else ""}" href="projects?scope=people{psuffix}">Nach Personen</a>'
    filters += f'<a class="filter-btn {"active" if show == "done" else ""}" href="projects?show=done{scope_suffix}{psuffix}">Abgeschlossen ({len(done_projects)})</a>'
    for r in areas:
        active_cls = "active" if room == r and show != "done" else ""
        filters += f'<a class="filter-btn {active_cls}" href="projects?room={r}{scope_suffix}{psuffix}">{r}</a>'
    filters += '</div>'

    rows = ""
    if not projects:
        hint = "Noch keine abgeschlossenen Projekte." if show == "done" else "Noch keine Ordnungsprojekte."
        rows = (
            f'<div class="empty">'
            f'<div class="empty-icon">📦</div>'
            f'<div style="font-weight:600">{hint}</div>'
            f'<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            f'Leg ein neues Projekt an, um loszulegen.</div>'
            f'</div>'
        )
    else:
        def project_row(proj: Project, visible: list[Step], person_name: str = "") -> str:
            steps = list_steps(proj.id)
            done, total = proj.progress(visible)
            pct = int(done / total * 100) if total else 0
            assigned = f"<span class='task-meta'>→ {proj.assigned_to}</span>" if proj.assigned_to else ""
            fill_class = "green" if proj.completed else ""
            opacity = "opacity:0.65;" if proj.completed else ""

            if proj.completed:
                action_btns = (
                    f'<a class="icon-btn" href="projects/{proj.id}/archive" '
                    f'title="Archivieren">{_icon("archive", 16)}</a>'
                )
            else:
                action_btns = (
                    f'<a class="icon-btn" href="projects/{proj.id}/edit" '
                    f'title="Bearbeiten">{_icon("edit", 16)}</a>'
                )
            del_btn = (
                f'<a class="icon-btn danger" href="projects/{proj.id}/delete" '
                f'onclick="return confirm(\'Projekt löschen?\')" title="Löschen">'
                f'{_icon("trash", 16)}</a>'
            )

            person_suffix = f" · {person_name}" if person_name else ""
            return f"""
            <div class="proj-row" style="{opacity}">
              <a href="projects/{proj.id}{'?scope=people' if grouped_by_person else ''}" style="display:contents;text-decoration:none">
                {_proj_icon(proj.room, icon=proj.icon)}
              </a>
              <div style="flex:1;min-width:0">
                <a href="projects/{proj.id}{'?scope=people' if grouped_by_person else ''}"
                   style="text-decoration:none;color:inherit;font-weight:600;
                          font-size:0.9rem;display:block;margin-bottom:0.15rem">
                  {proj.name}
                </a>
                <div class="task-meta">{proj.room}{person_suffix} · {done}/{total} sichtbare Schritte {assigned}</div>
                <div class="progress-track" style="margin-top:0.4rem">
                  <div class="progress-fill {fill_class}" style="width:{pct}%"></div>
                </div>
              </div>
              <div class="task-actions">{action_btns}{del_btn}</div>
            </div>"""

        if grouped_by_person:
            from collections import defaultdict
            grouped: dict[str, list[str]] = defaultdict(list)
            for proj in projects:
                steps = list_steps(proj.id)
                for person_name in _project_people(proj, steps):
                    visible = _steps_for_person(proj, steps, person_name)
                    if not visible and proj.assigned_to == person_name:
                        visible = steps
                    grouped[person_name].append(project_row(proj, visible, person_name))
            for person_name, person_rows in sorted(grouped.items()):
                rows += (
                    f'<div style="padding:0.5rem 1.25rem;font-size:0.72rem;font-weight:700;'
                    f'color:var(--primary-dark);text-transform:uppercase;letter-spacing:0.06em;'
                    f'background:var(--primary-light);display:flex;align-items:center;gap:0.4rem">'
                    f'{_icon("person", 13, "var(--primary-dark)")} {person_name}</div>'
                    + "".join(person_rows)
                )
        else:
            for proj in projects:
                steps = list_steps(proj.id)
                rows += project_row(proj, _visible_steps(proj, steps, p, admins))

    psuffix_q = f"?p={p}" if p else ""
    content = f"""
    <div class="page-header">
      <h2>Projekte <span class="muted" style="font-weight:400">({len(active_projects)} offen)</span></h2>
      <a class="btn btn-primary btn-sm" href="projects/new{psuffix_q}"
         style="display:flex;align-items:center;gap:0.3rem">
        {_icon("plus", 14, "white")} Neu
      </a>
    </div>
    {filters}
    <div class="card card-flush">{rows}</div>"""
    return render(content, request, page="projects", person=p)


@router.get("/new", response_class=HTMLResponse)
async def project_new_form(request: Request, p: str = ""):
    p = resolve_person(request, p)
    areas   = await get_areas()
    persons = await get_persons()
    room_opts   = "".join(f'<option value="{r}">{r}</option>' for r in areas)
    person_opts = '<option value="">— Niemand —</option>' + "".join(
        f'<option value="{pn}">{pn}</option>' for pn in persons)
    content = f"""
    <h2>Neues Ordnungsprojekt</h2>
    <div class="card">
      <form method="post" action="projects">
        <div class="form-group">
          <label>Projektname</label>
          <input name="name" required placeholder="z.B. Keller aufräumen">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>Raum</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>Zugewiesen an</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
        </div>
        <div class="form-group">
          <label>Beschreibung (optional)</label>
          <input name="description" placeholder="Was soll erreicht werden?">
        </div>
        {_icon_chooser("", "icon")}
        <button class="btn btn-primary btn-full" type="submit">Projekt anlegen</button>
        <a class="btn btn-ghost btn-full" href="projects" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.post("")
async def project_create(request: Request, name: str = Form(...), room: str = Form(...),
                          assigned_to: str = Form(""), description: str = Form(""),
                          icon: str = Form("")):
    proj = Project(name=name, room=room, assigned_to=assigned_to or None,
                   description=description or None, icon=icon)
    create_project(proj)
    return RedirectResponse(_base(request) + f"projects/{proj.id}", status_code=303)


@router.get("/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str, request: Request, scope: str = "mine", p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    base = _base(request)
    all_steps = list_steps(project_id)
    grouped_by_person = p in admins and scope == "people"
    if not grouped_by_person and not _can_see_project(proj, all_steps, p, admins):
        raise HTTPException(404)
    steps = all_steps if grouped_by_person else _visible_steps(proj, all_steps, p, admins)
    done, total = proj.progress(steps)
    pct = int(done / total * 100) if total else 0
    persons = await get_persons()
    default_done_by = proj.assigned_to or p or ""
    person_names = list(persons)
    if default_done_by and default_done_by not in person_names:
        person_names.insert(0, default_done_by)
    person_opts = f'<option value=""{_selected("", default_done_by)}>— Niemand —</option>' + "".join(
        f'<option value="{pn}"{_selected(pn, default_done_by)}>{pn}</option>'
        for pn in person_names)

    fill_cls = "green" if pct == 100 else ""
    step_rows = ""
    for s in steps:
        assignee = _step_assignee(s, proj)
        step_person_names = list(person_names)
        if assignee and assignee not in step_person_names:
            step_person_names.insert(0, assignee)
        step_person_opts = f'<option value=""{_selected("", assignee)}>— Niemand —</option>' + "".join(
            f'<option value="{pn}"{_selected(pn, assignee)}>{pn}</option>'
            for pn in step_person_names)
        if s.completed:
            who = f" · {s.completed_by}" if s.completed_by else ""
            step_rows += f"""
            <div class="project-step-row is-done">
              <span style="color:var(--success);font-size:1.1rem;flex-shrink:0">
                {_icon("check", 18, "var(--success)")}
              </span>
              <div class="project-step-main">
                <span class="project-step-title">{s.name}</span>
                <span class="project-step-meta">{s.points} Pkt · → {assignee or "Niemand"}{who}</span>
              </div>
            </div>"""
        else:
            step_rows += f"""
            <div class="project-step-row">
              <div class="project-step-main">
                <span class="project-step-title">{s.name}</span>
                <span class="project-step-meta">{s.points} Pkt</span>
              </div>
              <div class="project-step-actions">
                <form class="project-step-form" method="post" action="{base}projects/{project_id}/steps/{s.id}/assign">
                  <select class="project-step-person" name="assigned_to" aria-label="Zugewiesen an"
                          onchange="this.form.submit()">
                  {step_person_opts}
                  </select>
                </form>
                <form class="inline" method="post" action="{base}projects/{project_id}/steps/{s.id}/done">
                  <input type="hidden" name="done_by" value="{assignee}">
                  <button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>
                </form>
                <a class="icon-btn danger"
                   href="{base}projects/{project_id}/steps/{s.id}/delete"
                   onclick="return confirm('Schritt löschen?')"
                   title="Schritt löschen">
                   {_icon("trash", 15)}
                </a>
              </div>
            </div>"""

    if not steps:
        step_rows = (
            '<div class="empty">'
            '<div class="empty-icon">📝</div>'
            '<div>Noch keine Schritte. Füge unten den ersten hinzu.</div>'
            '</div>'
        )

    assigned = f" · → {proj.assigned_to}" if proj.assigned_to else ""
    desc = (f'<p class="muted" style="margin-bottom:1rem">{proj.description}</p>'
            if proj.description else "")

    content = f"""
    <div class="page-header">
      <div>
        <h2>{proj.name}</h2>
        <div class="muted">{proj.room}{assigned}</div>
      </div>
      <a class="btn btn-ghost btn-sm" href="{base}projects/{project_id}/edit"
         style="display:flex;align-items:center;gap:0.3rem">
        {_icon("edit", 14, "var(--primary-dark)")} Bearbeiten
      </a>
    </div>
    {desc}
    <div class="card project-progress-card">
      <div class="project-progress-head">
        <span>{done} von {total} Schritten</span><span>{pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill {fill_cls}" style="width:{pct}%"></div>
      </div>
    </div>
    <div class="card card-flush" style="margin-bottom:1rem">{step_rows}</div>
    <div class="card">
      <h3 style="margin-bottom:0.75rem">Schritt hinzufügen</h3>
      <form method="post" action="{base}projects/{project_id}/steps">
        <div class="grid-2">
          <div class="form-group">
            <label>Beschreibung</label>
            <input name="name" required placeholder="z.B. Kartons sortieren">
          </div>
          <div class="form-group">
            <label>Punkte</label>
            <input name="points" type="number" value="5" min="1" max="100">
          </div>
        </div>
        <div class="form-group">
          <label>Zugewiesen an</label>
          <select name="assigned_to">{person_opts}</select>
        </div>
        <div class="project-step-add-actions">
          <button class="btn btn-primary btn-sm" type="submit">
            {_icon("plus", 14, "white")} Hinzufügen
          </button>
          <a class="btn btn-ghost btn-sm" href="{base}projects">← Alle Projekte</a>
        </div>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.get("/{project_id}/edit", response_class=HTMLResponse)
async def project_edit_form(project_id: str, request: Request, p: str = ""):
    p = resolve_person(request, p)
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    base = _base(request)
    areas   = await get_areas()
    persons = await get_persons()
    room_opts = "".join(
        f'<option value="{r}"{_selected(r, proj.room)}>{r}</option>' for r in areas)
    person_opts = (
        f'<option value=""{_selected("", proj.assigned_to or "")}>— Niemand —</option>'
        + "".join(f'<option value="{pn}"{_selected(pn, proj.assigned_to or "")}>{pn}</option>'
                  for pn in persons))
    content = f"""
    <h2>Projekt bearbeiten</h2>
    <div class="card">
      <form method="post" action="{base}projects/{project_id}/edit">
        <div class="form-group">
          <label>Name</label>
          <input name="name" required value="{proj.name}">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>Raum</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>Zugewiesen an</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
        </div>
        <div class="form-group">
          <label>Beschreibung</label>
          <input name="description" value="{proj.description or ''}">
        </div>
        {_icon_chooser(proj.icon, "icon")}
        <button class="btn btn-primary btn-full" type="submit">Speichern</button>
        <a class="btn btn-ghost btn-full" href="{base}projects/{project_id}"
           style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.post("/{project_id}/edit")
async def project_edit(project_id: str, request: Request, name: str = Form(...),
                        room: str = Form(...), assigned_to: str = Form(""),
                        description: str = Form(""), icon: str = Form("")):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    proj.name = name
    proj.room = room
    proj.assigned_to = assigned_to or None
    proj.description = description or None
    proj.icon = icon
    update_project(proj)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@router.get("/{project_id}/delete")
async def project_delete(project_id: str, request: Request):
    delete_project(project_id)
    return RedirectResponse(_base(request) + "projects", status_code=303)


@router.get("/{project_id}/archive")
async def project_archive(project_id: str, request: Request):
    proj = get_project(project_id)
    if proj:
        delete_project(project_id)
    return RedirectResponse(_base(request) + "projects", status_code=303)


@router.post("/{project_id}/steps")
async def step_add(project_id: str, request: Request,
                   name: str = Form(...), points: int = Form(5),
                   assigned_to: str = Form("")):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    assignee = assigned_to or proj.assigned_to
    add_step(Step(project_id=project_id, name=name, points=points,
                  assigned_to=assignee or None))
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@router.post("/{project_id}/steps/{step_id}/assign")
async def step_assign(project_id: str, step_id: str, request: Request,
                      assigned_to: str = Form("")):
    if not assign_step(step_id, assigned_to=assigned_to or None):
        raise HTTPException(404)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@router.post("/{project_id}/steps/{step_id}/done")
async def step_done(project_id: str, step_id: str, request: Request):
    form = await request.form()
    step = complete_step(step_id, done_by=form.get("done_by") or None)
    if not step:
        raise HTTPException(404)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@router.get("/{project_id}/steps/{step_id}/delete")
async def step_delete(project_id: str, step_id: str, request: Request):
    delete_step(step_id)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)
