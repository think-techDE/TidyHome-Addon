from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from access import (can_group_projects_by_person, can_view_project,
                    filter_hidden_rooms, project_people, project_step_assignee,
                    project_steps_for_person, visible_project_steps,
                    visible_projects_for_person)
from ha_client import get_areas, get_persons
from i18n import tr
from models import Project, Step
from reminders import send_project_step_reminder
from render import (_base, _icon, _icon_chooser, _selected,
                    comments_card, photos_card, project_row, project_step_reminder_form,
                    project_step_row, render, resolve_person)
from storage import (add_comment, add_photo, add_step, assign_step, complete_step, create_project,
                     delete_photo, delete_project, delete_step, get_admins, get_step,
                     get_project, list_projects, list_steps, update_project)
from uploads import selected_photo_upload

router = APIRouter(prefix="/projects")


def _p_suffix(person: str = "", separator: str = "?") -> str:
    return f"{separator}p={quote(person)}" if person else ""


@router.get("", response_class=HTMLResponse)
async def projects_list(request: Request, room: str = None, show: str = "active",
                        scope: str = "mine", p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    areas = await get_areas()
    all_projects = list_projects(room=room)

    grouped_by_person = can_group_projects_by_person(p, admins) and scope == "people"

    if p:
        all_projects = filter_hidden_rooms(all_projects, p)
        if not grouped_by_person:
            all_projects = visible_projects_for_person(
                all_projects, p, list_steps, admins
            )

    active_projects = [pr for pr in all_projects if not pr.completed]
    done_projects   = [pr for pr in all_projects if pr.completed]
    projects = done_projects if show == "done" else active_projects

    psuffix = f"&p={p}" if p else ""
    scope_suffix = "&scope=people" if grouped_by_person else ""

    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if show == "active" and not room and not grouped_by_person else ""}" href="projects{("?p="+p) if p else ""}">{tr("menu.my_view")}</a>'
    if can_group_projects_by_person(p, admins):
        filters += f'<a class="filter-btn {"active" if grouped_by_person else ""}" href="projects?scope=people{psuffix}">Nach Personen</a>'
    filters += f'<a class="filter-btn {"active" if show == "done" else ""}" href="projects?show=done{scope_suffix}{psuffix}">{tr("status.done")} ({len(done_projects)})</a>'
    for r in areas:
        active_cls = "active" if room == r and show != "done" else ""
        filters += f'<a class="filter-btn {active_cls}" href="projects?room={r}{scope_suffix}{psuffix}">{r}</a>'
    filters += '</div>'

    rows = ""
    if not projects:
        hint = tr("project.archived_empty") if show == "done" else tr("project.empty")
        rows = (
            f'<div class="empty">'
            f'<div class="empty-icon">📦</div>'
            f'<div style="font-weight:600">{hint}</div>'
            f'<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            f'{tr("project.create")}.</div>'
            f'</div>'
        )
    else:
        if grouped_by_person:
            from collections import defaultdict
            grouped: dict[str, list[str]] = defaultdict(list)
            for proj in projects:
                steps = list_steps(proj.id)
                for person_name in project_people(proj, steps):
                    visible = project_steps_for_person(proj, steps, person_name)
                    if not visible and proj.assigned_to == person_name:
                        visible = steps
                    grouped[person_name].append(
                        project_row(
                            proj, visible, steps, person=p,
                            grouped_by_person=grouped_by_person,
                            person_name=person_name,
                        )
                    )
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
                rows += project_row(
                    proj, visible_project_steps(proj, steps, p, admins), steps,
                    person=p, grouped_by_person=grouped_by_person
                )

    psuffix_q = f"?p={p}" if p else ""
    visible_step_count = 0
    done_step_count = 0
    for pr in active_projects:
        pr_steps = list_steps(pr.id)
        visible = (
            pr_steps if grouped_by_person
            else visible_project_steps(pr, pr_steps, p, admins)
        )
        d, total = pr.progress(visible)
        visible_step_count += total
        done_step_count += d
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">{tr("project.progress_plan")}</div>
        <div class="hero-title">{tr("project.projects")}</div>
      </div>
      <div class="page-hero-actions">
        <a class="btn btn-primary btn-sm" href="projects/new{psuffix_q}">
          {_icon("plus", 14, "white")} {tr("common.new")}
        </a>
      </div>
    </div>
    <div class="today-grid" style="margin-bottom:1rem">
      <div class="today-stat">
        <div class="today-value">{len(active_projects)}</div>
        <div class="today-label">{tr("project.open")}</div>
      </div>
      <div class="today-stat">
        <div class="today-value">{done_step_count}/{visible_step_count}</div>
        <div class="today-label">{tr("project.steps")}</div>
      </div>
      <div class="today-stat">
        <div class="today-value">{len(done_projects)}</div>
        <div class="today-label">{tr("project.done")}</div>
      </div>
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
    person_opts = f'<option value="">— {tr("common.none")} —</option>' + "".join(
        f'<option value="{pn}">{pn}</option>' for pn in persons)
    content = f"""
    <div class="page-header">
      <h2>{tr("project.new")}</h2>
      <a class="icon-btn" href="projects{_p_suffix(p)}" title="{tr("common.cancel")}">{_icon("chevron_l", 20)}</a>
    </div>
    <div class="card">
      <form method="post" action="projects">
        <input type="hidden" name="return_p" value="{p}">
        <div class="form-group">
          <label>{tr("project.name")}</label>
          <input name="name" required placeholder="{tr("form.project_name_placeholder")}">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>{tr("form.room")}</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>{tr("form.assigned_to")}</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
        </div>
        <div class="form-group">
          <label>{tr("form.description_optional")}</label>
          <input name="description" placeholder="{tr("form.project_description_placeholder")}">
        </div>
        {_icon_chooser("", "icon", include_room_icons=True)}
        <button class="btn btn-primary btn-full" type="submit">{tr("project.create")}</button>
        <a class="btn btn-ghost btn-full" href="projects{_p_suffix(p)}" style="margin-top:0.5rem">{tr("common.cancel")}</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.post("")
async def project_create(request: Request, name: str = Form(...), room: str = Form(...),
                          assigned_to: str = Form(""), description: str = Form(""),
                          icon: str = Form(""), return_p: str = Form("")):
    proj = Project(name=name, room=room, assigned_to=assigned_to or None,
                   description=description or None, icon=icon)
    create_project(proj)
    return RedirectResponse(_base(request) + f"projects/{proj.id}{_p_suffix(return_p)}", status_code=303)


@router.get("/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str, request: Request, scope: str = "mine", p: str = ""):
    p = resolve_person(request, p)
    admins = get_admins()
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    base = _base(request)
    all_steps = list_steps(project_id)
    grouped_by_person = can_group_projects_by_person(p, admins) and scope == "people"
    if not grouped_by_person and not can_view_project(proj, all_steps, p, admins):
        raise HTTPException(404)
    steps = (
        all_steps if grouped_by_person
        else visible_project_steps(proj, all_steps, p, admins)
    )
    done, total = proj.progress(steps)
    pct = int(done / total * 100) if total else 0
    persons = await get_persons()
    default_done_by = proj.assigned_to or p or ""
    person_names = list(persons)
    if default_done_by and default_done_by not in person_names:
        person_names.insert(0, default_done_by)
    person_opts = f'<option value=""{_selected("", default_done_by)}>— {tr("common.none")} —</option>' + "".join(
        f'<option value="{pn}"{_selected(pn, default_done_by)}>{pn}</option>'
        for pn in person_names)

    fill_cls = "green" if pct == 100 else ""
    step_rows = ""
    for s in steps:
        assignee = project_step_assignee(s, proj)
        step_person_names = list(person_names)
        if assignee and assignee not in step_person_names:
            step_person_names.insert(0, assignee)
        step_person_opts = f'<option value=""{_selected("", assignee)}>— {tr("common.none")} —</option>' + "".join(
            f'<option value="{pn}"{_selected(pn, assignee)}>{pn}</option>'
            for pn in step_person_names)
        step_rows += (
            '<div class="card card-flush" style="margin-bottom:0.75rem">'
            + project_step_row(proj, s, assignee, step_person_opts, base, p)
            + '</div>'
        )
        step_rows += photos_card("step", s.id, f"{base}projects/{project_id}/steps/{s.id}/photos",
                                  p, title=f"{tr('photos.photos')}: {s.name}")
    if not steps:
        step_rows = (
            '<div class="empty">'
            '<div class="empty-icon">📝</div>'
            f'<div>{tr("project.no_steps")}</div>'
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
      <a class="btn btn-ghost btn-sm" href="{base}projects/{project_id}/edit{_p_suffix(p)}"
         style="display:flex;align-items:center;gap:0.3rem">
        {_icon("edit", 14, "var(--primary-dark)")} {tr("common.edit")}
      </a>
    </div>
    {desc}
    <div class="card project-progress-card">
      <div class="project-progress-head">
        <span>{done} von {total} {tr("project.steps")}</span><span>{pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill {fill_cls}" style="width:{pct}%"></div>
      </div>
    </div>
    {photos_card("project", project_id, f"{base}projects/{project_id}/photos", p, title=tr("project.photos"))}
    <div style="margin-bottom:1rem">{step_rows}</div>
    {comments_card("project", project_id, f"projects/{project_id}/comments", p)}
    <div class="card">
      <h3 style="margin-bottom:0.75rem">{tr("project.add_step")}</h3>
      <form method="post" action="{base}projects/{project_id}/steps">
        <input type="hidden" name="return_p" value="{p}">
        <div class="grid-2">
          <div class="form-group">
            <label>{tr("form.description")}</label>
            <input name="name" required placeholder="{tr("form.step_name_placeholder")}">
          </div>
          <div class="form-group">
            <label>{tr("form.points")}</label>
            <input name="points" type="number" value="5" min="1" max="100">
          </div>
        </div>
        <div class="form-group">
          <label>{tr("form.assigned_to")}</label>
          <select name="assigned_to">{person_opts}</select>
        </div>
        <div class="project-step-add-actions">
          <button class="btn btn-primary btn-sm" type="submit">
            {_icon("plus", 14, "white")} {tr("common.add")}
          </button>
          <a class="btn btn-ghost btn-sm" href="{base}projects">← {tr("project.all")}</a>
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
        f'<option value=""{_selected("", proj.assigned_to or "")}>— {tr("common.none")} —</option>'
        + "".join(f'<option value="{pn}"{_selected(pn, proj.assigned_to or "")}>{pn}</option>'
                  for pn in persons))
    content = f"""
    <div class="page-header">
      <h2>{tr("project.edit")}</h2>
      <a class="icon-btn" href="{base}projects/{project_id}{_p_suffix(p)}" title="{tr("common.cancel")}">{_icon("chevron_l", 20)}</a>
    </div>
    <div class="card">
      <form method="post" action="{base}projects/{project_id}/edit">
        <input type="hidden" name="return_p" value="{p}">
        <div class="form-group">
          <label>{tr("form.name")}</label>
          <input name="name" required value="{proj.name}">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>{tr("form.room")}</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>{tr("form.assigned_to")}</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
        </div>
        <div class="form-group">
          <label>{tr("form.description")}</label>
          <input name="description" value="{proj.description or ''}">
        </div>
        {_icon_chooser(proj.icon, "icon", include_room_icons=True)}
        <button class="btn btn-primary btn-full" type="submit">{tr("common.save")}</button>
        <a class="btn btn-ghost btn-full" href="{base}projects/{project_id}{_p_suffix(p)}"
           style="margin-top:0.5rem">{tr("common.cancel")}</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@router.post("/{project_id}/edit")
