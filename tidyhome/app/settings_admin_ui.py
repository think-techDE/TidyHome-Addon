from i18n import tr
from render import (_icon, ROOM_ICON_CHOICES, ROOM_ICON_LABELS,
                    _auto_room_icon_config)
from settings_ui import _person_settings_card
from storage import get_person_settings, get_room_icons


def admin_page_content(base: str, admins: set[str], persons: list[str],
                       areas: list[str], saved: str = "",
                       available_svcs: list[str] | None = None) -> str:
    available_svcs = available_svcs or []
    # ── Admin-Verwaltung ──────────────────────────────────────────────────
    person_cbs = ""
    for pn in persons:
        is_adm = pn in admins
        person_cbs += f"""
        <label style="display:flex;align-items:center;gap:0.75rem;
                       padding:0.65rem 0;border-bottom:1px solid var(--border);
                       cursor:pointer;font-size:0.9rem;font-weight:{'600' if is_adm else '400'}">
          <input type="checkbox" name="admins" value="{pn}"
                 {'checked' if is_adm else ''}
                 style="width:1.1rem;height:1.1rem;accent-color:var(--primary)">
          {pn}
          {'<span class="admin-badge" style="margin-left:0.25rem">Admin</span>' if is_adm else ''}
        </label>"""

    saved_banner = f"""
        <div style="background:var(--success-bg);color:var(--success);padding:0.6rem 0.875rem;
                    border-radius:0.6rem;margin-bottom:1rem;font-size:0.84rem;font-weight:600">
          {tr("settings.saved")}
        </div>""" if saved == "1" else ""

    admin_section = f"""
    <section id="admin-rights" class="card admin-section">
      <div class="admin-section-head">
        <div>
          <h3>{tr("settings.admin_rights")}</h3>
          <p class="muted">{tr("settings.admin_rights_hint")}</p>
        </div>
      </div>
      {saved_banner}
      <form method="post" action="{base}admin/admins">
        <div class="admin-list">{person_cbs}</div>
        <button class="btn btn-primary btn-sm admin-save" type="submit">{tr("settings.admin_rights_save")}</button>
      </form>
    </section>"""

    data_section = f"""
    <section id="admin-data" class="card admin-section">
      <div class="admin-section-head">
        <div>
          <h3>{tr("admin.data_diagnostics")}</h3>
          <p class="muted">{tr("settings.data_diagnostics_hint")}</p>
        </div>
      </div>
      <div class="admin-data-actions">
        <a class="btn btn-primary btn-sm" href="{base}admin/export.json">{_icon("download", 14, "white")} {tr("admin.backup_json")}</a>
        <a class="btn btn-ghost btn-sm" href="{base}admin/export/tasks.csv">{tr("admin.tasks_csv")}</a>
        <a class="btn btn-ghost btn-sm" href="{base}admin/export/projects.csv">{tr("admin.projects_csv")}</a>
        <a class="btn btn-ghost btn-sm" href="{base}admin/export/scores.csv">{tr("admin.scores_csv")}</a>
        <a class="btn btn-outline btn-sm" href="{base}admin/diagnostics">{_icon("alert", 14)} {tr("admin.open_diagnostics")}</a>
      </div>
    </section>"""

    # ── Geräte-Verwaltung ─────────────────────────────────────────────────
    if not admins:
        device_section = f"""
        <section id="admin-devices" class="card admin-section" style="background:var(--warning-bg);border:1px solid var(--warning)">
          <p style="color:var(--warning);margin:0;font-size:0.85rem">
            {tr("settings.no_admins_hint")}
          </p>
        </section>"""
    else:
        cards = ""
        for pn in persons:
            cfg = get_person_settings(pn)
            selected_svcs = set(cfg.get("services") or [])
            admin_b = f' <span class="admin-badge">Admin</span>' if pn in admins else ""

            if available_svcs:
                svc_cbs = ""
                for svc in available_svcs:
                    chk = "checked" if svc in selected_svcs else ""
                    short = svc.replace("notify.", "")
                    svc_cbs += f"""
                    <label style="display:flex;align-items:center;gap:0.6rem;
                                   padding:0.45rem 0;border-bottom:1px solid var(--border);
                                   cursor:pointer;font-size:0.85rem">
                      <input type="checkbox" name="services" value="{svc}" {chk}
                             style="width:1.1rem;height:1.1rem;accent-color:var(--primary)">
                      <span style="flex:1">{short}</span>
                      <span class="muted" style="font-size:0.72rem">{svc}</span>
                    </label>"""
                extra = ", ".join(s for s in selected_svcs if s not in available_svcs)
                extra_field = f"""
                <div class="form-group" style="margin-top:0.75rem">
                  <label>{tr("settings.extra_services")}</label>
                  <input name="extra_services" value="{extra}"
                         placeholder="notify.anderer_service">
                </div>"""
                svc_content = svc_cbs + extra_field
                hint = ""
            else:
                svc_val = ", ".join(selected_svcs)
                svc_content = f"""
                <div class="form-group">
                  <label>{tr("settings.notify_services")}</label>
                  <input name="extra_services" value="{svc_val}"
                         placeholder="notify.mobile_app_iphone, notify.alexa_kueche">
                </div>"""
                hint = f'<div class="muted" style="margin-bottom:0.75rem;font-size:0.78rem">{tr("settings.services_load_failed")}</div>'

            cards += f"""
            <details class="admin-details">
              <summary>
                <span>{pn}{admin_b}</span>
                <span class="muted">{len(selected_svcs)} {tr("settings.devices")}</span>
              </summary>
              <form method="post" action="{base}admin">
                <input type="hidden" name="person" value="{pn}">
                {hint if not available_svcs else ''}
                {svc_content}
                <button class="btn btn-primary btn-sm" style="margin-top:0.5rem" type="submit">{tr("common.save")}</button>
              </form>
            </details>"""
        device_section = f"""
        <section id="admin-devices" class="card admin-section">
          <div class="admin-section-head">
            <div>
              <h3>{tr("settings.notifications")}</h3>
              <p class="muted">{tr("settings.notifications_hint")}</p>
            </div>
          </div>
          <div class="admin-list">{cards}</div>
        </section>"""

    # ── Raum-Icons ────────────────────────────────────────────────────────
    stored_icons = get_room_icons()
    room_cards = ""
    for r in areas:
        current_key = stored_icons.get(r, "")
        safe_name = r.replace(" ", "_")

        # Preview bubble: use stored key or name-based fallback
        if current_key in ROOM_ICON_CHOICES:
            prev_img, prev_bg = ROOM_ICON_CHOICES[current_key]
        else:
            prev_img, prev_bg = _auto_room_icon_config(r)

        # Auto button
        auto_active = " ri-active" if not current_key else ""
        choices_html = (
            f'<button type="button" class="ri-choice{auto_active}" '
            f'data-key="" data-room="{safe_name}" title="Automatisch" '
            f'data-label="automatisch auto" '
            f'data-img="assets/icons/{prev_img}.svg" data-bg="{prev_bg}" '
            f'onclick="pickRoomIcon(this)">🔮</button>'
        )
        for key, (filename, bg) in ROOM_ICON_CHOICES.items():
            label = ROOM_ICON_LABELS.get(key, key)
            active = " ri-active" if key == current_key else ""
            choices_html += (
                f'<button type="button" class="ri-choice{active}" '
                f'data-key="{key}" data-room="{safe_name}" '
                f'data-label="{label.casefold()} {key}" '
                f'data-img="assets/icons/{filename}.svg" data-bg="{bg}" '
                f'title="{label}" onclick="pickRoomIcon(this)">'
                f'<img src="assets/icons/{filename}.svg" width="22" height="22" style="display:block">'
                f'</button>'
            )

        room_cards += f"""
        <div class="ri-card">
          <div class="ri-head">
            <div class="ri-preview" id="rip_{safe_name}"
                 style="width:48px;height:48px;border-radius:50%;background:{prev_bg};
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;overflow:hidden">
              <img id="ripimg_{safe_name}" src="assets/icons/{prev_img}.svg"
                   width="29" height="29" style="display:block" loading="lazy">
            </div>
            <span class="ri-name">{r}</span>
          </div>
          <div class="ri-choices">{choices_html}</div>
          <input type="hidden" name="icon__{safe_name}" id="riinput_{safe_name}" value="{current_key}">
        </div>"""

    ri_js = """<script>
function pickRoomIcon(btn){
  var room=btn.dataset.room;
  btn.closest('.ri-choices').querySelectorAll('.ri-choice')
    .forEach(function(b){b.classList.remove('ri-active')});
  btn.classList.add('ri-active');
  document.getElementById('riinput_'+room).value=btn.dataset.key||'';
  var preview=document.getElementById('rip_'+room);
  var img=document.getElementById('ripimg_'+room);
  if(btn.dataset.img){
    img.src=btn.dataset.img;
    preview.style.background=btn.dataset.bg||'var(--primary-soft)';
  }
}
function filterRoomIcons(input){
  var query=(input.value||'').trim().toLowerCase();
  document.querySelectorAll('.ri-choice').forEach(function(btn){
    var label=(btn.dataset.label||'').toLowerCase();
    btn.style.display=(!query || label.indexOf(query)!==-1) ? '' : 'none';
  });
}
</script>"""

    room_icons_section = f"""
    <section id="admin-room-icons" class="card admin-section">
      <h3 style="margin-bottom:0.25rem">{tr("settings.room_icons")}</h3>
      <p class="muted" style="margin-bottom:1rem;font-size:0.8rem">
        {tr("settings.room_icon_hint")}
      </p>
      <form method="post" action="{base}admin/room-icons">
        <div class="icon-filter"><input type="search" placeholder="{tr("settings.room_icon_search")}" oninput="filterRoomIcons(this)" autocomplete="off"></div>
        <div class="ri-grid">{room_cards}</div>
        <button class="btn btn-primary btn-sm admin-save" type="submit">{tr("common.save")}</button>
      </form>
      {ri_js}
    </section>"""

    # ── Personeneinstellungen (Benachrichtigungen + Räume) ────────────────────
    person_settings_cards = "".join(
        _person_settings_card(pn, areas, admins, base=base, action="settings",
                               show_admin_fields=True)
        for pn in persons
    )
    admin_count = len([pn for pn in persons if pn in admins])
    admin_overview = f"""
    <div class="admin-overview">
      <a class="admin-overview-card" href="#admin-rights">
        <strong>{admin_count}</strong><span>Admins</span>
      </a>
      <a class="admin-overview-card" href="#admin-room-icons">
        <strong>{len(areas)}</strong><span>{tr("dashboard.rooms")}</span>
      </a>
      <a class="admin-overview-card" href="#admin-devices">
        <strong>{len(persons)}</strong><span>{tr("settings.notifications")}</span>
      </a>
      <a class="admin-overview-card" href="#admin-people">
        <strong>{len(persons)}</strong><span>{tr("settings.profiles")}</span>
      </a>
      <a class="admin-overview-card" href="#admin-data">
        <strong>CSV</strong><span>{tr("settings.data")}</span>
      </a>
    </div>"""

    content = f"""
    <div class="admin-hero">
      <div>
        <h2>Admin</h2>
        <p class="muted">{tr("settings.admin_subtitle")}</p>
      </div>
      <span class="admin-badge">{len(persons)} {tr("settings.people")}</span>
    </div>
    {admin_overview}
    <div class="admin-stack">
      {admin_section}
      {data_section}
      {room_icons_section}
      {device_section}
      <section id="admin-people" class="admin-section">
        <div class="admin-section-head">
          <div>
            <h3>Personeneinstellungen</h3>
            <p class="muted">Rollen, Ziele, Räume und Test-Benachrichtigungen pro Person.</p>
          </div>
        </div>
        <div class="admin-person-grid">{person_settings_cards}</div>
      </section>
    </div>"""
    return content
