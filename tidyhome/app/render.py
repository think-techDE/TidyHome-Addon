from urllib.parse import quote
from datetime import date, datetime
from html import escape

from fastapi import Request
from fastapi.responses import HTMLResponse
from i18n import resolve_language, tr, translate_html
from storage import (get_admins, get_vacation_mode, is_vacation_mode_active,
                     count_photos, get_person_settings, list_comments, list_photos)

from ui_icons import (
    ROOM_ICON_CHOICES,
    ROOM_ICON_LABELS,
    ROOM_ICONS,
    _ICON_LABELS,
    _ICON_PATHS,
    _NAV_ITEMS,
    _TASK_ICONS,
    _auto_room_icon_config,
    _icon,
    _icon_chooser,
    _openmoji_nav_icon,
    _proj_icon,
    _room_icon,
    _task_icon,
    _task_icon_key,
)

INTERVALS = {
    1: "Täglich", 2: "Alle 2 Tage", 7: "Wöchentlich", 14: "Alle 2 Wochen",
    30: "Monatlich", 90: "Vierteljährlich", 180: "Halbjährlich", 365: "Jährlich",
}


def _ring_chart(value_str: str, pct: int, color: str, label: str, size: int = 70) -> str:
    """SVG donut ring chart with center text label."""
    safe_pct = max(0, min(pct, 100))
    return (
        f'<div style="text-align:center">'
        f'<div style="position:relative;width:{size}px;height:{size}px;margin:0 auto 0.4rem">'
        f'<svg viewBox="0 0 36 36" width="{size}" height="{size}" style="transform:rotate(-90deg)">'
        f'<circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--ring-bg)" stroke-width="3"/>'
        f'<circle cx="18" cy="18" r="15.9" fill="none" stroke="{color}" stroke-width="3"'
        f' stroke-dasharray="{safe_pct} 100" stroke-linecap="round"/>'
        f'</svg>'
        f'<div style="position:absolute;inset:0;display:flex;align-items:center;'
        f'justify-content:center;font-size:0.82rem;font-weight:800;color:var(--text)">'
        f'{value_str}</div>'
        f'</div>'
        f'<div style="font-size:0.65rem;color:var(--muted);font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.05em">{label}</div>'
        f'</div>'
    )


def interval_label(days: int) -> str:
    if days <= 0:
        return "Einmalig"
    return INTERVALS.get(days, f"Alle {days} Tage")


def urgency_class(days: int) -> str:
    if days < 0:  return "overdue"
    if days == 0: return "today"
    if days <= 3: return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


def _ha_user(request: Request) -> str:
    return (
        request.headers.get("X-Remote-User-Display-Name") or
        request.headers.get("X-Remote-User-Name", "")
    ).strip()


def person_suffix(person: str = "", separator: str = "?") -> str:
    return f"{separator}p={quote(person)}" if person else ""


def resolve_person(request: Request, p_param: str = "") -> str:
    ha_user = _ha_user(request)
    if p_param and ha_user in get_admins():
        return p_param
    return ha_user or p_param


def _selected(value, current) -> str:
    return " selected" if str(value) == str(current) else ""


def format_date_de(raw: str) -> str:
    if not raw:
        return ""
    try:
        return date.fromisoformat(raw).strftime("%d.%m.%Y")
    except ValueError:
        return raw


def _comment_time(raw: str) -> str:
    try:
        return datetime.fromisoformat(raw).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return raw[:16].replace("T", " ")


def comments_card(entity_type: str, entity_id: str, action: str,
                  person: str = "", margin_top: bool = False) -> str:
    comments = list_comments(entity_type, entity_id)
    total = len(comments)
    if comments:
        rows = ""
        for c in comments:
            author = escape(c.author or "Unbekannt")
            text = escape(c.text).replace("\n", "<br>")
            created = escape(_comment_time(c.created_at))
            rows += f"""
            <div class="task-row" style="align-items:flex-start">
              <div class="task-body">
                <div class="task-header">
                  <span class="task-name">{author}</span>
                  <span class="task-meta">{created}</span>
                </div>
                <div class="muted" style="margin-top:0.25rem;line-height:1.45">{text}</div>
              </div>
            </div>"""
    else:
        rows = (
            '<div class="comments-empty">'
            f'<div style="font-weight:600">{tr("comments.none")}</div>'
            '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            f'{tr("comments.empty_hint")}</div>'
            '</div>'
        )

    margin = "margin-top:1rem;" if margin_top else "margin-bottom:1rem;"
    open_attr = " open" if total else ""
    count_label = f"{total} Notiz{'en' if total != 1 else ''}" if total else tr("comments.none")
    return f"""
    <details class="card comments-card" style="{margin}"{open_attr}>
      <summary class="comments-head">
        <div>
          <h3>{tr("comments.title")}</h3>
          <div class="muted">{count_label} · {tr("comments.summary")}</div>
        </div>
        <span class="comment-summary-icon">{_icon("edit", 15)}</span>
      </summary>
      {rows}
      <form class="comment-form" method="post" action="{action}">
        <input type="hidden" name="return_p" value="{person}">
        <div class="form-group">
          <label>{tr("comments.new")}</label>
          <textarea name="text" rows="3" required placeholder="{tr("comments.placeholder")}"></textarea>
        </div>
        <button class="btn btn-primary btn-sm" type="submit">{tr("comments.save")}</button>
      </form>
    </details>"""