async def project_edit(project_id: str, request: Request, name: str = Form(...),
                        room: str = Form(...), assigned_to: str = Form(""),
                        description: str = Form(""), icon: str = Form(""),
                        return_p: str = Form("")):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    proj.name = name
    proj.room = room
    proj.assigned_to = assigned_to or None
    proj.description = description or None
    proj.icon = icon
    update_project(proj)
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(return_p)}", status_code=303)


@router.post("/{project_id}/comments")
async def project_comment_add(project_id: str, request: Request,
                              text: str = Form(...), return_p: str = Form("")):
    if not get_project(project_id):
        raise HTTPException(404)
    author = resolve_person(request, return_p)
    add_comment("project", project_id, text, author=author)
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(return_p)}", status_code=303)


@router.post("/{project_id}/photos")
async def project_photo_add(project_id: str, request: Request,
                            photo_type: str = Form("before"),
                            return_p: str = Form(""),
                            photo: UploadFile | None = File(None),
                            photo_camera: UploadFile | None = File(None),
                            photo_file: UploadFile | None = File(None)):
    if not get_project(project_id):
        raise HTTPException(404)
    selected_photo, data = await selected_photo_upload(photo, photo_camera, photo_file)
    if not selected_photo:
        raise HTTPException(400, "Kein Foto ausgewählt")
    author = resolve_person(request, return_p)
    add_photo("project", project_id, photo_type, selected_photo.filename or "",
              selected_photo.content_type or "", data, author=author)
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(return_p)}", status_code=303)


