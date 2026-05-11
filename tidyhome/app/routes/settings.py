from html import escape
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ha_client import get_areas, get_notify_services, get_persons
from i18n import normalize_language, tr
from render import (_base, _ha_user, _icon, person_suffix, render)
from scheduler import notify_person_now, parse_time
from settings_admin_ui import admin_page_content
from settings_exports import _csv_response, json_backup_response
from settings_ui import _person_settings_card
from storage import (ROLES, diagnose_data, export_backup_data, get_admins,
                     get_person_settings, list_person_settings, project_export_rows,
                     save_admins, save_person_settings, save_room_icons,
                     score_export_rows, task_export_rows)

router = APIRouter()


def _require_admin(request: Request) -> None:
    user = _ha_user(request)
    if user not in get_admins():
        raise HTTPException(403)


@router.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request, p: str = ""):
    base = _base(request)
    admins = get_admins()
    areas = await get_areas()

    # HA-User aus Header bestimmen
    ha_user = _ha_user(request)
    is_admin = ha_user in admins

    admin_link = (
        f'<a href="{base}admin" class="btn btn-primary btn-sm">{tr("settings.open_admin")}</a>'
        if is_admin else ""
    )

    if not p:
        if is_admin:
            # Admin ohne ?p= → Personenpicker anzeigen
            persons = await get_persons()
            pills = "".join(
                f'<a href="{base}settings?p={quote(pn, safe="")}" class="settings-person-tile">'
                f'<span>{escape(pn)}</span><small>{tr("settings.open_profile")}</small></a>'
                for pn in persons
            )
            own_controls = (
                f'<div class="settings-actions" style="margin-bottom:0.75rem">'
                f'<a href="{base}" class="btn btn-primary btn-sm">{tr("settings.back_to_me")}</a>'
                f'<a href="{base}settings{person_suffix(ha_user)}" class="btn btn-ghost btn-sm">{tr("menu.my_settings")}</a>'
                f'</div>'
                if ha_user else ""
            )
            content = f"""
            <div class="hero-card page-hero">
              <div>
                <div class="hero-eyebrow">Profile und Ansicht</div>
                <div class="hero-title">{tr("settings.title")}</div>
              </div>
              <div class="page-hero-actions">{admin_link}</div>
            </div>
            <div class="card settings-picker-card">
              <div class="settings-picker-head">
                <div>
                  <h3>{tr("menu.switch_person")}</h3>
                  <p class="muted">{tr("settings.profile_picker_hint")}</p>
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
        <h2>{tr("menu.who")}</h2>
        <div class="card">
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem">{pills}</div>
        </div>"""
        return render(content, request, page="settings", person="")

    card = _person_settings_card(p, areas, admins, base=base, action="settings")
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">{tr("settings.profile_notifications")}</div>
        <div class="hero-title">{tr("settings.title")}</div>
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
    language = normalize_language(form.get("language", cfg.get("language", "auto")) or "auto")
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
                         vacation_until=vacation_until,
                         language=language)
    return RedirectResponse(_base(request) + f"settings{person_suffix(person)}", status_code=303)


@router.get("/admin", response_class=HTMLResponse)
async def admin_form(request: Request, saved: str = ""):
    base = _base(request)
    admins = get_admins()
    persons = await get_persons()
    areas = await get_areas()

    available_svcs = await get_notify_services() if admins else []
    content = admin_page_content(base, admins, persons, areas, saved, available_svcs)
    return render(content, request, page="settings", person=_ha_user(request))


@router.get("/admin/export.json")
async def admin_export_json(request: Request):
    _require_admin(request)
    return json_backup_response(export_backup_data())


@router.get("/admin/export/tasks.csv")
async def admin_export_tasks(request: Request):
    _require_admin(request)
    return _csv_response("tidyhome-tasks.csv", task_export_rows())


@router.get("/admin/export/projects.csv")
async def admin_export_projects(request: Request):
    _require_admin(request)
    return _csv_response("tidyhome-projects.csv", project_export_rows())


@router.get("/admin/export/scores.csv")
async def admin_export_scores(request: Request):
    _require_admin(request)
    return _csv_response("tidyhome-scores.csv", score_export_rows())


@router.get("/admin/diagnostics", response_class=HTMLResponse)
async def admin_diagnostics(request: Request):
    _require_admin(request)
    persons = await get_persons()
    areas = await get_areas()
    result = diagnose_data(persons, areas)
    issue_rows = ""
    for issue in result["issues"]:
        badge_cls = "overdue" if issue.get("severity") == "error" else "today"
        issue_rows += f"""
        <div class="admin-row">
          <div class="admin-row-main">
            <div class="admin-row-title">{escape(issue.get("label", ""))}</div>
            <div class="admin-row-sub">{escape(issue.get("type", ""))} · {escape(issue.get("detail", ""))}</div>
          </div>
          <span class="badge {badge_cls}">{escape(issue.get("severity", ""))}</span>
        </div>"""
    if not issue_rows:
        issue_rows = (
            '<div class="empty"><div class="empty-icon">✓</div>'
            '<div style="font-weight:700">Keine Probleme gefunden</div>'
            '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            'Personen, Räume, Projekte, Schritte und Fotos wirken konsistent.</div></div>'
        )

    counts = result["counts"]
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">Datenprüfung</div>
        <div class="hero-title">Admin-Diagnose</div>
        <div class="muted">{counts["issues"]} Hinweis(e) · {counts["tasks"]} Aufgaben · {counts["photos"]} Fotos</div>
      </div>
      <div class="page-hero-actions">
        <a class="btn btn-ghost btn-sm" href="{_base(request)}admin">{_icon("chevron_l", 14)} Admin</a>
      </div>
    </div>
    <div class="today-grid" style="margin-bottom:1rem">
      <div class="today-stat"><div class="today-value">{counts["tasks"]}</div><div class="today-label">Aufgaben</div></div>
      <div class="today-stat"><div class="today-value">{counts["projects"]}</div><div class="today-label">Projekte</div></div>
      <div class="today-stat"><div class="today-value">{counts["issues"]}</div><div class="today-label">Hinweise</div></div>
    </div>
    <div class="card card-flush">{issue_rows}</div>"""
    return render(content, request, page="settings", person=_ha_user(request))


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
                         vacation_until=cfg.get("vacation_until", ""),
                         language=cfg.get("language", "auto"))
    return RedirectResponse(_base(request) + "admin?saved=1", status_code=303)


@router.get("/notify-now/{person}")
async def notify_now(person: str, request: Request, p: str = ""):
    await notify_person_now(person)
    return RedirectResponse(_base(request) + f"settings{person_suffix(p or person)}", status_code=303)
