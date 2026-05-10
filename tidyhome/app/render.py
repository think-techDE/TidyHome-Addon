from html import escape

from fastapi import Request
from fastapi.responses import HTMLResponse
from i18n import resolve_language, tr, translate_html
from storage import (get_admins, get_vacation_mode, is_vacation_mode_active,
                     get_person_settings)

from ui_cards import comments_card, photos_card
from ui_helpers import (
    INTERVALS,
    _base,
    _ha_user,
    _ring_chart,
    _selected,
    format_date_de,
    interval_label,
    person_suffix,
    resolve_person,
    urgency_class,
)
from ui_rows import (
    project_row,
    project_step_reminder_form,
    project_step_row,
    task_row,
)
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