@router.get("/{project_id}/photos/{photo_id}/delete")
async def project_photo_delete(project_id: str, photo_id: str, request: Request, p: str = ""):
    delete_photo(photo_id, "project", project_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(p)}", status_code=303)


@router.get("/{project_id}/steps/{step_id}/remind", response_class=HTMLResponse)
async def step_remind_form(project_id: str, step_id: str, request: Request, p: str = ""):
    p = resolve_person(request, p)
    proj = get_project(project_id)
    step = get_step(step_id)
    if not proj or not step or step.project_id != project_id:
        raise HTTPException(404)

    assignee = project_step_assignee(step, proj)
    if not assignee or assignee == p:
        msg = quote("Keine andere Person für diesen Schritt")
        sep = "&" if p else "?"
        return RedirectResponse(
            _base(request) + f"projects/{project_id}{_p_suffix(p)}{sep}msg={msg}",
            status_code=303
        )

    content = project_step_reminder_form(proj, step, assignee, _base(request), p)
    return render(content, request, page="projects", person=p)


@router.post("/{project_id}/steps/{step_id}/remind")
async def step_remind_send(project_id: str, step_id: str, request: Request,
                           message: str = Form(...), return_p: str = Form("")):
    proj = get_project(project_id)
    step = get_step(step_id)
    if not proj or not step or step.project_id != project_id:
        raise HTTPException(404)

    sender = resolve_person(request, return_p)
    assignee = project_step_assignee(step, proj)
    sent = False
    if assignee and assignee != sender:
        sent = await send_project_step_reminder(proj, step, assignee, message, sender=sender)
    msg = (
        f"Erinnerung an {assignee} gesendet"
        if sent else
        f"Erinnerung für {assignee or 'niemanden'} als Notiz gespeichert"
    )
    sep = "&" if return_p else "?"
    return RedirectResponse(
        _base(request) + f"projects/{project_id}{_p_suffix(return_p)}{sep}msg={quote(msg)}",
        status_code=303
    )


