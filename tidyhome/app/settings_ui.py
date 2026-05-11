from datetime import date
from html import escape
from urllib.parse import quote

from i18n import language_options, normalize_language, tr
from render import format_date_de, person_suffix
from storage import (ROLES, get_person_settings, get_vacation_mode,
                     is_vacation_mode_active)


def _person_settings_card(pn: str, areas: list[str], admins: set[str],
                           base: str = "", action: str = "settings",
                           show_admin_fields: bool = False) -> str:
    """HTML-Karte für die Einstellungen einer einzelnen Person."""
    cfg = get_person_settings(pn)
    time_val = cfg.get("notify_time", "08:00")
    checked = "checked" if cfg.get("enabled") else ""
    services = cfg.get("services") or []
    hidden_rooms = set(cfg.get("hidden_rooms") or [])
    weekly_goal = cfg.get("weekly_goal", 0) or 0
    role = cfg.get("role", "member")
    can_see_children = cfg.get("can_see_children", False)
    language = normalize_language(cfg.get("language", "auto") or "auto")
    lang_opts = language_options(language)
    pn_html = escape(pn)
    pn_attr = escape(pn, quote=True)
    pn_url = quote(pn, safe="")
    vacation = get_vacation_mode(pn)
    vacation_active = is_vacation_mode_active(pn)
    vacation_checked = "checked" if vacation.get("enabled") else ""
    vacation_until = vacation.get("until", "")
    vacation_expired = False
    if vacation.get("enabled") and vacation_until:
        try:
            vacation_expired = date.fromisoformat(vacation_until) < date.today()
        except ValueError:
            vacation_expired = False
    vacation_state = (
        f' <span class="admin-badge">Pausiert bis {format_date_de(vacation_until)}</span>'
        if vacation_active and vacation_until else
        ' <span class="admin-badge">Pausiert</span>'
        if vacation_active else
        f' <span class="badge ok" style="font-size:0.68rem">Abgelaufen am {format_date_de(vacation_until)}</span>'
        if vacation_expired else ""
    )
    svc_info = (
        f'<div class="settings-help">{tr("settings.devices")}: {", ".join(escape(s) for s in services)}</div>'
        if services else
        f'<div class="settings-help">{tr("settings.no_devices")}</div>'
    )
    admin_b = f' <span class="admin-badge">Admin</span>' if pn in admins else ""
    role_label = tr(f"role.{role}") if role in ROLES else role
    device_count = len(services)
    open_attr = "" if show_admin_fields else " open"

    room_boxes = ""
    for r in areas:
        r_html = escape(r)
        r_attr = escape(r, quote=True)
        room_boxes += f"""
        <label class="settings-check">
          <input type="checkbox" name="hidden_rooms" value="{r_attr}"
                 {'checked' if r in hidden_rooms else ''}
          >
          <span>{r_html}</span>
        </label>"""

    admin_fields = ""
    if show_admin_fields:
        role_opts = "".join(
            f'<option value="{k}"{" selected" if k == role else ""}>{tr(f"role.{k}")}</option>'
            for k, v in ROLES.items()
        )
        admin_fields = f"""
        <div class="settings-block">
          <div class="settings-block-title">{tr("settings.role_visibility")}</div>
          <div class="grid-2">
            <div class="form-group">
              <label>{tr("settings.role")}</label>
              <select name="role">{role_opts}</select>
            </div>
            <div class="form-group settings-check-field">
              <label class="settings-check">
                <input type="checkbox" name="can_see_children" value="1"
                       {'checked' if can_see_children else ''}>
                <span>{tr("settings.can_see_children")}</span>
              </label>
            </div>
          </div>
        </div>"""

    return f"""
    <details class="card person-settings-card"{open_attr}>
      <summary class="person-settings-summary">
        <span class="person-settings-main">
          <span class="person-settings-title">{pn_html}{admin_b}{vacation_state}</span>
          <span class="person-settings-meta">{escape(role_label)} · {device_count} Gerät(e)</span>
        </span>
        <span class="person-settings-toggle">{tr("settings.edit")}</span>
      </summary>
      <form class="person-settings-form" method="post" action="{base}{action}">
        <input type="hidden" name="person" value="{pn_attr}">

        <div class="settings-block">
          <div class="settings-block-title">{tr("settings.notification")}</div>
          {svc_info}
          <div class="grid-2">
            <div class="form-group">
              <label>{tr("settings.notification_time")}</label>
              <input name="notify_time" type="time" value="{escape(time_val, quote=True)}">
            </div>
            <div class="form-group settings-check-field">
              <label class="settings-check">
                <input type="checkbox" name="enabled" value="1" {checked}>
                <span>{tr("common.active")}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="settings-block">
          <div class="settings-block-title">{tr("settings.display")}</div>
          <div class="form-group">
            <label>{tr("settings.language")}</label>
            <select name="language">{lang_opts}</select>
          </div>
        </div>

        <div class="settings-block">
          <div class="settings-block-title">{tr("settings.motivation")}</div>
          <div class="form-group">
            <label>{tr("settings.weekly_goal")}</label>
            <input name="weekly_goal" type="number" min="0" max="99" value="{weekly_goal}"
                   placeholder="{tr("settings.no_goal")}">
          </div>
        </div>

        <div class="settings-block">
          <div class="settings-block-title">{tr("settings.vacation")}</div>
          <div class="grid-2">
            <div class="form-group settings-check-field">
              <label class="settings-check">
                <input type="checkbox" name="vacation_enabled" value="1" {vacation_checked}>
                <span>{tr("settings.vacation_mode")}</span>
              </label>
            </div>
            <div class="form-group">
              <label>{tr("settings.vacation_until")}</label>
              <input type="date" name="vacation_until" value="{escape(vacation_until, quote=True)}">
            </div>
          </div>
        </div>

        {admin_fields}

        <div class="settings-block">
          <div class="settings-block-title">{tr("settings.hide_rooms")}</div>
          <div class="settings-room-list">{room_boxes}</div>
        </div>

        <div class="settings-actions">
          <button class="btn btn-primary btn-sm" type="submit">{tr("common.save")}</button>
          <a class="btn btn-ghost btn-sm" href="{base}notify-now/{pn_url}{person_suffix(pn)}">{tr("common.test")}</a>
        </div>
      </form>
    </details>"""
