from fastapi import Request
from fastapi.responses import HTMLResponse

INTERVALS = {
    1: "Täglich", 2: "Alle 2 Tage", 7: "Wöchentlich", 14: "Alle 2 Wochen",
    30: "Monatlich", 90: "Vierteljährlich", 180: "Halbjährlich", 365: "Jährlich",
}

ROOM_ICONS = {
    "Küche": "🍳", "Wohnzimmer": "🛋", "Schlafzimmer": "🛏", "Bad": "🚿",
    "Badezimmer": "🚿", "Flur": "🚪", "Keller": "📦", "Garten": "🌿",
    "Garage": "🚗", "Büro": "💻", "Arbeitszimmer": "💻", "Esszimmer": "🍽",
    "Kinderzimmer": "🧸", "Balkon": "🌅", "Terrasse": "🌅",
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
    --primary: #b5738a;
    --primary-dark: #8f4f65;
    --primary-light: #f9f0f4;
    --primary-border: #e8c8d4;
    --bg: #faf7f8;
    --card: #ffffff;
    --text: #2d1f26;
    --muted: #9b8890;
    --border: #ede8eb;
    --success: #4a9e6b;
    --success-bg: #e8f5ee;
    --warning: #c47c1a;
    --warning-bg: #fef3e2;
    --danger: #c53030;
    --danger-bg: #fee2e2;
    --nav-h: 4rem;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: var(--bg); color: var(--text);
          padding-bottom: calc(var(--nav-h) + 0.5rem); }}
  header {{ background: white; border-bottom: 1px solid var(--border);
            padding: 0.875rem 1.25rem;
            display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 10; }}
  .h-left {{ display: flex; align-items: center; gap: 0.5rem; }}
  .h-logo {{ font-size: 1.35rem; }}
  .h-title {{ font-size: 1.05rem; font-weight: 700; color: var(--primary-dark); }}
  .h-pill {{ font-size: 0.78rem; background: var(--primary-light);
             color: var(--primary-dark); padding: 0.2rem 0.7rem;
             border-radius: 999px; border: 1px solid var(--primary-border);
             text-decoration: none; }}
  .bottom-nav {{ position: fixed; bottom: 0; left: 0; right: 0; height: var(--nav-h);
                 background: white; border-top: 1px solid var(--border);
                 display: flex; z-index: 10;
                 box-shadow: 0 -2px 8px rgba(0,0,0,0.05); }}
  .nav-item {{ flex: 1; display: flex; flex-direction: column; align-items: center;
               justify-content: center; gap: 0.15rem;
               text-decoration: none; color: var(--muted); font-size: 0.62rem;
               font-weight: 500; transition: color 0.15s; padding: 0.4rem 0; }}
  .nav-item.active {{ color: var(--primary); }}
  .nav-item .ni {{ font-size: 1.25rem; }}
  main {{ padding: 1.25rem; max-width: 640px; margin: 0 auto; }}
  .card {{ background: var(--card); border-radius: 1rem; padding: 1.25rem;
           box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 1rem; }}
  .card-flush {{ padding: 0; overflow: hidden; }}
  h2 {{ font-size: 1rem; font-weight: 700; margin-bottom: 0.875rem; }}
  h3 {{ font-size: 0.9rem; font-weight: 600; }}
  .muted {{ color: var(--muted); font-size: 0.8rem; }}
  .task-row {{ display: flex; align-items: center; gap: 0.75rem;
               padding: 0.8rem 1.25rem; border-bottom: 1px solid var(--border); }}
  .task-row:last-child {{ border-bottom: none; }}
  .task-name {{ flex: 1; font-weight: 500; font-size: 0.88rem; }}
  .task-meta {{ font-size: 0.75rem; color: var(--muted); }}
  .badge {{ display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
            font-size: 0.7rem; font-weight: 700; white-space: nowrap; }}
  .overdue {{ background: var(--danger-bg);  color: var(--danger); }}
  .today   {{ background: var(--warning-bg); color: var(--warning); }}
  .soon    {{ background: #fef9e7;           color: #92610a; }}
  .ok      {{ background: var(--success-bg); color: var(--success); }}
  .btn {{ display: inline-flex; align-items: center; justify-content: center;
          padding: 0.45rem 1rem; border-radius: 0.55rem; border: none;
          cursor: pointer; font-size: 0.84rem; font-weight: 600;
          text-decoration: none; transition: opacity 0.15s; gap: 0.3rem; }}
  .btn:hover {{ opacity: 0.82; }}
  .btn-primary {{ background: var(--primary); color: white; }}
  .btn-success {{ background: var(--success); color: white; }}
  .btn-danger  {{ background: var(--danger);  color: white; }}
  .btn-ghost   {{ background: var(--primary-light); color: var(--primary-dark);
                  border: 1px solid var(--primary-border); }}
  .btn-sm {{ padding: 0.22rem 0.55rem; font-size: 0.76rem; border-radius: 0.4rem; }}
  .btn-full {{ width: 100%; padding: 0.8rem; font-size: 0.95rem; border-radius: 0.75rem; }}
  form.inline {{ display: inline; }}
  .form-group {{ margin-bottom: 1rem; }}
  label {{ display: block; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.04em;
           text-transform: uppercase; margin-bottom: 0.3rem; color: var(--muted); }}
  input, select {{ width: 100%; padding: 0.6rem 0.875rem;
    border: 1.5px solid var(--border); border-radius: 0.6rem;
    font-size: 0.9rem; color: var(--text); background: white;
    transition: border-color 0.15s; }}
  input:focus, select:focus {{ outline: none; border-color: var(--primary); }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
  .filters {{ display: flex; gap: 0.4rem; margin-bottom: 1rem;
              flex-wrap: wrap; overflow-x: auto; padding-bottom: 0.1rem; }}
  .filter-btn {{ padding: 0.28rem 0.8rem; border-radius: 999px;
                 border: 1.5px solid var(--border); background: white;
                 cursor: pointer; font-size: 0.76rem; white-space: nowrap;
                 text-decoration: none; color: var(--text); transition: all 0.15s; }}
  .filter-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
  .score-row {{ display: flex; align-items: center; gap: 1rem;
                padding: 0.75rem 0; border-bottom: 1px solid var(--border); }}
  .score-row:last-child {{ border-bottom: none; }}
  .score-name {{ flex: 1; font-weight: 600; }}
  .score-pts {{ font-size: 1.1rem; font-weight: 700; color: var(--primary); }}
  .progress-track {{ background: var(--border); border-radius: 999px; height: 5px; }}
  .progress-fill  {{ background: var(--primary); height: 5px; border-radius: 999px; transition: width 0.3s; }}
  .progress-fill.green {{ background: var(--success); }}
  .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem; }}
  .stat-card {{ background: white; border-radius: 1rem; padding: 1rem 0.75rem;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06); text-align: center; }}
  .stat-value {{ font-size: 2rem; font-weight: 800; color: var(--primary); line-height: 1; }}
  .stat-value.green {{ color: var(--success); }}
  .stat-label {{ font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; font-weight: 500; }}
  .room-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }}
  .room-card {{ background: white; border-radius: 1rem; padding: 1rem;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                text-decoration: none; color: var(--text); display: block; }}
  .room-card:hover {{ box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
  .room-icon {{ font-size: 1.6rem; margin-bottom: 0.35rem; }}
  .room-name {{ font-weight: 700; font-size: 0.88rem; margin-bottom: 0.15rem; }}
  .room-count {{ font-size: 0.72rem; color: var(--muted); margin-bottom: 0.4rem; }}
  .empty {{ color: var(--muted); text-align: center; padding: 2.5rem 1rem; font-size: 0.88rem; }}
  .info-box {{ background: var(--primary-light); border: 1px solid var(--primary-border);
               border-radius: 0.75rem; padding: 0.875rem; margin-bottom: 1rem;
               font-size: 0.82rem; color: var(--primary-dark); }}
  .admin-badge {{ font-size: 0.7rem; background: var(--primary-light); color: var(--primary-dark);
                  padding: 0.1rem 0.5rem; border-radius: 999px; border: 1px solid var(--primary-border); }}
  .page-header {{ display: flex; justify-content: space-between;
                  align-items: center; margin-bottom: 1rem; }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #1c1518; --card: #261e22; --text: #ede5e9;
      --muted: #9b8890; --border: #3d2d34;
      --primary-light: #2e1e27; --primary-border: #5a3347;
      --success-bg: #0f2a1c; --warning-bg: #2a1e08; --danger-bg: #2a0f0f;
    }}
    header, .bottom-nav {{ background: var(--card); }}
    input, select {{ background: #2e2228; color: var(--text); border-color: var(--border); }}
    .room-card, .stat-card {{ background: var(--card); }}
    .filter-btn {{ background: var(--card); color: var(--text); border-color: var(--border); }}
    .filter-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
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
    <a href="admin" class="h-pill" title="Admin">⚙</a>
  </div>
</header>
<main>
{content}
</main>
<nav class="bottom-nav">
  <a href="./{psuffix}" class="nav-item {p_home}"><span class="ni">🏠</span>Zuhause</a>
  <a href="tasks{psuffix}" class="nav-item {p_tasks}"><span class="ni">✅</span>Aufgaben</a>
  <a href="projects{psuffix}" class="nav-item {p_projects}"><span class="ni">📦</span>Projekte</a>
  <a href="scores{psuffix}" class="nav-item {p_scores}"><span class="ni">🏆</span>Punkte</a>
  <a href="settings{psuffix}" class="nav-item {p_settings}"><span class="ni">👤</span>Einstellungen</a>
</nav>
</body>
</html>"""


def render(content: str, request: Request, page: str = "home",
           person: str = "") -> HTMLResponse:
    base = _base(request)
    psuffix = f"?p={person}" if person else ""
    person_nav = (f'<a href="settings{psuffix}" class="h-pill">{person}</a>' if person
                  else '<a href="settings" class="h-pill">Wer bin ich?</a>')
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
