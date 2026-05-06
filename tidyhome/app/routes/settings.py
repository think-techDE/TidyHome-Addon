from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from config import ADMINS
from ha_client import get_persons
from render import _base, render
from scheduler import notify_person_now, parse_time
from storage import get_person_settings, list_person_settings, save_person_settings

router = APIRouter()


@router.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request, p: str = ""):
    persons = await get_persons()
    cards = ""
    for pn in persons:
        cfg = get_person_settings(pn)
        time_val = cfg.get("notify_time", "08:00")
        checked = "checked" if cfg.get("enabled") else ""
        services = cfg.get("services") or []
        svc_info = (
            f'<div class="muted" style="margin-bottom:0.75rem">Geräte: {", ".join(services)}</div>'
            if services else
            '<div class="muted" style="margin-bottom:0.75rem">Keine Geräte (Admin konfiguriert diese)</div>'
        )
        admin_b = f' <span class="admin-badge">Admin</span>' if pn in ADMINS else ""
        cards += f"""
        <div class="card" style="margin-bottom:0.75rem">
          <form method="post" action="settings">
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
                  <input type="checkbox" name="enabled" value="1" {checked}
                         style="width:auto">
                  Aktiv
                </label>
              </div>
            </div>
            <div style="display:flex;gap:0.5rem">
              <button class="btn btn-primary btn-sm" type="submit">Speichern</button>
              <a class="btn btn-ghost btn-sm" href="notify-now/{pn}">🔔 Testen</a>
            </div>
          </form>
        </div>"""
    content = f"<h2>Einstellungen</h2>{cards}"
    return render(content, request, page="settings", person=p)


@router.post("/settings")
async def settings_save(request: Request, person: str = Form(...),
                         notify_time: str = Form("08:00"), enabled: str = Form("")):
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=cfg.get("services") or [],
                         notify_time=parse_time(notify_time), enabled=(enabled == "1"))
    return RedirectResponse(_base(request) + "settings", status_code=303)


@router.get("/admin", response_class=HTMLResponse)
async def admin_form(request: Request):
    if not ADMINS:
        content = """
        <h2>Admin</h2>
        <div class="card" style="background:var(--danger-bg);border:1px solid var(--danger)">
          <p style="color:var(--danger);margin:0">
            Keine Admins konfiguriert. Trage in der Add-on-Konfiguration unter
            <strong>admins</strong> die Personen ein (kommagetrennt).
          </p>
        </div>"""
        return render(content, request)

    persons = await get_persons()
    info = """<div class="info-box">
      <strong>Services finden:</strong> HA → Entwicklerwerkzeuge → Dienste → nach
      <code>notify.</code> suchen. Mehrere kommagetrennt eingeben.
    </div>"""
    cards = ""
    for pn in persons:
        cfg = get_person_settings(pn)
        svc_val = ", ".join(cfg.get("services") or [])
        admin_b = f' <span class="admin-badge">Admin</span>' if pn in ADMINS else ""
        cards += f"""
        <div class="card" style="margin-bottom:0.75rem">
          <form method="post" action="admin">
            <input type="hidden" name="person" value="{pn}">
            <div style="font-weight:700;margin-bottom:0.75rem">{pn}{admin_b}</div>
            <div class="form-group">
              <label>Notify-Services</label>
              <input name="services" value="{svc_val}"
                     placeholder="notify.mobile_app_iphone, notify.alexa_kueche">
            </div>
            <button class="btn btn-primary btn-sm" type="submit">Speichern</button>
          </form>
        </div>"""
    admin_list = ", ".join(sorted(ADMINS))
    footer = f'<div class="muted" style="margin-top:0.5rem">Admins: {admin_list} · änderbar in der Add-on-Konfiguration</div>'
    content = f"<h2>Admin — Geräteverwaltung</h2>{info}{cards}{footer}"
    return render(content, request)


@router.post("/admin")
async def admin_save(request: Request, person: str = Form(...), services: str = Form("")):
    if not ADMINS:
        raise HTTPException(403)
    svc_list = [s.strip() for s in services.split(",") if s.strip()]
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=svc_list,
                         notify_time=cfg.get("notify_time", "08:00"),
                         enabled=cfg.get("enabled", False))
    return RedirectResponse(_base(request) + "admin", status_code=303)


@router.get("/notify-now/{person}")
async def notify_now(person: str, request: Request):
    await notify_person_now(person)
    return RedirectResponse(_base(request) + "settings", status_code=303)