@router.get("/{project_id}/delete")
async def project_delete(project_id: str, request: Request, p: str = ""):
    delete_project(project_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"projects{_p_suffix(p)}", status_code=303)


@router.get("/{project_id}/archive")
async def project_archive(project_id: str, request: Request, p: str = ""):
    proj = get_project(project_id)
    if proj:
        delete_project(project_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"projects{_p_suffix(p)}", status_code=303)


@router.post("/{project_id}/steps")
async def step_add(project_id: str, request: Request,
                   name: str = Form(...), points: int = Form(5),
                   assigned_to: str = Form(""), return_p: str = Form("")):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    assignee = assigned_to or proj.assigned_to
    add_step(Step(project_id=project_id, name=name, points=points,
                  assigned_to=assignee or None))
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(return_p)}", status_code=303)


@router.post("/{project_id}/steps/{step_id}/photos")
async def step_photo_add(project_id: str, step_id: str, request: Request,
                         photo_type: str = Form("before"),
                         return_p: str = Form(""),
                         photo: UploadFile | None = File(None),
                         photo_camera: UploadFile | None = File(None),
                         photo_file: UploadFile | None = File(None)):
    step = get_step(step_id)
    if not step or step.project_id != project_id:
        raise HTTPException(404)
    selected_photo, data = await selected_photo_upload(photo, photo_camera, photo_file)
    if not selected_photo:
        raise HTTPException(400, "Kein Foto ausgewählt")
    author = resolve_person(request, return_p)
    add_photo("step", step_id, photo_type, selected_photo.filename or "",
              selected_photo.content_type or "", data, author=author)
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(return_p)}", status_code=303)


@router.get("/{project_id}/steps/{step_id}/photos/{photo_id}/delete")
async def step_photo_delete(project_id: str, step_id: str, photo_id: str,
                            request: Request, p: str = ""):
    delete_photo(photo_id, "step", step_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(p)}", status_code=303)


@router.post("/{project_id}/steps/{step_id}/assign")
async def step_assign(project_id: str, step_id: str, request: Request,
                      assigned_to: str = Form(""), return_p: str = Form("")):
    if not assign_step(step_id, assigned_to=assigned_to or None):
        raise HTTPException(404)
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(return_p)}", status_code=303)


@router.post("/{project_id}/steps/{step_id}/done")
async def step_done(project_id: str, step_id: str, request: Request):
    form = await request.form()
    before = get_step(step_id)
    step = complete_step(step_id, done_by=form.get("done_by") or None)
    if not step:
        raise HTTPException(404)
    return_p = str(form.get("return_p") or "")
    msg = ""
    if before and not before.completed and step.completed_by:
        msg = f"+{step.points} Punkte für {step.name}"
    sep = "&" if return_p else "?"
    msg_suffix = f"{sep}msg={quote(msg)}" if msg else ""
    return RedirectResponse(
        _base(request) + f"projects/{project_id}{_p_suffix(return_p)}{msg_suffix}",
        status_code=303
    )


@router.get("/{project_id}/steps/{step_id}/delete")
async def step_delete(project_id: str, step_id: str, request: Request, p: str = ""):
    delete_step(step_id)
    p = resolve_person(request, p) if p else ""
    return RedirectResponse(_base(request) + f"projects/{project_id}{_p_suffix(p)}", status_code=303)
