from datetime import date, timedelta
from html import escape

from fastapi import Request
from fastapi.responses import HTMLResponse

from ha_client import get_areas, get_persons
from i18n import tr
from render import (INTERVALS, _icon_chooser, _selected, comments_card,
                    person_suffix, photos_card, render)
from task_ui import (_EFFORT_LABELS, _ONETIME_INTERVAL, _task_return_path)


async def task_form(request: Request, title: str, action: str,
                    submit_label: str, task=None, person: str = "",
                    return_to: str = "", get_areas_fn=get_areas,
                    get_persons_fn=get_persons) -> HTMLResponse:
    areas   = await get_areas_fn()
    persons = await get_persons_fn()
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
    cur_paused     = task.paused if task else False
    cur_pause_until = task.pause_until or "" if task else ""
    cur_pause_reason = task.pause_reason or "" if task else ""

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
        </div>
        <div class="form-group">
          <label>Pause</label>
          <label class="option-card task-priority-card" style="margin-bottom:0.65rem">
            <input type="checkbox" name="paused" value="1" {"checked" if cur_paused else ""}>
            <span class="task-priority-main">
              <span class="task-priority-title">{_i("pause", 15)} Aufgabe pausieren</span>
              <span class="task-priority-hint">
                Pausierte Aufgaben bleiben sichtbar, zählen aber nicht als fällig.
              </span>
            </span>
          </label>
          <div class="grid-2">
            <div>
              <label>Pause bis (optional)</label>
              <input type="date" name="pause_until" value="{cur_pause_until}">
            </div>
            <div>
              <label>Grund (optional)</label>
              <input name="pause_reason" value="{escape(cur_pause_reason)}"
                     placeholder="z.B. Urlaub, saisonal">
            </div>
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
                    title=tr("tasks.photos"), margin_top=True)
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
          <div class="task-form-section-title">{tr("task.before_photo")}</div>
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
                {_i("camera", 14)} {tr("photos.camera")}
              </label>
              <button class="btn btn-ghost btn-sm camera-start" type="button" hidden>
                {_i("camera", 14)} {tr("photos.camera")}
              </button>
              <label class="btn btn-outline btn-sm photo-file-button" for="{file_input_id}">
                {_i("plus", 14)} {tr("photos.file")}
              </label>
            </div>
            <div class="camera-panel" hidden>
              <video class="camera-preview" playsinline autoplay muted></video>
              <div class="camera-actions">
                <button class="btn btn-primary btn-sm camera-shot" type="button">
                  {_i("camera", 14, "white")} {tr("photos.capture")}
                </button>
                <button class="btn btn-ghost btn-sm camera-stop" type="button">{tr("photos.close")}</button>
              </div>
            </div>
            <div class="camera-msg muted"></div>
            <div class="muted photo-upload-hint">
              {tr("task.before_photo_hint")}
            </div>
          </div>
        </div>"""
    priority_option = f"""
        <label class="option-card task-priority-card">
          <input type="checkbox" name="important" value="1" {important_checked}>
          <span class="task-priority-main">
            <span class="task-priority-title">
              {star_svg} {tr("task.mark_important")}
            </span>
            <span class="task-priority-hint">
              {tr("task.important_hint")}
            </span>
          </span>
        </label>"""

    content = f"""
    <div class="page-header">
      <h2>{title}</h2>
      <a class="icon-btn" href="{back_url}" title="{tr("common.cancel")}">{_i("chevron_l", 20)}</a>
    </div>
    <div class="card task-form-card">
      <form method="post" action="{action}" enctype="multipart/form-data">
        <input type="hidden" name="return_p" value="{person}">
        <input type="hidden" name="return_to" value="{return_to}">
        <div class="task-form-section">
          <div class="task-form-section-title">{tr("task.section_task")}</div>
          <div class="form-group">
            <label>{tr("task.what")}</label>
            <input name="name" required placeholder="{tr("task.name_placeholder")}" value="{escape(cur_name)}">
          </div>
          {priority_option}
          {initial_note}
        </div>
        {initial_photo}

        <div class="task-form-section">
          <div class="task-form-section-title">{tr("task.section_planning")}</div>
          <div class="grid-2">
            <div class="form-group">
              <label>{tr("form.room")}</label>
              <select name="room">{room_opts}</select>
            </div>
            <div class="form-group">
              <label>{tr("task.interval")}</label>
              <select name="interval_days">{interval_opts}</select>
            </div>
            <div class="form-group">
              <label>{tr("form.points")}</label>
              <input name="points" type="number" value="{cur_points}" min="1" max="100">
            </div>
            <div class="form-group">
              <label>{tr("task.start_date_optional")}</label>
              <input type="date" name="start_date" value="{cur_start_date}">
            </div>
          </div>
          <div class="form-group">
            <label>{tr("effort.label")}</label>
            <div class="effort-picker">{effort_btns}</div>
          </div>
          {snooze_section}
        </div>

        <div class="task-form-section">
          <div class="task-form-section-title">{tr("task.section_responsibility")}</div>
          <div class="form-group">
            <label>{tr("form.assigned_to")}</label>
            <div class="task-assignee-grid">{person_boxes}</div>
          </div>
        </div>

        <div class="task-form-section">
          <div class="task-form-section-title">{tr("task.section_display")}</div>
          {_icon_chooser(cur_icon)}
        </div>

        <div class="form-actions">
          <button class="btn btn-primary btn-full" type="submit">{submit_label}</button>
          <a class="btn btn-ghost btn-full" href="{back_url}">{tr("common.cancel")}</a>
        </div>
      </form>
    </div>
    {photos}
    {comments}"""
    return render(content, request, page="tasks", person=person)
