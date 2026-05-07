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
<style>
  :root {{
    --bg: #f6f7f9;
    --surface: #ffffff;
    --surface-2: #f0f2f5;
    --card: var(--surface);
    --text: #20242a;
    --muted: #6f7682;
    --border: #dde2e8;
    --primary: #b5738a;
    --primary-dark: #85495e;
    --primary-soft: rgba(181, 115, 138, 0.13);
    --primary-border: rgba(181, 115, 138, 0.28);
    --success: #2f8f5b;
    --success-bg: #e8f5ee;
    --warning: #b06d12;
    --warning-bg: #fff4df;
    --danger: #c43d37;
    --danger-bg: #fde9e7;
    --soon-bg: #fff8d8;
    --soon: #8f6908;
    --shadow: 0 12px 30px rgba(24, 31, 42, 0.06);
    --nav-h: 4.25rem;
    --radius: 0.75rem;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: var(--bg); color: var(--text);
          padding-bottom: calc(var(--nav-h) + 0.75rem); }}
  header {{ background: rgba(255,255,255,0.88); border-bottom: 1px solid var(--border);
            padding: 0.75rem 1rem;
            display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 10; backdrop-filter: blur(18px); }}
  .h-left {{ display: flex; align-items: center; gap: 0.65rem; min-width: 0; }}
  .h-title {{ font-size: 1.02rem; font-weight: 750; color: var(--text); letter-spacing: 0; }}
  .h-pill {{ font-size: 0.78rem; background: var(--primary-soft);
             color: var(--primary-dark); padding: 0.38rem 0.7rem;
             border-radius: 999px; border: 1px solid var(--primary-border);
             text-decoration: none; font-weight: 650; line-height: 1; }}
  .bottom-nav {{ position: fixed; bottom: 0; left: 0; right: 0; height: var(--nav-h);
                 background: rgba(255,255,255,0.94); border-top: 1px solid var(--border);
                 display: flex; z-index: 10;
                 box-shadow: 0 -12px 28px rgba(24,31,42,0.08); backdrop-filter: blur(18px); }}
  .nav-item {{ flex: 1; display: flex; flex-direction: column; align-items: center;
               justify-content: center; gap: 0.25rem; position: relative;
               text-decoration: none; color: var(--muted); font-size: 0.64rem;
               font-weight: 650; transition: color 0.15s; padding: 0.45rem 0; }}
  .nav-item.active::before {{ content: ""; position: absolute; top: 0; width: 2.25rem;
                              height: 3px; border-radius: 999px; background: var(--primary); }}
  .nav-item.active {{ color: var(--primary); }}
  .nav-item .ni {{ width: 1.25rem; height: 1.25rem; display: grid; place-items: center; }}
  .nav-item svg {{ width: 1.2rem; height: 1.2rem; stroke-width: 2.2; }}
  main {{ padding: 1rem; max-width: 720px; margin: 0 auto; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
           padding: 1rem; box-shadow: var(--shadow); margin-bottom: 1rem; }}
  .card-flush {{ padding: 0; overflow: hidden; }}
  h2 {{ font-size: 1.05rem; font-weight: 750; margin-bottom: 0.875rem; letter-spacing: 0; }}
  h3 {{ font-size: 0.92rem; font-weight: 700; letter-spacing: 0; }}
  .muted {{ color: var(--muted); font-size: 0.8rem; }}
  .section-title {{ display:flex;justify-content:space-between;align-items:center;
                    gap:0.75rem;margin:1rem 0 0.65rem; }}
  .task-row {{ display: flex; align-items: center; gap: 0.7rem;
               padding: 0.9rem 1rem; border-bottom: 1px solid var(--border); position: relative; }}
  .task-row:last-child {{ border-bottom: none; }}
  .task-row.important {{ border-left: 4px solid var(--warning); }}
  .task-main {{ flex: 1; min-width: 0; }}
  .task-top {{ display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; }}
  .task-actions {{ display:flex; align-items:center; gap:0.35rem; flex-shrink: 0; }}
  .task-name {{ flex: 1; font-weight: 650; font-size: 0.91rem; min-width: 7rem; }}
  .task-meta {{ font-size: 0.75rem; color: var(--muted); }}
  .badge {{ display: inline-flex; align-items:center; gap:0.25rem; padding: 0.22rem 0.55rem;
            border-radius: 999px; font-size: 0.7rem; font-weight: 750; white-space: nowrap; }}
  .overdue {{ background: var(--danger-bg);  color: var(--danger); }}
  .today   {{ background: var(--warning-bg); color: var(--warning); }}
  .soon    {{ background: var(--soon-bg);    color: var(--soon); }}
  .ok      {{ background: var(--success-bg); color: var(--success); }}
  .btn {{ display: inline-flex; align-items: center; justify-content: center;
          min-height: 2.25rem; padding: 0.48rem 0.9rem; border-radius: 0.55rem; border: 1px solid transparent;
          cursor: pointer; font-size: 0.84rem; font-weight: 600;
          text-decoration: none; transition: background 0.15s, border-color 0.15s, transform 0.15s; gap: 0.3rem; }}
  .btn:hover {{ transform: translateY(-1px); }}
  .btn-primary {{ background: var(--primary); color: white; }}
  .btn-success {{ background: var(--success); color: white; }}
  .btn-danger  {{ background: var(--danger);  color: white; }}
  .btn-ghost   {{ background: var(--primary-soft); color: var(--primary-dark);
                  border: 1px solid var(--primary-border); }}
  .btn-icon {{ width: 2.25rem; padding: 0; font-size: 0.9rem; }}
  .btn-sm {{ min-height: 2rem; padding: 0.3rem 0.65rem; font-size: 0.76rem; border-radius: 0.48rem; }}
  .btn-full {{ width: 100%; padding: 0.8rem; font-size: 0.95rem; border-radius: 0.65rem; }}
  form.inline {{ display: inline; }}
  .form-group {{ margin-bottom: 1rem; }}
  label {{ display: block; font-size: 0.78rem; font-weight: 650;
           margin-bottom: 0.35rem; color: var(--muted); }}
  input, select {{ width: 100%; padding: 0.68rem 0.85rem;
    border: 1px solid var(--border); border-radius: 0.6rem;
    font-size: 0.9rem; color: var(--text); background: var(--surface);
    transition: border-color 0.15s, box-shadow 0.15s; }}
  input:focus, select:focus {{ outline: none; border-color: var(--primary);
                               box-shadow: 0 0 0 3px var(--primary-soft); }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
  .filters {{ display: flex; gap: 0.45rem; margin-bottom: 1rem;
              flex-wrap: nowrap; overflow-x: auto; padding-bottom: 0.15rem; scrollbar-width: none; }}
  .filters::-webkit-scrollbar {{ display:none; }}
  .filter-btn {{ padding: 0.42rem 0.82rem; border-radius: 999px;
                 border: 1px solid var(--border); background: var(--surface);
                 cursor: pointer; font-size: 0.76rem; white-space: nowrap;
                 text-decoration: none; color: var(--text); transition: all 0.15s; font-weight: 650; }}
  .filter-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
  .score-row {{ display: flex; align-items: center; gap: 1rem;
                padding: 0.75rem 0; border-bottom: 1px solid var(--border); }}
  .score-row:last-child {{ border-bottom: none; }}
  .score-name {{ flex: 1; font-weight: 600; }}
  .score-pts {{ font-size: 1.1rem; font-weight: 700; color: var(--primary); }}
  .progress-track {{ background: var(--surface-2); border-radius: 999px; height: 0.45rem; overflow:hidden; }}
  .progress-fill  {{ background: var(--primary); height: 100%; border-radius: 999px; transition: width 0.3s; }}
  .progress-fill.green {{ background: var(--success); }}
  .hero-card {{ background: linear-gradient(135deg, var(--surface), var(--surface-2));
                border:1px solid var(--border); border-radius: var(--radius); padding: 1rem;
                margin-bottom: 1rem; box-shadow: var(--shadow); }}
  .hero-eyebrow {{ color: var(--muted); font-size: 0.78rem; font-weight: 700; margin-bottom: 0.2rem; }}
  .hero-title {{ font-size: 1.35rem; font-weight: 800; line-height: 1.12; margin-bottom: 0.75rem; }}
  .today-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.55rem; }}
  .today-stat {{ background: var(--surface); border:1px solid var(--border); border-radius:0.65rem;
                 padding:0.7rem 0.55rem; }}
  .today-value {{ font-size: 1.25rem; font-weight: 800; line-height: 1; color: var(--text); }}
  .today-label {{ font-size: 0.68rem; color: var(--muted); margin-top: 0.22rem; font-weight:650; }}
  .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem; }}
  .stat-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
                padding: 0.85rem 0.75rem; text-align: center; }}
  .stat-value {{ font-size: 1.8rem; font-weight: 800; color: var(--primary); line-height: 1; }}
  .stat-value.green {{ color: var(--success); }}
  .stat-label {{ font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; font-weight: 500; }}
  .room-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }}
  .room-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
                padding: 0.9rem; box-shadow: var(--shadow);
                text-decoration: none; color: var(--text); display: block; }}
  .room-card:hover {{ border-color: var(--primary-border); }}
  .room-icon {{ width: 2.2rem; height: 2.2rem; border-radius:0.65rem; display:grid; place-items:center;
                background:var(--primary-soft); color:var(--primary-dark); font-weight:800;
                font-size:0.72rem; margin-bottom: 0.55rem; letter-spacing:0; }}
  .room-name {{ font-weight: 750; font-size: 0.9rem; margin-bottom: 0.15rem; }}
  .room-count {{ font-size: 0.72rem; color: var(--muted); margin-bottom: 0.4rem; }}
  .empty {{ color: var(--muted); text-align: center; padding: 2.5rem 1rem; font-size: 0.88rem; }}
  .info-box {{ background: var(--primary-soft); border: 1px solid var(--primary-border);
               border-radius: 0.75rem; padding: 0.875rem; margin-bottom: 1rem;
               font-size: 0.82rem; color: var(--primary-dark); }}
  .admin-badge {{ font-size: 0.7rem; background: var(--primary-soft); color: var(--primary-dark);
                  padding: 0.1rem 0.5rem; border-radius: 999px; border: 1px solid var(--primary-border); }}
  .page-header {{ display: flex; justify-content: space-between;
                  align-items: center; margin-bottom: 1rem; }}
  .project-card {{ display:block; color:inherit; text-decoration:none; padding:1rem; border-bottom:1px solid var(--border); }}
  .project-card:last-child {{ border-bottom:none; }}
  .project-card.done {{ opacity:0.72; }}
  .option-card {{ display:flex; align-items:flex-start; gap:0.65rem; padding:0.75rem;
                  border:1px solid var(--border); border-radius:0.65rem; background:var(--surface-2);
                  cursor:pointer; color:var(--text); }}
  .option-card input {{ width:1.05rem; height:1.05rem; margin-top:0.05rem; accent-color:var(--primary); }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #101114; --surface: #181a1f; --surface-2: #20232a; --card: var(--surface);
      --text: #f4f1f2; --muted: #a8a2a6; --border: #30333b;
      --primary: #c06b8b; --primary-dark: #f0b7c9; --primary-soft: rgba(192,107,139,0.16);
      --primary-border: rgba(192,107,139,0.32);
      --success: #63c174; --success-bg: rgba(99,193,116,0.13);
      --warning: #e0b84d; --warning-bg: rgba(224,184,77,0.14);
      --danger: #ff6257; --danger-bg: rgba(255,98,87,0.14);
      --soon: #e5c760; --soon-bg: rgba(229,199,96,0.13);
      --shadow: 0 14px 34px rgba(0,0,0,0.22);
    }}
    header, .bottom-nav {{ background: rgba(24,26,31,0.92); }}
    input, select {{ background: var(--surface-2); color: var(--text); border-color: var(--border); }}
    .filter-btn {{ background: var(--surface); color: var(--text); border-color: var(--border); }}
    .filter-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
  }}
  @media (max-width: 430px) {{
    main {{ padding: 0.85rem; }}
    .grid-2 {{ grid-template-columns: 1fr; gap: 0; }}
    .task-row {{ align-items:flex-start; }}
    .task-actions {{ flex-direction:column; }}
    .today-grid {{ grid-template-columns: repeat(3, minmax(0,1fr)); }}
  }}
</style>
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
