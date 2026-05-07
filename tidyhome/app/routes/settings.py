from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_notify_services, get_persons
from render import _base, render
from scheduler import notify_person_now, parse_time
from storage import (get_admins, get_person_settings, list_person_settings,
                     save_admins, save_person_settings)

router = APIRouter()


def _person_settings_card(pn: str, areas: list[str], admins: set[str],
                           action: str = "settings") -> str:
    """HTML-Karte für die Einstellungen einer einzelnen Person."""
    cfg = get_person_settings(pn)
    time_val = cfg.get("notify_time", "08:00")
    checked = "checked" if cfg.get("enabled") else ""
    services = cfg.get("services") or []
    hidden_rooms = set(cfg.get("hidden_rooms") or [])
    weekly_goal = cfg.get("weekly_goal", 0) or 0
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

    return f"""
    <div class="card" style="margin-bottom:0.75rem">
      <form method="post" action="{action}">
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
        <div class="grid-2">
          <div class="form-group">
            <label>Wochenziel (Aufgaben)</label>
            <input name="weekly_goal" type="number" min="0" max="99" value="{weekly_goal}"
                   placeholder="0 = kein Ziel">
          </div>
        </div>
        <div class="form-group">
          <label>Räume ausblenden</label>
          <div style="display:flex;flex-wrap:wrap;gap:0 1.5rem">{room_boxes}</div>
        </div>
        <div style="display:flex;gap:0.5rem">
          <button class="btn btn-primary btn-sm" type="submit">Speichern</button>
          <a class="btn btn-ghost btn-sm" href="notify-now/{pn}">🔔 Testen</a>
        </div>
      </form>
    </div>"""


@router.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request, p: str = ""):
    admins = get_admins()
    areas = await get_areas()

    if not p:
        content = """
        <h2>Einstellungen</h2>
        <div class="card">
          <div class="muted">Wähle zuerst eine Person über das Menü aus.</div>
        </div>"""
        return render(content, request, page="settings", person=p)

    card = _person_settings_card(p, areas, admins, action="settings")
    content = f"<h2>Einstellungen</h2>{card}"
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
    save_person_settings(person=person, services=cfg.get("services") or [],
                         notify_time=notify_time, enabled=enabled,
                         hidden_rooms=hidden_rooms, weekly_goal=weekly_goal)
    return RedirectResponse(_base(request) + "settings", status_code=303)


