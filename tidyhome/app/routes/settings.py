from datetime import date
from html import escape
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_notify_services, get_persons
from render import (_base, _ha_user, _ICON_LABELS, ROOM_ICON_CHOICES, ROOM_ICON_LABELS,
                    _auto_room_icon_config, _room_icon, format_date_de,
                    person_suffix, render)
from scheduler import notify_person_now, parse_time
from storage import (ROLES, get_admins, get_person_settings, get_room_icons,
                     get_vacation_mode, is_vacation_mode_active, list_person_settings,
                     save_admins, save_person_settings, save_room_icons)

router = APIRouter()


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
        f'<div class="settings-help">Geräte: {", ".join(escape(s) for s in services)}</div>'
        if services else
        '<div class="settings-help">Keine Geräte hinterlegt. Das konfiguriert der Admin-Bereich.</div>'
    )
    admin_b = f' <span class="admin-badge">Admin</span>' if pn in admins else ""
    role_label = ROLES.get(role, role)
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
            f'<option value="{k}"{" selected" if k == role else ""}>{v}</option>'
            for k, v in ROLES.items()
        )
        admin_fields = f"""
        <div class="settings-block">
          <div class="settings-block-title">Rolle und Sicht</div>
          <div class="grid-2">
            <div class="form-group">
              <label>Rolle</label>
              <select name="role">{role_opts}</select>
            </div>
            <div class="form-group settings-check-field">
              <label class="settings-check">
                <input type="checkbox" name="can_see_children" value="1"
                       {'checked' if can_see_children else ''}>
                <span>Kinder sehen</span>
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
        <span class="person-settings-toggle">Bearbeiten</span>
      </summary>
      <form class="person-settings-form" method="post" action="{base}{action}">
        <input type="hidden" name="person" value="{pn_attr}">

        <div class="settings-block">
          <div class="settings-block-title">Benachrichtigung</div>
          {svc_info}
          <div class="grid-2">
            <div class="form-group">
              <label>Benachrichtigungszeit</label>
              <input name="notify_time" type="time" value="{escape(time_val, quote=True)}">
            </div>
            <div class="form-group settings-check-field">
              <label class="settings-check">
                <input type="checkbox" name="enabled" value="1" {checked}>
                <span>Aktiv</span>
              </label>
            </div>
          </div>
        </div>

        <div class="settings-block">
          <div class="settings-block-title">Motivation</div>
          <div class="form-group">
            <label>Wochenziel (Aufgaben)</label>
            <input name="weekly_goal" type="number" min="0" max="99" value="{weekly_goal}"
                   placeholder="0 = kein Ziel">
          </div>
        </div>

        <div class="settings-block">
          <div class="settings-block-title">Urlaub</div>
          <div class="grid-2">
            <div class="form-group settings-check-field">
              <label class="settings-check">
                <input type="checkbox" name="vacation_enabled" value="1" {vacation_checked}>
                <span>Urlaubsmodus</span>
              </label>
            </div>
            <div class="form-group">
              <label>Urlaub bis einschließlich</label>
              <input type="date" name="vacation_until" value="{escape(vacation_until, quote=True)}">
            </div>
          </div>
        </div>

        {admin_fields}

        <div class="settings-block">
          <div class="settings-block-title">Räume ausblenden</div>
          <div class="settings-room-list">{room_boxes}</div>
        </div>

        <div class="settings-actions">
          <button class="btn btn-primary btn-sm" type="submit">Speichern</button>
          <a class="btn btn-ghost btn-sm" href="{base}notify-now/{pn_url}{person_suffix(pn)}">Testen</a>
        </div>
      </form>
    </details>"""


