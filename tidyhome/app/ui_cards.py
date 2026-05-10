from datetime import datetime
from html import escape
from urllib.parse import quote

from i18n import tr
from storage import list_comments, list_photos
from ui_icons import _icon


def _person_suffix(person: str = "", separator: str = "?") -> str:
    return f"{separator}p={quote(person)}" if person else ""


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
            <a class="photo-delete" href="{action}/{photo_id}/delete{_person_suffix(person)}"
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
