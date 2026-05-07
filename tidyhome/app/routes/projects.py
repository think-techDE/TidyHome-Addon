from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_persons
from models import Project, Step
from render import _base, _selected, render
from storage import (add_step, complete_step, create_project, delete_project,
                     delete_step, get_project, list_projects, list_steps,
                     update_project)

router = APIRouter(prefix="/projects")


@router.get("", response_class=HTMLResponse)
async def projects_list(request: Request, room: str = None, show: str = "active", p: str = ""):
    areas = await get_areas()
    all_projects = list_projects(room=room)

    active_projects = [pr for pr in all_projects if not pr.completed]
    done_projects   = [pr for pr in all_projects if pr.completed]
    projects = done_projects if show == "done" else active_projects

    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if show == "active" and not room else ""}" href="projects">Offen</a>'
    filters += f'<a class="filter-btn {"active" if show == "done" else ""}" href="projects?show=done">✅ Abgeschlossen ({len(done_projects)})</a>'
    for r in areas:
        active_cls = "active" if room == r and show != "done" else ""
        filters += f'<a class="filter-btn {active_cls}" href="projects?room={r}">{r}</a>'
    filters += '</div>'

    rows = ""
    if not projects:
        hint = "Noch keine abgeschlossenen Projekte." if show == "done" else "Noch keine Ordnungsprojekte."
        rows = f'<div class="empty">{hint}</div>'
    else:
        for proj in projects:
            steps = list_steps(proj.id)
            done, total = proj.progress(steps)
            pct = int(done / total * 100) if total else 0
            assigned = f"<span class='task-meta'>→ {proj.assigned_to}</span>" if proj.assigned_to else ""
            completed_badge = '<span class="badge ok">✓ Fertig</span>' if proj.completed else ""
            opacity = "opacity:0.7;" if proj.completed else ""
            fill_class = "green" if proj.completed else ""
            rows += f"""
            <div class="task-row" style="{opacity}">
              <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
                  <a href="projects/{proj.id}" class="task-name"
                     style="text-decoration:none;color:inherit">{proj.name}</a>
                  {completed_badge}{assigned}
                </div>
                <div class="task-meta" style="margin-top:0.2rem">{proj.room} · {done}/{total} Schritte</div>
                <div class="progress-track" style="margin-top:0.4rem">
                  <div class="progress-fill {fill_class}" style="width:{pct}%"></div>
                </div>
              </div>
              {'<a class="btn btn-danger btn-sm" href="projects/' + proj.id + '/archive" title="Archivieren">📁</a>' if proj.completed else '<a class="btn btn-ghost btn-sm" href="projects/' + proj.id + '/edit">✎</a>'}
              <a class="btn btn-danger btn-sm" href="projects/{proj.id}/delete"
                 onclick="return confirm('Projekt löschen?')">✕</a>
            </div>"""

    content = f"""
    <div class="page-header">
      <h2>Ordnungsprojekte ({len(active_projects)} offen)</h2>
      <a class="btn btn-primary btn-sm" href="projects/new">+ Neu</a>
    </div>
    {filters}
    <div class="card card-flush">{rows}</div>"""
    return render(content, request, page="projects", person=p)


@router.get("/new", response_class=HTMLResponse)
async def project_new_form(request: Request, p: str = ""):
    areas = await get_areas()
    persons = await get_persons()
    room_opts = "".join(f'<option value="{r}">{r}</option>' for r in areas)
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
        <button class="btn btn-primary btn-full" type="submit">Projekt anlegen</button>
        <a class="btn btn-ghost btn-full" href="projects" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.post("")
async def project_create(request: Request, name: str = Form(...), room: str = Form(...),
                          assigned_to: str = Form(""), description: str = Form("")):
    proj = Project(name=name, room=room, assigned_to=assigned_to or None,
                   description=description or None)
    create_project(proj)
    return RedirectResponse(_base(request) + f"projects/{proj.id}", status_code=303)


