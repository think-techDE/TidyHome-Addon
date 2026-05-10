from datetime import date
from html import escape
from urllib.parse import quote

from i18n import tr
from reminders import task_reminder_recipients
from storage import count_photos
from ui_icons import _icon, _proj_icon, _task_icon


def _person_suffix(person: str = "", separator: str = "?") -> str:
    return f"{separator}p={quote(person)}" if person else ""


def _format_date_de(raw: str) -> str:
    if not raw:
        return ""
    try:
        return date.fromisoformat(raw).strftime("%d.%m.%Y")
    except ValueError:
        return raw


def task_row(task, base: str = "", person: str = "", show_assigned: bool = False,
             paused: bool = False, vacation_until: str = "") -> str:
    effort_labels = {"low": tr("effort.low"), "medium": tr("effort.medium"), "high": tr("effort.high")}
    effort_badges = {"low": "ok", "medium": "today", "high": "overdue"}
    due = task.days_until_due()

    if due < 0:
        badge_text, badge_cls = tr("status.overdue"), "overdue"
        date_text = f"{abs(due)}d überfällig"
    elif due == 0:
        badge_text, badge_cls = tr("status.today"), "today"
        date_text = tr("date.today")
    else:
        badge_text, badge_cls = tr("status.planned"), "ok"
        date_text = tr("date.tomorrow") if due == 1 else f"In {due} Tagen"

    if task.snooze_until:
        try:
            snooze_d = date.fromisoformat(task.snooze_until)
            if snooze_d > date.today():
                date_text = f"Verschoben bis {snooze_d.strftime('%-d. %b')}"
                badge_text, badge_cls = "Verschoben", "ok"
        except ValueError:
            pass

    task_paused = bool(paused or getattr(task, "is_paused", lambda: False)())
    pause_until = getattr(task, "pause_until", "") or vacation_until
    pause_reason = getattr(task, "pause_reason", "") or ""

    if task_paused:
        badge_text, badge_cls = tr("status.paused"), "ok"
        date_text = (
            f"Pausiert bis {_format_date_de(pause_until)}"
            if pause_until else tr("status.paused")
        )
        if pause_reason:
            date_text += f" · {pause_reason}"

    important_cls = " important" if task.important else ""
    paused_cls = " is-paused" if task_paused else ""
    star = _icon("star", 13, "var(--warning)", 2.5) if task.important else ""
    effort_badge = (
        f'<span class="badge {effort_badges[task.effort]}" '
        f'style="font-size:0.62rem;flex-shrink:0">{effort_labels[task.effort]}</span>'
    ) if task.effort in effort_labels else ""
    sub_badges = (
        f'<div class="task-badge-subrow">{effort_badge}</div>'
        if effort_badge else ""
    )
    assigned_txt = ""
    if task.assigned_to and show_assigned:
        assigned_txt = (
            f'<span class="task-meta" style="font-size:0.72rem">'
            f'→ {", ".join(task.assigned_to)}</span>'
        )
    task_meta_inline = f'<span class="task-name-meta"> · {date_text}</span>'
    photo_count = count_photos("task", task.id)
    photo_badge = (
        f'<span class="task-photo-badge" title="{photo_count} Foto'
        f'{"s" if photo_count != 1 else ""}">{_icon("camera", 12)} {photo_count}</span>'
        if photo_count else ""
    )
    psuffix = _person_suffix(person)

    done_btn = (
        f'<form class="inline" method="post" action="{base}tasks/{task.id}/done">'
        + (f'<input type="hidden" name="done_by" value="{person}">' if person else "")
        + (f'<input type="hidden" name="return_p" value="{person}">' if person else "")
        + f'<button class="icon-btn success" title="{tr("common.done")}">{_icon("check", 17)}</button>'
        f'</form>'
    )
    snooze_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/snooze{psuffix}" '
        f'title="Verschieben">{_icon("clock", 16)}</a>'
    )
    pause_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/pause{psuffix}" '
        f'title="Pause bearbeiten">{_icon("pause", 15)}</a>'
    )
    remind_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/remind{psuffix}" '
        f'title="Andere erinnern">{_icon("bell", 16)}</a>'
    ) if task_reminder_recipients(task, person) else ""
    edit_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/edit{psuffix}" title="{tr("common.edit")}">'
        f'{_icon("edit", 16)}</a>'
    )
    del_btn = (
        f'<a class="icon-btn danger" href="{base}tasks/{task.id}/delete{psuffix}" '
        f'onclick="return confirm(\'{tr("task.delete_confirm")}\')" title="{tr("common.delete")}">'
        f'{_icon("trash", 16)}</a>'
    )

    return f"""
    <div class="task-row{important_cls}{paused_cls}">
      {_task_icon(task.name, task.room, icon=task.icon, size=40)}
      <div class="task-body">
        <div class="task-header">
          <span class="task-name">{star}{task.name}{task_meta_inline}</span>
          <div class="task-badges">
            <span class="badge {badge_cls}">{badge_text}</span>
            {sub_badges}
          </div>
        </div>
        {f'<div class="task-date">{assigned_txt}{photo_badge}</div>' if assigned_txt or photo_badge else ''}
      </div>
      <div class="task-actions">
        {done_btn}{snooze_btn}{pause_btn}{remind_btn}{edit_btn}{del_btn}
      </div>
    </div>"""


