from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_notify_services, get_persons
from render import (_base, _ha_user, _ICON_LABELS, ROOM_ICON_CHOICES, ROOM_ICON_LABELS,
                    _auto_room_icon_config, _room_icon, person_suffix, render)
from scheduler import notify_person_now, parse_time
from storage import (ROLES, get_admins, get_person_settings, get_room_icons,
                     get_vacation_mode, is_vacation_mode_active, list_person_settings,
                     save_admins, save_person_settings, save_room_icons,
                     save_vacation_mode)

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
    svc_info = (
        f'<div class="muted" style="margin-bottom:0.75rem">Geräte: {", ".join(services)}</div>'
        if services else
        '<div class="muted" style="margin-bottom:0.75rem">Keine Geräte (Admin konfiguriert diese)</div>'
    )
    admin_b = f' <span class="admin-badge">Admin</span>' if pn in admins else ""

    room_boxes = ""
    for r in areas:
        room_boxes += f"""
        <label style="display:flex;align-items:center;gap:0.5rem;
                       padding:0.3rem 0;cursor:pointer;font-size:0.84rem">
          <input type="checkbox" name="hidden_rooms" value="{r}"
                 {'checked' if r in hidden_rooms else ''}
                 style="width:1rem;height:1rem;accent-color:var(--primary)">
          {r}
        </label>"""

    admin_fields = ""
    if show_admin_fields:
        role_opts = "".join(
            f'<option value="{k}"{" selected" if k == role else ""}>{v}</option>'
            for k, v in ROLES.items()
        )
        admin_fields = f"""
        <div class="grid-2" style="margin-top:0.5rem">
          <div class="form-group">
            <label>Rolle</label>
            <select name="role">{role_opts}</select>
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;padding-bottom:0.75rem">
            <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;
                          text-transform:none;font-size:0.84rem;letter-spacing:0;font-weight:500;margin:0">
              <input type="checkbox" name="can_see_children" value="1"
                     {'checked' if can_see_children else ''}
                     style="width:1rem;height:1rem;accent-color:var(--primary)">
              Kinder sehen
            </label>
          </div>
        </div>"""

    return f"""
    <div class="card" style="margin-bottom:0.75rem">
      <form method="post" action="{base}{action}">
        <input type="hidden" name="person" value="{pn}">
        <div style="font-weight:700;margin-bottom:0.5rem">{pn}{admin_b}</div>
        {svc_info}
        <div class="grid-2">
          <div class="form-group">
            <label>Benachrichtigungszeit</label>
            <input name="notify_time" type="time" value="{time_val}">
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;padding-bottom:0.1rem">
            <label style="display:flex;align-items:center;gap:0.5rem;
                          cursor:pointer;text-transform:none;font-size:0.85rem;letter-spacing:0;margin:0">
              <input type="checkbox" name="enabled" value="1" {checked} style="width:auto">
              Aktiv
            </label>
          </div>
        </div>
        <div class="form-group">
          <label>Wochenziel (Aufgaben)</label>
          <input name="weekly_goal" type="number" min="0" max="99" value="{weekly_goal}"
                 placeholder="0 = kein Ziel">
        </div>
        {admin_fields}
        <div class="form-group">
          <label>Räume ausblenden</label>
          <div style="display:flex;flex-wrap:wrap;gap:0 1.5rem">{room_boxes}</div>
        </div>
        <div style="display:flex;gap:0.5rem">
          <button class="btn btn-primary btn-sm" type="submit">Speichern</button>
          <a class="btn btn-ghost btn-sm" href="{base}notify-now/{pn}{person_suffix(pn)}">Testen</a>
        </div>
      </form>
    </div>"""


