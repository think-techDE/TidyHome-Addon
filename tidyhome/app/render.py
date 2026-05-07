from fastapi import Request
from fastapi.responses import HTMLResponse
from storage import get_admins

INTERVALS = {
    1: "Täglich", 2: "Alle 2 Tage", 7: "Wöchentlich", 14: "Alle 2 Wochen",
    30: "Monatlich", 90: "Vierteljährlich", 180: "Halbjährlich", 365: "Jährlich",
}

ROOM_ICONS = {
    "Küche": "KI", "Wohnzimmer": "WO", "Schlafzimmer": "SZ", "Bad": "BD",
    "Badezimmer": "BD", "Flur": "FL", "Keller": "KE", "Garten": "GA",
    "Garage": "GR", "Büro": "BU", "Arbeitszimmer": "AR", "Esszimmer": "EZ",
    "Kinderzimmer": "KZ", "Balkon": "BA", "Terrasse": "TE",
}


def interval_label(days: int) -> str:
    return INTERVALS.get(days, f"Alle {days} Tage")


def urgency_class(days: int) -> str:
    if days < 0:  return "overdue"
    if days == 0: return "today"
    if days <= 3: return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


def resolve_person(request: Request, p_param: str = "") -> str:
    """Effektive Person: Admins können per ?p= wechseln, alle anderen
    werden automatisch über den HA-Ingress-Header erkannt."""
    ha_user = (
        request.headers.get("X-Remote-User-Display-Name") or
        request.headers.get("X-Remote-User-Name", "")
    ).strip()
    # Admin mit explizitem Override: Ansicht wechseln erlaubt
    if p_param and ha_user in get_admins():
        return p_param
    # Alle anderen: HA-Identity, Fallback auf p_param
    return ha_user or p_param


def _selected(value, current) -> str:
    return " selected" if str(value) == str(current) else ""


_HTML_BASE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="{base}">
<title>TidyHome</title>
<link rel="icon" type="image/svg+xml" href="assets/logo.svg">
<link rel="stylesheet" href="assets/app.css">
</head>
<body>
<header>
  <div class="h-left">
    <img src="assets/logo.svg" style="width:30px;height:30px;border-radius:7px">
    <span class="h-title">TidyHome</span>
  </div>
  <div style="display:flex;gap:0.4rem;align-items:center">
    {person_nav}
    <a href="admin" class="h-pill" title="Admin">Admin</a>
  </div>
</header>
<main>
{content}
</main>
<nav class="bottom-nav">
  <a href="./{psuffix}" class="nav-item {p_home}"><span class="ni"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-5h5v5"/></svg></span>Zuhause</a>
  <a href="tasks{psuffix}" class="nav-item {p_tasks}"><span class="ni"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m9 11 2 2 4-5"/><path d="M5 6h.01"/><path d="M5 12h.01"/><path d="M5 18h.01"/><path d="M8 6h11"/><path d="M8 18h11"/></svg></span>Aufgaben</a>
  <a href="projects{psuffix}" class="nav-item {p_projects}"><span class="ni"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 7h16v12H4z"/><path d="M8 7V5h8v2"/><path d="M8 13h8"/></svg></span>Projekte</a>
  <a href="scores{psuffix}" class="nav-item {p_scores}"><span class="ni"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M5 5H3v2a4 4 0 0 0 4 4"/><path d="M19 5h2v2a4 4 0 0 1-4 4"/></svg></span>Punkte</a>
  <a href="settings{psuffix}" class="nav-item {p_settings}"><span class="ni"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="8" r="4"/></svg></span>Ich</a>
</nav>
</body>
</html>"""


def render(content: str, request: Request, page: str = "home",
           person: str = "") -> HTMLResponse:
    base = _base(request)
    psuffix = f"?p={person}" if person else ""
    admins = get_admins()
    if not person:
        person_nav = '<a href="settings" class="h-pill">Wer bin ich?</a>'
    elif person in admins:
        # Admin: kann Person wechseln
        person_nav = f'<a href="settings" class="h-pill">{person} ▾</a>'
    else:
        # Kein Admin: Name nur als Text, kein Wechsel möglich
        person_nav = f'<span class="h-pill">{person}</span>'
    html = _HTML_BASE.format(
        base=base,
        content=content,
        person_nav=person_nav,
        psuffix=psuffix,
        p_home="active" if page == "home" else "",
        p_tasks="active" if page == "tasks" else "",
        p_projects="active" if page == "projects" else "",
        p_scores="active" if page == "scores" else "",
        p_settings="active" if page == "settings" else "",
    )
    return HTMLResponse(html)