def project_row(project, visible_steps: list, all_steps: list, person: str = "",
                grouped_by_person: bool = False, person_name: str = "") -> str:
    done, total = project.progress(visible_steps)
    pct = int(done / total * 100) if total else 0
    assigned = (
        f"<span>→ {project.assigned_to}</span>"
        if project.assigned_to and not grouped_by_person else ""
    )
    fill_class = "green" if project.completed else ""
    opacity = "opacity:0.65;" if project.completed else ""
    detail_suffix = (
        f"?scope=people{_person_suffix(person, '&')}"
        if grouped_by_person else _person_suffix(person)
    )
    person_hint = f" · {person_name}" if person_name else ""
    status_badge = (
        f'<span class="badge ok">{tr("status.done")}</span>'
        if project.completed else f'<span class="badge today">{done}/{total}</span>'
    )
    project_photo_count = count_photos("project", project.id)
    step_photo_count = sum(count_photos("step", step.id) for step in all_steps)
    photo_count = project_photo_count + step_photo_count
    photo_hint = (
        f'<span class="task-photo-badge" title="{photo_count} Foto'
        f'{"s" if photo_count != 1 else ""}">{_icon("camera", 12)} {photo_count}</span>'
        if photo_count else ""
    )
    reference_person = person_name or person
    foreign_open_assignees: list[str] = []
    for step in all_steps:
        assignee = step.assigned_to or project.assigned_to or ""
        if step.completed or not assignee or assignee == reference_person:
            continue
        if assignee not in foreign_open_assignees:
            foreign_open_assignees.append(assignee)
    foreign_open_count = sum(
        1
        for step in all_steps
        if not step.completed
        and (step.assigned_to or project.assigned_to or "")
        and (step.assigned_to or project.assigned_to or "") != reference_person
    )
    if foreign_open_count:
        shown_names = ", ".join(escape(name) for name in foreign_open_assignees[:2])
        more = f" +{len(foreign_open_assignees) - 2}" if len(foreign_open_assignees) > 2 else ""
        foreign_hint = (
            f'<span class="proj-reminder-hint">{_icon("bell", 13)} '
            f'{foreign_open_count} offen bei {shown_names}{more}</span>'
        )
    else:
        foreign_hint = ""

    if project.completed:
        action_btns = (
            f'<a class="icon-btn" href="projects/{project.id}/archive{_person_suffix(person)}" '
            f'title="Archivieren">{_icon("archive", 16)}</a>'
        )
    else:
        action_btns = (
            f'<a class="icon-btn" href="projects/{project.id}/edit{_person_suffix(person)}" '
            f'title="{tr("common.edit")}">{_icon("edit", 16)}</a>'
        )
    del_btn = (
        f'<a class="icon-btn danger" href="projects/{project.id}/delete{_person_suffix(person)}" '
        f'onclick="return confirm(\'{tr("project.delete_confirm")}\')" title="{tr("common.delete")}">'
        f'{_icon("trash", 16)}</a>'
    )

    return f"""
    <div class="proj-row" style="{opacity}">
      <a href="projects/{project.id}{detail_suffix}" style="display:contents;text-decoration:none">
        {_proj_icon(project.room, icon=project.icon)}
      </a>
      <div class="proj-main">
        <div class="proj-head">
          <a class="proj-title" href="projects/{project.id}{detail_suffix}">{project.name}</a>
          {status_badge}
        </div>
        <div class="proj-meta">
          <span>{project.room}{person_hint}</span>
          <span>{len(all_steps)} {tr("project.steps")}</span>
          {assigned}
          {photo_hint}
          {foreign_hint}
        </div>
        <div class="proj-progress">
          <div class="progress-track">
            <div class="progress-fill {fill_class}" style="width:{pct}%"></div>
          </div>
          <span class="proj-percent">{pct}%</span>
        </div>
      </div>
      <div class="task-actions">{action_btns}{del_btn}</div>
    </div>"""