def photos_card(entity_type: str, entity_id: str, action: str,
                person: str = "", title: str = "",
                margin_top: bool = False) -> str:
    title = title or tr("photos.photos")
    photos = list_photos(entity_type, entity_id)
    total = len(photos)
    safe_id = "".join(ch if ch.isalnum() else "-" for ch in f"{entity_type}-{entity_id}")
    live_input_id = escape(f"photo-live-{safe_id}")
    camera_input_id = escape(f"photo-camera-{safe_id}")
    file_input_id = escape(f"photo-file-{safe_id}")
    sections = {"before": "", "after": ""}
    for photo in photos:
        ptype = photo.get("photo_type") if photo.get("photo_type") in sections else "before"
        label = "Vorher" if ptype == "before" else "Nachher"
        filename = escape(photo.get("filename", ""))
        photo_id = escape(photo.get("id", ""))
        sections[ptype] += f"""
        <figure class="photo-tile">
          <img src="photos/{filename}" alt="{label}">
          <figcaption>
            <span>{label}</span>
            <a class="photo-delete" href="{action}/{photo_id}/delete{person_suffix(person)}"
               onclick="return confirm('Foto löschen?')" title="Foto löschen">
              {_icon("trash", 13)}
            </a>
          </figcaption>
        </figure>"""

    def _section(label: str, key: str) -> str:
        body = sections[key] or '<div class="photo-empty">Noch kein Foto</div>'
        return f"""
        <div class="photo-section">
          <div class="photo-section-title">{label}</div>
          <div class="photo-grid">{body}</div>
        </div>"""

    margin = "margin-top:1rem;" if margin_top else "margin-bottom:1rem;"
    open_attr = " open" if total else ""
    count_label = f"{total} {tr('photos.photos')}" if total else tr("photos.no_photos")
    return f"""
    <details class="card photos-card" style="{margin}"{open_attr}>
      <summary class="photos-head">
        <div>
          <h3>{title}</h3>
          <div class="muted">{count_label} · {tr("photos.document")}</div>
        </div>
        <span class="photo-summary-icon">{_icon("camera", 15)}</span>
      </summary>
      {_section(tr("photos.before"), "before")}
      {_section(tr("photos.after"), "after")}
      <form class="photo-upload" method="post" action="{action}" enctype="multipart/form-data">
        <input type="hidden" name="return_p" value="{person}">
        <div class="photo-type-picker">
          <label class="option-card">
            <input type="radio" name="photo_type" value="before" checked>
            <span>{tr("photos.before")}</span>
          </label>
          <label class="option-card">
            <input type="radio" name="photo_type" value="after">
            <span>{tr("photos.after")}</span>
          </label>
        </div>
        <input id="{live_input_id}" class="photo-file-input photo-live-input" type="file"
               name="photo" accept="image/*">
        <input id="{camera_input_id}" class="photo-file-input" type="file"
               name="photo_camera" accept="image/*,android/force-camera-workaround"
               capture="environment" onchange="this.form.submit()">
        <input id="{file_input_id}" class="photo-file-input" type="file"
               name="photo_file" accept="image/*" onchange="this.form.submit()">
        <div class="photo-actions">
          <label class="btn btn-ghost btn-sm camera-native-button" for="{camera_input_id}">
            {_icon("camera", 14)} {tr("photos.camera")}
          </label>
          <button class="btn btn-ghost btn-sm camera-start" type="button" hidden>
            {_icon("camera", 14)} {tr("photos.camera")}
          </button>
          <label class="btn btn-outline btn-sm photo-file-button" for="{file_input_id}">
            {_icon("plus", 14)} {tr("photos.file")}
          </label>
        </div>
        <div class="camera-panel" hidden>
          <video class="camera-preview" playsinline autoplay muted></video>
          <div class="camera-actions">
            <button class="btn btn-primary btn-sm camera-shot" type="button">
              {_icon("camera", 14, "white")} {tr("photos.capture")}
            </button>
            <button class="btn btn-ghost btn-sm camera-stop" type="button">{tr("photos.close")}</button>
          </div>
        </div>
        <div class="camera-msg muted"></div>
        <div class="muted photo-upload-hint">{tr("photos.hint")}</div>
      </form>
    </details>"""