@router.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request, p: str = ""):
    base = _base(request)
    admins = get_admins()
    areas = await get_areas()

    # HA-User aus Header bestimmen
    ha_user = _ha_user(request)
    is_admin = ha_user in admins

    admin_link = (
        f'<a href="{base}admin" class="btn btn-primary btn-sm" '
        f'style="margin-bottom:1rem">Admin-Bereich öffnen</a>'
        if is_admin else ""
    )

    if not p:
        if is_admin:
            # Admin ohne ?p= → Personenpicker anzeigen
            persons = await get_persons()
            pills = "".join(
                f'<a href="{base}settings?p={pn}" class="btn btn-ghost btn-sm" '
                f'style="font-size:0.9rem;padding:0.5rem 1.1rem">{pn}</a>'
                for pn in persons
            )
            own_controls = (
                f'<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem">'
                f'<a href="{base}" class="btn btn-primary btn-sm">Zurück zu mir</a>'
                f'<a href="{base}settings{person_suffix(ha_user)}" class="btn btn-ghost btn-sm">Mein Profil</a>'
                f'</div>'
                if ha_user else ""
            )
            content = f"""
            <h2>Einstellungen</h2>
            {admin_link}
            <h3 style="margin-bottom:0.5rem">Person wechseln</h3>
            <div class="card">
              <p class="muted" style="margin-bottom:1rem">
                Als Admin kannst du die Ansicht für jede Person öffnen.
              </p>
              {own_controls}
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem">{pills}</div>
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
            f'<a href="{base}settings?p={pn}" class="btn btn-ghost btn-sm" '
            f'style="font-size:0.9rem;padding:0.5rem 1.1rem">{pn}</a>'
            for pn in persons
        )
        content = f"""
        <h2>Wer bist du?</h2>
        <div class="card">
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem">{pills}</div>
        </div>"""
        return render(content, request, page="settings", person="")

    card = _person_settings_card(p, areas, admins, base=base, action="settings")
    content = f"<h2>Einstellungen</h2>{admin_link}{card}"
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
    role = form.get("role", "member")
    if role not in ROLES:
        role = "member"
    can_see_children = form.get("can_see_children", "") == "1"
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=cfg.get("services") or [],
                         notify_time=notify_time, enabled=enabled,
                         hidden_rooms=hidden_rooms, weekly_goal=weekly_goal,
                         role=role, can_see_children=can_see_children)
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
    <section class="card admin-section">
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

    vacation = get_vacation_mode()
    vacation_active = is_vacation_mode_active()
    vacation_checked = "checked" if vacation.get("enabled") else ""
    vacation_until = vacation.get("until", "")
    vacation_state = (
        '<span class="admin-badge">Aktiv</span>'
        if vacation_active else
        '<span class="badge ok" style="font-size:0.68rem">Inaktiv</span>'
    )
    vacation_section = f"""
    <section class="card admin-section">
      <div class="admin-section-head">
        <div>
          <h3>Urlaubsmodus</h3>
          <p class="muted">Pausiert fällige Aufgaben und tägliche Benachrichtigungen global.</p>
        </div>
        {vacation_state}
      </div>
      <form method="post" action="{base}admin/vacation">
        <div class="grid-2">
          <div class="form-group" style="display:flex;align-items:flex-end;padding-bottom:0.75rem">
            <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;
                          text-transform:none;font-size:0.84rem;letter-spacing:0;font-weight:500;margin:0">
              <input type="checkbox" name="enabled" value="1" {vacation_checked}
                     style="width:1rem;height:1rem;accent-color:var(--primary)">
              Aktiv
            </label>
          </div>
          <div class="form-group">
            <label>Bis einschließlich</label>
            <input type="date" name="until" value="{vacation_until}">
          </div>
        </div>
        <button class="btn btn-primary btn-sm admin-save" type="submit">Urlaubsmodus speichern</button>
      </form>
    </section>"""

    # ── Geräte-Verwaltung ─────────────────────────────────────────────────
    if not admins:
        device_section = """
        <section class="card admin-section" style="background:var(--warning-bg);border:1px solid var(--warning)">
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
        <section class="card admin-section">
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
    <section class="card admin-section">
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

    content = f"""
    <div class="admin-hero">
      <div>
        <h2>Admin</h2>
        <p class="muted">Rechte, Räume, Benachrichtigungen und Personen an einem Ort.</p>
      </div>
      <span class="admin-badge">{len(persons)} Personen</span>
    </div>
    <div class="admin-stack">
      {admin_section}
      {vacation_section}
      {room_icons_section}
      {device_section}
      <section class="admin-section">
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


@router.post("/admin/vacation")
async def admin_save_vacation(request: Request):
    if not get_admins():
        raise HTTPException(403)
    form = await request.form()
    save_vacation_mode(
        enabled=(form.get("enabled", "") == "1"),
        until=str(form.get("until") or ""),
    )
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
                         enabled=cfg.get("enabled", False))
    return RedirectResponse(_base(request) + "admin?saved=1", status_code=303)


@router.get("/notify-now/{person}")
async def notify_now(person: str, request: Request, p: str = ""):
    await notify_person_now(person)
    return RedirectResponse(_base(request) + f"settings{person_suffix(p or person)}", status_code=303)