@router.get("/admin", response_class=HTMLResponse)
async def admin_form(request: Request, saved: str = ""):
    admins = get_admins()
    persons = await get_persons()

    # ── Admin-Verwaltung ──────────────────────────────────────────────────
    checkboxes = ""
    for pn in persons:
        is_admin = pn in admins
        checkboxes += f"""
        <label style="display:flex;align-items:center;gap:0.75rem;
                       padding:0.65rem 0;border-bottom:1px solid var(--border);
                       cursor:pointer;font-size:0.9rem;font-weight:{'600' if is_admin else '400'}">
          <input type="checkbox" name="admins" value="{pn}"
                 {'checked' if is_admin else ''}
                 style="width:1.1rem;height:1.1rem;accent-color:var(--primary)">
          {pn}
          {'<span class="admin-badge" style="margin-left:0.25rem">Admin</span>' if is_admin else ''}
        </label>"""

    saved_banner = """
        <div style="background:var(--success-bg);color:var(--success);padding:0.6rem 0.875rem;
                    border-radius:0.6rem;margin-bottom:1rem;font-size:0.84rem;font-weight:600">
          ✓ Admin-Einstellungen gespeichert
        </div>""" if saved == "1" else ""

    admin_section = f"""
    <div class="card" style="margin-bottom:1rem">
      <h3 style="margin-bottom:0.75rem">Admin-Rechte vergeben</h3>
      {saved_banner}
      <form method="post" action="admin/admins">
        <div style="margin-bottom:1rem">{checkboxes}</div>
        <button class="btn btn-primary btn-sm" type="submit">Speichern</button>
      </form>
    </div>"""

    # ── Geräte-Verwaltung ─────────────────────────────────────────────────
    if not admins:
        device_section = """
        <div class="card" style="background:var(--warning-bg);border:1px solid var(--warning)">
          <p style="color:var(--warning);margin:0;font-size:0.85rem">
            Noch keine Admins festgelegt. Wähle oben mindestens eine Person aus.
          </p>
        </div>"""
    else:
        available_svcs = await get_notify_services()
        cards = ""
        for pn in persons:
            cfg = get_person_settings(pn)
            selected_svcs = set(cfg.get("services") or [])
            admin_b = f' <span class="admin-badge">Admin</span>' if pn in admins else ""

            if available_svcs:
                # Checkboxen für alle bekannten Services
                checkboxes = ""
                for svc in available_svcs:
                    checked = "checked" if svc in selected_svcs else ""
                    short = svc.replace("notify.", "")
                    checkboxes += f"""
                    <label style="display:flex;align-items:center;gap:0.6rem;
                                   padding:0.45rem 0;border-bottom:1px solid var(--border);
                                   cursor:pointer;font-size:0.85rem">
                      <input type="checkbox" name="services" value="{svc}" {checked}
                             style="width:1.1rem;height:1.1rem;accent-color:var(--primary)">
                      <span style="flex:1">{short}</span>
                      <span class="muted" style="font-size:0.72rem">{svc}</span>
                    </label>"""
                # Manuelles Zusatzfeld für nicht erkannte Services
                extra = ", ".join(s for s in selected_svcs if s not in available_svcs)
                extra_field = f"""
                <div class="form-group" style="margin-top:0.75rem">
                  <label>Weitere Services (manuell)</label>
                  <input name="extra_services" value="{extra}"
                         placeholder="notify.anderer_service">
                </div>"""
                svc_content = checkboxes + extra_field
                hint = ""
            else:
                # Fallback: Freitext wenn HA keine Services liefert
                svc_val = ", ".join(selected_svcs)
                svc_content = f"""
                <div class="form-group">
                  <label>Notify-Services</label>
                  <input name="extra_services" value="{svc_val}"
                         placeholder="notify.mobile_app_iphone, notify.alexa_kueche">
                </div>"""
                hint = '<div class="muted" style="margin-bottom:0.75rem;font-size:0.78rem">HA-Services konnten nicht geladen werden – bitte manuell eintragen.</div>'

            cards += f"""
            <div class="card" style="margin-bottom:0.75rem">
              <form method="post" action="admin">
                <input type="hidden" name="person" value="{pn}">
                <div style="font-weight:700;margin-bottom:0.75rem">{pn}{admin_b}</div>
                {hint if not available_svcs else ''}
                {svc_content}
                <button class="btn btn-primary btn-sm" style="margin-top:0.5rem" type="submit">Speichern</button>
              </form>
            </div>"""
        device_section = cards

    # ── Personeneinstellungen (Benachrichtigungen + Räume) ────────────────────
    areas = await get_areas()
    person_settings_cards = "".join(
        _person_settings_card(pn, areas, admins, action="settings")
        for pn in persons
    )

    content = (
        f"<h2>Admin</h2>{admin_section}"
        f"<h2 style='margin-bottom:0.75rem'>Geräte-Verwaltung</h2>{device_section}"
        f"<h2 style='margin-bottom:0.75rem;margin-top:1rem'>Personeneinstellungen</h2>"
        f"{person_settings_cards}"
    )
    return render(content, request)


@router.post("/admin/admins")
async def admin_save_admins(request: Request):
    form = await request.form()
    selected = form.getlist("admins")
    save_admins(selected)
    return RedirectResponse(_base(request) + "admin?saved=1", status_code=303)


@router.post("/admin")
async def admin_save_devices(request: Request):
    if not get_admins():
        raise HTTPException(403)
    form = await request.form()
    person = form.get("person", "")
    # Checkboxen (mehrere Werte mit gleichem Key)
    checked = list(form.getlist("services"))
    # Manuelles Zusatzfeld
    extra = [s.strip() for s in form.get("extra_services", "").split(",") if s.strip()]
    svc_list = sorted(set(checked + extra))
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=svc_list,
                         notify_time=cfg.get("notify_time", "08:00"),
                         enabled=cfg.get("enabled", False))
    return RedirectResponse(_base(request) + "admin", status_code=303)


@router.get("/notify-now/{person}")
async def notify_now(person: str, request: Request):
    await notify_person_now(person)
    return RedirectResponse(_base(request) + "settings", status_code=303)