def task_row(task, base: str = "", person: str = "", show_assigned: bool = False,
             paused: bool = False, vacation_until: str = "") -> str:
    from reminders import task_reminder_recipients

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
            f"Pausiert bis {format_date_de(pause_until)}"
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
    psuffix = person_suffix(person)

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
        f"?scope=people{person_suffix(person, '&')}"
        if grouped_by_person else person_suffix(person)
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
            f'<a class="icon-btn" href="projects/{project.id}/archive{person_suffix(person)}" '
            f'title="Archivieren">{_icon("archive", 16)}</a>'
        )
    else:
        action_btns = (
            f'<a class="icon-btn" href="projects/{project.id}/edit{person_suffix(person)}" '
            f'title="{tr("common.edit")}">{_icon("edit", 16)}</a>'
        )
    del_btn = (
        f'<a class="icon-btn danger" href="projects/{project.id}/delete{person_suffix(person)}" '
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
    psuffix = person_suffix(person)
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
    psuffix = person_suffix(person)
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


def render(content: str, request: Request, page: str = "home",
           person: str = "") -> HTMLResponse:
    base = _base(request)
    psuffix = person_suffix(person)
    admins = get_admins()
    ha_user = _ha_user(request)
    is_admin = ha_user in admins
    display_person = person or ha_user
    language_person = ha_user or display_person
    lang_setting = (
        get_person_settings(language_person).get("language", "auto")
        if language_person else "auto"
    )
    ui_language = resolve_language(
        lang_setting,
        request.headers.get("accept-language", ""),
    )
    vacation_banner = ""
    flash = ""
    msg = request.query_params.get("msg", "").strip()
    if msg:
        flash = (
            '<div class="card" style="border-color:var(--success);'
            'background:var(--success-bg);margin-bottom:1rem">'
            f'<div style="font-weight:750;color:var(--success)">{escape(msg)}</div>'
            '</div>'
        )
    if display_person and is_vacation_mode_active(display_person):
        vacation = get_vacation_mode(display_person)
        until = vacation.get("until") or ""
        until_txt = f" bis {format_date_de(until)}" if until else ""
        vacation_banner = (
            '<div class="card" style="border-color:var(--warning);'
            'background:var(--warning-bg);margin-bottom:1rem">'
            f'<div style="font-weight:750;color:var(--warning)">{tr("vacation.active")}{until_txt}</div>'
            '<div class="muted" style="margin-top:0.25rem;font-size:0.82rem">'
            f'{tr("vacation.paused_notice")}</div>'
            '</div>'
        )

    # Person nav pill / dropdown
    if not display_person:
        person_nav = f'<a href="{base}settings" class="h-pill">{tr("menu.who")}</a>'
    elif is_admin:
        profile_person = person or ha_user
        viewing_other = bool(ha_user and profile_person != ha_user)
        menu_hint = (
            f'{tr("menu.view_of")} {profile_person}'
            if viewing_other else
            tr("menu.my_view")
        )
        own_link = (
            f'<a href="{base}" class="hpill-action">{_icon("home", 16)}<span>{tr("menu.back_to_my_view")}</span></a>'
            if viewing_other else ""
        )
        current_profile = (
            f'<a href="{base}settings{person_suffix(profile_person)}" class="hpill-action">'
            f'{_icon("settings", 16)}<span>{tr("menu.settings_for")} {profile_person}</span></a>'
        )
        own_profile = (
            f'<a href="{base}settings{person_suffix(ha_user)}" class="hpill-action">'
            f'{_icon("person", 16)}<span>{tr("menu.my_settings")}</span></a>'
            if viewing_other else ""
        )
        person_nav = f'''
        <details class="hpill-menu">
          <summary class="h-pill h-pill-person">
            {_icon("person", 15)}
            <span>{display_person}</span>
            <span class="h-pill-caret">▾</span>
          </summary>
          <div class="hpill-dropdown">
            <div class="hpill-head">
              <div class="hpill-head-label">{menu_hint}</div>
              <div class="hpill-head-name">{display_person}</div>
            </div>
            <div class="hpill-section-label">{tr("menu.view")}</div>
            {own_link}
            <a href="{base}settings" class="hpill-action">{_icon("person", 16)}<span>{tr("menu.switch_person")}</span></a>
            <div class="hpill-section-label">{tr("menu.settings")}</div>
            {own_profile}
            {current_profile}
            <div class="hpill-section-label">{tr("menu.housekeepers")}</div>
            <a href="{base}housekeeping" class="hpill-action">{_icon("clock", 16)}<span>{tr("menu.manage_work_times")}</span></a>
            <div class="hpill-section-label">{tr("menu.admin")}</div>
            <a href="{base}admin" class="hpill-action">{_icon("settings", 16)}<span>{tr("menu.admin_area")}</span></a>
          </div>
        </details>'''
    else:
        person_nav = (
            f'<a href="{base}settings{person_suffix(display_person)}" class="h-pill h-pill-person">'
            f'{_icon("person", 15)}<span>{display_person}</span></a>'
        )

    # Bottom navigation with local OpenMoji icons
    nav_items = ""
    for icon_file, label_key, page_key, href in _NAV_ITEMS:
        label = tr(label_key)
        active = "active" if page == page_key else ""
        nav_items += (
            f'<a href="{href}{psuffix}" class="nav-item {active}">'
            f'{_openmoji_nav_icon(icon_file, label)}'
            f'<span>{label}</span>'
            f'</a>'
        )

    html = f"""<!DOCTYPE html>
<html lang="{ui_language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<base href="{base}">
<title>TidyHome</title>
<link rel="icon" type="image/svg+xml" href="assets/logo.svg">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{background:#f4f0f2;color:#24181f;
             font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
             padding-bottom:5rem}}
  body{{opacity:0}}
  header{{background:rgba(255,255,255,0.90);border-bottom:1px solid #ddd6da;
          padding:0.75rem 1rem;display:flex;align-items:center;
          justify-content:space-between;position:sticky;top:0;z-index:10}}
  .bottom-nav{{position:fixed;bottom:0;left:0;right:0;height:4.25rem;
               background:rgba(255,255,255,0.96);border-top:1px solid #ddd6da;
               display:flex;z-index:10;overflow:hidden}}
  .nav-item{{flex:1;display:flex;flex-direction:column;align-items:center;
             justify-content:center;text-decoration:none;color:transparent}}
  @media(prefers-color-scheme:dark){{
    html,body{{background:#101114;color:#f4f1f2}}
    header,.bottom-nav{{background:rgba(24,26,31,0.92);border-color:#30333b}}
  }}
</style>
<link rel="stylesheet" href="assets/app.css">
</head>
<body>
<header>
  <div class="h-left">
    <img src="assets/logo.svg" style="width:28px;height:28px;border-radius:7px">
    <span class="h-title">TidyHome</span>
  </div>
  <div style="display:flex;gap:0.5rem;align-items:center">
    {person_nav}
  </div>
</header>
<main>
        {flash}
        {vacation_banner}
        {content}
      </main>
<nav class="bottom-nav">{nav_items}</nav>
<script>
(function(){{
  function selectedPhotoType(card){{
    var selected = card.querySelector('input[name="photo_type"]:checked');
    return selected ? selected.value : 'before';
  }}

  function setCameraMessage(card, text){{
    var msg = card.querySelector('.camera-msg');
    if (msg) msg.textContent = text || '';
  }}

  async function stopCamera(card){{
    var stream = card._cameraStream;
    if (stream) stream.getTracks().forEach(function(track){{ track.stop(); }});
    card._cameraStream = null;
    var panel = card.querySelector('.camera-panel');
    if (panel) panel.hidden = true;
  }}

  function waitForVideo(video){{
    if (video.videoWidth && video.videoHeight) return Promise.resolve();
    return new Promise(function(resolve){{
      var done = function(){{
        clearTimeout(timer);
        video.removeEventListener('loadedmetadata', done);
        video.removeEventListener('canplay', done);
        resolve();
      }};
      var timer = setTimeout(done, 1500);
      video.addEventListener('loadedmetadata', done);
      video.addEventListener('canplay', done);
    }});
  }}

  function setCameraMode(card, liveMode){{
    var nativeButton = card.querySelector('.camera-native-button');
    var liveButton = card.querySelector('.camera-start');
    if (nativeButton) nativeButton.hidden = !!liveMode;
    if (liveButton) liveButton.hidden = !liveMode;
  }}

  function enhanceCameraControls(){{
    var liveMode = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    document.querySelectorAll('.photos-card').forEach(function(card){{
      setCameraMode(card, liveMode);
    }});
  }}

  function markPendingPhoto(card, input){{
    if (!card || !card.classList.contains('photo-pending-card')) return;
    card.querySelectorAll('.photo-file-input').forEach(function(other){{
      if (other !== input) other.value = '';
    }});
    var filename = input && input.files && input.files.length ? input.files[0].name : '';
    card.classList.toggle('has-pending-photo', !!filename);
    setCameraMessage(card, filename ? 'Vorher-Foto ausgewählt: ' + filename : '');
  }}

  async function startCamera(card){{
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
      setCameraMode(card, false);
      setCameraMessage(card, 'Live-Kamera nicht verfügbar. Nutze Kamera öffnen oder Datei auswählen als Fallback.');
      return;
    }}
    try {{
      await stopCamera(card);
      var stream = await navigator.mediaDevices.getUserMedia({{
        video: {{ facingMode: {{ ideal: 'environment' }} }},
        audio: false
      }});
      card._cameraStream = stream;
      var video = card.querySelector('.camera-preview');
      var panel = card.querySelector('.camera-panel');
      video.srcObject = stream;
      panel.hidden = false;
      setCameraMessage(card, '');
    }} catch (err) {{
      setCameraMode(card, false);
      setCameraMessage(card, 'Live-Kamera wurde blockiert. Kamera öffnen nutzt jetzt den nativen Kamera-/Dateidialog.');
    }}
  }}

  async function snapshotBlob(video){{
    await waitForVideo(video);
    return new Promise(function(resolve){{
      var canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 960;
      canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(function(blob){{ resolve(blob); }}, 'image/jpeg', 0.9);
    }});
  }}

  async function uploadBlob(card, blob){{
    var pending = card.classList.contains('photo-pending-card');
    var form = card.querySelector('.photo-upload') || card.closest('form');
    var input = card.querySelector('.photo-live-input');
    if (!form || !input || !blob) return;

    if (window.File && window.DataTransfer) {{
      var file = new File([blob], 'camera.jpg', {{ type: 'image/jpeg' }});
      var transfer = new DataTransfer();
      transfer.items.add(file);
      input.files = transfer.files;
      await stopCamera(card);
      if (pending) {{
        markPendingPhoto(card, input);
        return;
      }}
      form.submit();
      return;
    }}

    if (pending) {{
      await stopCamera(card);
      setCameraMessage(card, 'Live-Foto konnte nicht übernommen werden. Bitte Kamera öffnen oder Datei auswählen nutzen.');
      return;
    }}

    var data = new FormData();
    data.append('photo_type', selectedPhotoType(card));
    var returnP = form.querySelector('input[name="return_p"]');
    if (returnP) data.append('return_p', returnP.value);
    data.append('photo', blob, 'camera.jpg');

    var response = await fetch(form.action, {{
      method: 'POST',
      body: data,
      credentials: 'same-origin'
    }});
    if (!response.ok && !response.redirected) throw new Error('upload failed');
    await stopCamera(card);
    window.location.href = response.url || window.location.href;
  }}

  async function takePhoto(card){{
    var video = card.querySelector('.camera-preview');
    if (!video || !video.srcObject) return;
    try {{
      setCameraMessage(card, 'Foto wird gespeichert...');
      var blob = await snapshotBlob(video);
      if (!blob) throw new Error('snapshot failed');
      await uploadBlob(card, blob);
    }} catch (err) {{
      setCameraMessage(card, 'Foto konnte nicht gespeichert werden. Bitte Datei auswählen nutzen.');
    }}
  }}

  document.addEventListener('click', function(event){{
    var start = event.target.closest('.camera-start');
    var shot = event.target.closest('.camera-shot');
    var stop = event.target.closest('.camera-stop');
    if (!start && !shot && !stop) return;
    var card = event.target.closest('.photos-card');
    if (!card) return;
    if (start) startCamera(card);
    if (shot) takePhoto(card);
    if (stop) stopCamera(card);
  }});
  document.addEventListener('change', function(event){{
    var input = event.target.closest('.photo-file-input');
    if (!input) return;
    var card = input.closest('.photos-card');
    markPendingPhoto(card, input);
  }});
  document.addEventListener('DOMContentLoaded', enhanceCameraControls);
  enhanceCameraControls();
}})();
</script>
</body>
</html>"""

    return HTMLResponse(
        translate_html(html, ui_language),
        headers={"Content-Language": ui_language},
    )