@router.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request, p: str = ""):
    base = _base(request)
    admins = get_admins()
    areas = await get_areas()

    # HA-User aus Header bestimmen
    ha_user = _ha_user(request)
    is_admin = ha_user in admins

    admin_link = (
        f'<a href="{base}admin" class="btn btn-primary btn-sm">Admin-Bereich öffnen</a>'
        if is_admin else ""
    )

    if not p:
        if is_admin:
            # Admin ohne ?p= → Personenpicker anzeigen
            persons = await get_persons()
            pills = "".join(
                f'<a href="{base}settings?p={quote(pn, safe="")}" class="settings-person-tile">'
                f'<span>{escape(pn)}</span><small>Einstellungen öffnen</small></a>'
                for pn in persons
            )
            own_controls = (
                f'<div class="settings-actions" style="margin-bottom:0.75rem">'
                f'<a href="{base}" class="btn btn-primary btn-sm">Zurück zu mir</a>'
                f'<a href="{base}settings{person_suffix(ha_user)}" class="btn btn-ghost btn-sm">Mein Profil</a>'
                f'</div>'
                if ha_user else ""
            )
            content = f"""
            <div class="hero-card page-hero">
              <div>
                <div class="hero-eyebrow">Profile und Ansicht</div>
                <div class="hero-title">Einstellungen</div>
              </div>
              <div class="page-hero-actions">{admin_link}</div>
            </div>
            <div class="card settings-picker-card">
              <div class="settings-picker-head">
                <div>
                  <h3>Person wechseln</h3>
                  <p class="muted">Als Admin kannst du Profile gezielt öffnen.</p>
                </div>
              </div>
              {own_controls}
              <div class="settings-person-grid">{pills}</div>
            </div>"""
            return render(content, request, page="settings", person=ha_user)
        else:
            # Kein Admin, kein p → eigene Person aus HA-Header
            p = ha_user
    else:
        # p angegeben aber kein Admin → immer eigene Person
        if not is_admin:
            p = ha_user or p

    if not p:
        # Fallback: kein HA-Header und kein p (lokale Entwicklung)
        persons = await get_persons()
        pills = "".join(
            f'<a href="{base}settings?p={quote(pn, safe="")}" class="btn btn-ghost btn-sm" '
            f'style="font-size:0.9rem;padding:0.5rem 1.1rem">{escape(pn)}</a>'
            for pn in persons
        )
        content = f"""
        <h2>Wer bist du?</h2>
        <div class="card">
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem">{pills}</div>
        </div>"""
        return render(content, request, page="settings", person="")

    card = _person_settings_card(p, areas, admins, base=base, action="settings")
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">Profil und Benachrichtigung</div>
        <div class="hero-title">Einstellungen</div>
      </div>
      <div class="page-hero-actions">{admin_link}</div>
    </div>
    {card}"""
    return render(content, request, page="settings", person=p)


@router.post("/settings")
async def settings_save(request: Request):
    form = await request.form()
    person = form.get("person", "")
    notify_time = parse_time(form.get("notify_time", "08:00"))
    enabled = form.get("enabled", "") == "1"
    hidden_rooms = list(form.getlist("hidden_rooms"))
    try:
        weekly_goal = int(form.get("weekly_goal", 0) or 0)
    except ValueError:
        weekly_goal = 0
    cfg = get_person_settings(person)
    role = form.get("role", cfg.get("role", "member"))
    if role not in ROLES:
        role = "member"
    can_see_children = (
        form.get("can_see_children", "") == "1"
        if "can_see_children" in form else
        cfg.get("can_see_children", False)
    )
    vacation_enabled = form.get("vacation_enabled", "") == "1"
    vacation_until = str(form.get("vacation_until") or "")
    save_person_settings(person=person, services=cfg.get("services") or [],
                         notify_time=notify_time, enabled=enabled,
                         hidden_rooms=hidden_rooms, weekly_goal=weekly_goal,
                         role=role, can_see_children=can_see_children,
                         vacation_enabled=vacation_enabled,
                         vacation_until=vacation_until)
    return RedirectResponse(_base(request) + f"settings{person_suffix(person)}", status_code=303)


@router.get("/admin", response_class=HTMLResponse)
async def admin_form(request: Request, saved: str = ""):
    base = _base(request)
    admins = get_admins()
    persons = await get_persons()
    areas = await get_areas()

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

    saved_banner = """
        <div style="background:var(--success-bg);color:var(--success);padding:0.6rem 0.875rem;
                    border-radius:0.6rem;margin-bottom:1rem;font-size:0.84rem;font-weight:600">
          Gespeichert
        </div>""" if saved == "1" else ""

    admin_section = f"""
    <section id="admin-rights" class="card admin-section">
      <div class="admin-section-head">
        <div>
          <h3>Admin-Rechte</h3>
          <p class="muted">Wer den Admin-Bereich öffnen und Ansichten wechseln darf.</p>
        </div>
      </div>
      {saved_banner}
      <form method="post" action="{base}admin/admins">
        <div class="admin-list">{person_cbs}</div>
        <button class="btn btn-primary btn-sm admin-save" type="submit">Admin-Rechte speichern</button>
      </form>
    </section>"""

    # ── Geräte-Verwaltung ─────────────────────────────────────────────────
    if not admins:
        device_section = """
        <section id="admin-devices" class="card admin-section" style="background:var(--warning-bg);border:1px solid var(--warning)">
          <p style="color:var(--warning);margin:0;font-size:0.85rem">
            Noch keine Admins festgelegt. Wähle oben mindestens eine Person aus.
          </p>
        </section>"""
    else:
        available_svcs = await get_notify_services()
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
                  <label>Weitere Services (manuell)</label>
                  <input name="extra_services" value="{extra}"
                         placeholder="notify.anderer_service">
                </div>"""
                svc_content = svc_cbs + extra_field
                hint = ""
            else:
                svc_val = ", ".join(selected_svcs)
                svc_content = f"""
                <div class="form-group">
                  <label>Notify-Services</label>
                  <input name="extra_services" value="{svc_val}"
                         placeholder="notify.mobile_app_iphone, notify.alexa_kueche">
                </div>"""
                hint = '<div class="muted" style="margin-bottom:0.75rem;font-size:0.78rem">HA-Services konnten nicht geladen werden – bitte manuell eintragen.</div>'

            cards += f"""
            <details class="admin-details">
              <summary>
                <span>{pn}{admin_b}</span>
                <span class="muted">{len(selected_svcs)} Gerät(e)</span>
              </summary>
              <form method="post" action="{base}admin">
                <input type="hidden" name="person" value="{pn}">
                {hint if not available_svcs else ''}
                {svc_content}
                <button class="btn btn-primary btn-sm" style="margin-top:0.5rem" type="submit">Speichern</button>
              </form>
            </details>"""
        device_section = f"""
        <section id="admin-devices" class="card admin-section">
          <div class="admin-section-head">
            <div>
              <h3>Benachrichtigungen</h3>
              <p class="muted">Notify-Geräte pro Person verwalten.</p>
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
        preview_icon = _room_icon(r, 48, stored_icons)
        # Data attrs for live preview update
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
      <h3 style="margin-bottom:0.25rem">Raum-Icons</h3>
      <p class="muted" style="margin-bottom:1rem;font-size:0.8rem">
        Klicke ein Symbol an – 🔮 nutzt automatisch den Raumnamen.
      </p>
      <form method="post" action="{base}admin/room-icons">
        <div class="icon-filter"><input type="search" placeholder="Raum-Icon suchen" oninput="filterRoomIcons(this)" autocomplete="off"></div>
        <div class="ri-grid">{room_cards}</div>
        <button class="btn btn-primary btn-sm admin-save" type="submit">Speichern</button>
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
        <strong>{len(areas)}</strong><span>Räume</span>
      </a>
      <a class="admin-overview-card" href="#admin-devices">
        <strong>{len(persons)}</strong><span>Benachrichtigungen</span>
      </a>
      <a class="admin-overview-card" href="#admin-people">
        <strong>{len(persons)}</strong><span>Profile</span>
      </a>
    </div>"""

    content = f"""
    <div class="admin-hero">
      <div>
        <h2>Admin</h2>
        <p class="muted">Rechte, Räume, Benachrichtigungen und Personen an einem Ort.</p>
      </div>
      <span class="admin-badge">{len(persons)} Personen</span>
    </div>
    {admin_overview}
    <div class="admin-stack">
      {admin_section}
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

    # Admin-Person aus Header für die Nav-Pill
    ha_user = _ha_user(request)
    return render(content, request, page="settings", person=ha_user)


@router.post("/admin/admins")
async def admin_save_admins(request: Request):
    form = await request.form()
    selected = form.getlist("admins")
    save_admins(selected)
    return RedirectResponse(_base(request) + "admin?saved=1", status_code=303)


@router.post("/admin/room-icons")
async def admin_save_room_icons(request: Request):
    if not get_admins():
        raise HTTPException(403)
    form = await request.form()
    icons: dict[str, str] = {}
    for key, value in form.multi_items():
        if key.startswith("icon__") and value:
            room = key[6:].replace("_", " ")  # strip prefix, restore spaces
            icons[room] = value
    save_room_icons(icons)
    return RedirectResponse(_base(request) + "admin?saved=1", status_code=303)


@router.post("/admin")
async def admin_save_devices(request: Request):
    if not get_admins():
        raise HTTPException(403)
    form = await request.form()
    person = form.get("person", "")
    checked = list(form.getlist("services"))
    extra = [s.strip() for s in form.get("extra_services", "").split(",") if s.strip()]
    svc_list = sorted(set(checked + extra))
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=svc_list,
                         notify_time=cfg.get("notify_time", "08:00"),
                         enabled=cfg.get("enabled", False),
                         hidden_rooms=cfg.get("hidden_rooms") or [],
                         weekly_goal=cfg.get("weekly_goal", 0) or 0,
                         role=cfg.get("role", "member"),
                         can_see_children=cfg.get("can_see_children", False),
                         vacation_enabled=cfg.get("vacation_enabled", False),
                         vacation_until=cfg.get("vacation_until", ""))
    return RedirectResponse(_base(request) + "admin?saved=1", status_code=303)


@router.get("/notify-now/{person}")
async def notify_now(person: str, request: Request, p: str = ""):
    await notify_person_now(person)
    return RedirectResponse(_base(request) + f"settings{person_suffix(p or person)}", status_code=303)