@router.get("/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str, request: Request, p: str = ""):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    steps = list_steps(project_id)
    done, total = proj.progress(steps)
    pct = int(done / total * 100) if total else 0
    persons = await get_persons()
    person_opts = '<option value="">— Niemand —</option>' + "".join(
        f'<option value="{pn}">{pn}</option>' for pn in persons)

    step_rows = ""
    for s in steps:
        if s.completed:
            who = f" · {s.completed_by}" if s.completed_by else ""
            step_rows += f"""
            <div class="task-row" style="opacity:0.5">
              <span style="color:var(--success);font-size:1.1rem">✓</span>
              <span class="task-name" style="text-decoration:line-through">{s.name}</span>
              <span class="task-meta">{s.points} Pkt{who}</span>
            </div>"""
        else:
            step_rows += f"""
            <div class="task-row">
              <span class="task-name" style="flex:1">{s.name}</span>
              <span class="task-meta" style="margin-right:0.5rem">{s.points} Pkt</span>
              <form class="inline" method="post" action="steps/{s.id}/done">
                <select name="done_by" style="width:auto;padding:0.2rem 0.4rem;
                  font-size:0.78rem;margin-right:0.3rem;border-radius:0.4rem">
                  {person_opts}
                </select>
                <button class="btn btn-success btn-sm">✓</button>
              </form>
              <a class="btn btn-danger btn-sm" style="margin-left:0.3rem"
                 href="steps/{s.id}/delete" onclick="return confirm('Schritt löschen?')">✕</a>
            </div>"""

    if not steps:
        step_rows = '<div class="empty">Noch keine Schritte. Füge unten den ersten hinzu.</div>'

    assigned = f" · → {proj.assigned_to}" if proj.assigned_to else ""
    desc = (f'<p class="muted" style="margin-bottom:1rem">{proj.description}</p>'
            if proj.description else "")

    content = f"""
    <div class="page-header">
      <div>
        <h2>{proj.name}</h2>
        <div class="muted">{proj.room}{assigned}</div>
      </div>
      <a class="btn btn-ghost btn-sm" href="edit">✎ Bearbeiten</a>
    </div>
    {desc}
    <div class="card" style="padding:1rem;margin-bottom:1rem">
      <div style="display:flex;justify-content:space-between;font-size:0.78rem;
                  color:var(--muted);margin-bottom:0.4rem">
        <span>{done} von {total} Schritten</span><span>{pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill {'green' if pct == 100 else ''}" style="width:{pct}%"></div>
      </div>
    </div>
    <div class="card card-flush" style="margin-bottom:1rem">{step_rows}</div>
    <div class="card">
      <h3 style="margin-bottom:0.75rem">Schritt hinzufügen</h3>
      <form method="post" action="steps">
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
        <button class="btn btn-primary btn-sm" type="submit">Hinzufügen</button>
        <a class="btn btn-ghost btn-sm" href="projects" style="margin-left:0.5rem">← Alle Projekte</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.get("/{project_id}/edit", response_class=HTMLResponse)
async def project_edit_form(project_id: str, request: Request, p: str = ""):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    areas = await get_areas()
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
      <form method="post" action="edit">
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
        <button class="btn btn-primary btn-full" type="submit">Speichern</button>
        <a class="btn btn-ghost btn-full" href="../{project_id}" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.post("/{project_id}/edit")
async def project_edit(project_id: str, request: Request, name: str = Form(...),
                        room: str = Form(...), assigned_to: str = Form(""),
                        description: str = Form("")):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    proj.name = name
    proj.room = room
    proj.assigned_to = assigned_to or None
    proj.description = description or None
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
        delete_project(project_id)  # sets active=False
    return RedirectResponse(_base(request) + "projects", status_code=303)


@router.post("/{project_id}/steps")
async def step_add(project_id: str, request: Request,
                   name: str = Form(...), points: int = Form(5)):
    if not get_project(project_id):
        raise HTTPException(404)
    add_step(Step(project_id=project_id, name=name, points=points))
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@router.post("/{project_id}/steps/{step_id}/done")
async def step_done(project_id: str, step_id: str, request: Request):
    form = await request.form()
    complete_step(step_id, done_by=form.get("done_by") or None)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@router.get("/{project_id}/steps/{step_id}/delete")
async def step_delete(project_id: str, step_id: str, request: Request):
    delete_step(step_id)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)