def project_step_row(project, step, assignee: str, person_options: str,
                     base: str, person: str = "") -> str:
    psuffix = _person_suffix(person)
    photo_count = count_photos("step", step.id)
    photo_hint = (
        f' · <span class="task-photo-badge" title="{photo_count} Foto'
        f'{"s" if photo_count != 1 else ""}">{_icon("camera", 12)} {photo_count}</span>'
        if photo_count else ""
    )
    if step.completed:
        who = f" · {step.completed_by}" if step.completed_by else ""
        return f"""
        <div class="project-step-row is-done">
          <span style="color:var(--success);font-size:1.1rem;flex-shrink:0">
            {_icon("check", 18, "var(--success)")}
          </span>
          <div class="project-step-main">
            <span class="project-step-title">{step.name}</span>
            <span class="project-step-meta">{step.points} Pkt · → {assignee or "Niemand"}{who}{photo_hint}</span>
          </div>
        </div>"""

    remind_btn = (
        f'<a class="icon-btn" href="{base}projects/{project.id}/steps/{step.id}/remind{psuffix}" '
        f'title="Andere erinnern">{_icon("bell", 16)}</a>'
    ) if assignee and assignee != person else ""

    return f"""
    <div class="project-step-row">
      <div class="project-step-main">
        <span class="project-step-title">{step.name}</span>
        <span class="project-step-meta">{step.points} Pkt{photo_hint}</span>
      </div>
      <div class="project-step-actions">
        <form class="project-step-form" method="post" action="{base}projects/{project.id}/steps/{step.id}/assign">
          <input type="hidden" name="return_p" value="{person}">
          <select class="project-step-person" name="assigned_to" aria-label="Zugewiesen an"
                  onchange="this.form.submit()">
          {person_options}
          </select>
        </form>
        <form class="inline" method="post" action="{base}projects/{project.id}/steps/{step.id}/done">
          <input type="hidden" name="done_by" value="{assignee}">
          <input type="hidden" name="return_p" value="{person}">
          <button class="icon-btn success" title="{tr("common.done")}">{_icon("check", 17)}</button>
        </form>
        {remind_btn}
        <a class="icon-btn danger"
           href="{base}projects/{project.id}/steps/{step.id}/delete{psuffix}"
           onclick="return confirm('Schritt löschen?')"
           title="Schritt löschen">
           {_icon("trash", 15)}
        </a>
      </div>
    </div>"""


def project_step_reminder_form(project, step, assignee: str, base: str,
                               person: str = "") -> str:
    default_message = f"Kannst du bitte an {step.name} denken?"
    psuffix = _person_suffix(person)
    return f"""
    <div class="page-header">
      <h2>Erinnerung senden</h2>
      <a class="icon-btn" href="{base}projects/{project.id}{psuffix}" title="Abbrechen">{_icon("chevron_l", 20)}</a>
    </div>
    <div class="card" style="margin-bottom:0.75rem">
      <div style="font-weight:600;margin-bottom:0.2rem">{project.name}</div>
      <div class="task-meta">{step.name} · {assignee}</div>
    </div>
    <div class="card">
      <form method="post" action="{base}projects/{project.id}/steps/{step.id}/remind">
        <input type="hidden" name="return_p" value="{person}">
        <div class="form-group">
          <label>Erinnerung an</label>
          <div style="padding:0.7rem 0.8rem;border:1px solid var(--border);
                      border-radius:8px;background:var(--bg-soft);font-weight:600">
            {assignee}
          </div>
        </div>
        <div class="form-group">
          <label>Nachricht</label>
          <textarea name="message" rows="3" required>{escape(default_message)}</textarea>
        </div>
        <button class="btn btn-primary btn-full" type="submit">Erinnerung senden</button>
        <a class="btn btn-ghost btn-full" href="{base}projects/{project.id}{psuffix}"
           style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
