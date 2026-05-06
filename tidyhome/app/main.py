import os
import asyncio
import logging
from datetime import datetime, time as dtime, timedelta, date
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from models import Task, Project, Step
from storage import (list_tasks, get_task, create_task, edit_task, delete_task,
                     mark_done, get_scores, get_person_settings, save_person_settings,
                     list_person_settings, list_projects, get_project, create_project,
                     update_project, delete_project, list_steps, add_step,
                     complete_step, delete_step)
from ha_client import get_areas, get_persons, send_notification

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger("tidyhome")

_admins_raw = os.environ.get("ADMINS", "")
ADMINS: set[str] = {a.strip() for a in _admins_raw.split(",") if a.strip()}
logger.info("Admins: %s", ADMINS or "(keine)")

app = FastAPI(title="TidyHome", version="1.0.0")

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
    if days < 0:   return "overdue"
    if days == 0:  return "today"
    if days <= 3:  return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


def _selected(value, current) -> str:
    return " selected" if str(value) == str(current) else ""


HTML_BASE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="{base}">
<title>TidyHome</title>
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
  .stat-sub {{ font-size: 0.65rem; color: var(--muted); }}

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
</style>
</head>
<body>
<header>
  <div class="h-left">
    <span class="h-logo">🧹</span>
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
  <a href="./" class="nav-item {p_home}"><span class="ni">🏠</span>Zuhause</a>
  <a href="tasks" class="nav-item {p_tasks}"><span class="ni">✅</span>Aufgaben</a>
  <a href="projects" class="nav-item {p_projects}"><span class="ni">📦</span>Projekte</a>
  <a href="scores" class="nav-item {p_scores}"><span class="ni">🏆</span>Punkte</a>
  <a href="settings" class="nav-item {p_settings}"><span class="ni">👤</span>Einstellungen</a>
</nav>
</body>
</html>"""


def render(content: str, request: Request, page: str = "home",
           person: str = "") -> HTMLResponse:
    base = _base(request)
    person_nav = (f'<span class="h-pill">{person}</span>' if person
                  else '<a href="settings" class="h-pill">Wer bin ich?</a>')
    html = HTML_BASE.format(
        content=content, base=base, person_nav=person_nav,
        p_home="active" if page == "home" else "",
        p_tasks="active" if page == "tasks" else "",
        p_projects="active" if page == "projects" else "",
        p_scores="active" if page == "scores" else "",
        p_settings="active" if page == "settings" else "",
    )
    return HTMLResponse(html)


# ── Dashboard ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, p: str = ""):
    areas = await get_areas()
    today = date.today().isoformat()

    all_tasks = list_tasks()
    overdue = [t for t in all_tasks if t.days_until_due() < 0]
    due_today = [t for t in all_tasks if t.days_until_due() == 0]
    done_today = [t for t in all_tasks if t.last_done == today]

    all_projects = list_projects()

    total = len(all_tasks)
    not_overdue = total - len(overdue)
    health_pct = int(not_overdue / total * 100) if total else 100

    greeting = f"Hallo{' ' + p if p else ''}! 👋"

    stat_grid = f"""
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">{len(done_today)}<span style="font-size:1rem;color:var(--muted)">/{len(due_today) + len(done_today)}</span></div>
        <div class="stat-label">Heute erledigt</div>
      </div>
      <div class="stat-card">
        <div class="stat-value {'green' if not overdue else ''}">{len(overdue)}</div>
        <div class="stat-label">Überfällig</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="font-size:1.4rem">{total} <span style="font-size:0.9rem;color:var(--muted)">|</span> {len(all_projects)}</div>
        <div class="stat-label">Aufgaben | Projekte</div>
      </div>
      <div class="stat-card">
        <div class="stat-value {'green' if health_pct == 100 else ''}">{health_pct}%</div>
        <div class="stat-label">Gesamtzustand</div>
      </div>
    </div>"""

    health_bar = f"""
    <div class="card" style="padding:1rem">
      <div style="display:flex;justify-content:space-between;font-size:0.78rem;
                  color:var(--muted);margin-bottom:0.4rem">
        <span>Gesamtzustand</span><span>{health_pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill {'green' if health_pct > 80 else ''}"
             style="width:{health_pct}%"></div>
      </div>
    </div>"""

    room_cards = ""
    for r in areas:
        icon = ROOM_ICONS.get(r, "🏠")
        r_tasks = [t for t in all_tasks if t.room == r]
        r_projects = [pr for pr in all_projects if pr.room == r]
        r_overdue = sum(1 for t in r_tasks if t.days_until_due() < 0)
        count_txt = f"{len(r_tasks)} Aufgaben · {len(r_projects)} Projekte"
        badge = (f'<span class="badge overdue" style="font-size:0.65rem">'
                 f'{r_overdue} überfällig</span>' if r_overdue else "")
        room_cards += f"""
        <a class="room-card" href="tasks?room={r}">
          <div class="room-icon">{icon}</div>
          <div class="room-name">{r}</div>
          <div class="room-count">{count_txt}</div>
          {badge}
        </a>"""

    content = f"""
    <h2 style="font-size:1.2rem;margin-bottom:1rem">{greeting}</h2>
    {stat_grid}
    {health_bar}
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin-bottom:0.75rem;margin-top:0.25rem">
      <h2 style="margin:0">Räume</h2>
      <a class="btn btn-ghost btn-sm" href="tasks/new">+ Neue Aufgabe</a>
    </div>
    <div class="room-grid">{room_cards}</div>
    """
    return render(content, request, page="home", person=p)


# ── Aufgaben ───────────────────────────────────────────────────────────────

@app.get("/tasks", response_class=HTMLResponse)
async def tasks_list(request: Request, room: str = None, person: str = None,
                     overdue: str = None, p: str = ""):
    tasks = list_tasks(room=room, assigned_to=person, overdue_only=(overdue == "1"))
    areas = await get_areas()

    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if not room and not overdue else ""}" href="tasks">Alle</a>'
    filters += f'<a class="filter-btn {"active" if overdue == "1" else ""}" href="tasks?overdue=1">Überfällig</a>'
    for r in areas:
        filters += f'<a class="filter-btn {"active" if room == r else ""}" href="tasks?room={r}">{r}</a>'
    filters += '</div>'

    rows = ""
    if not tasks:
        rows = '<div class="empty">Keine Aufgaben gefunden.</div>'
    else:
        for t in tasks:
            due = t.days_until_due()
            uc = urgency_class(due)
            if due < 0:   due_text = f"{abs(due)}d überfällig"
            elif due == 0: due_text = "Heute"
            elif due == 1: due_text = "Morgen"
            else:          due_text = f"In {due}d"
            assigned = f"<span class='task-meta'>→ {t.assigned_to}</span>" if t.assigned_to else ""
            rows += f"""
            <div class="task-row">
              <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
                  <span class="task-name">{t.name}</span>
                  <span class="badge {uc}">{due_text}</span>
                </div>
                <div class="task-meta" style="margin-top:0.2rem">
                  {t.room} · {interval_label(t.interval_days)} · {t.points} Pkt {assigned}
                </div>
              </div>
              <form class="inline" method="post" action="tasks/{t.id}/done">
                <button class="btn btn-success btn-sm" title="Erledigt">✓</button>
              </form>
              <a class="btn btn-ghost btn-sm" href="tasks/{t.id}/edit" title="Bearbeiten">✎</a>
              <a class="btn btn-danger btn-sm" href="tasks/{t.id}/delete"
                 onclick="return confirm('Löschen?')" title="Löschen">✕</a>
            </div>"""

    content = f"""
    <div class="page-header">
      <h2>Aufgaben ({len(tasks)})</h2>
      <a class="btn btn-primary btn-sm" href="tasks/new">+ Neu</a>
    </div>
    {filters}
    <div class="card card-flush">{rows}</div>
    """
    return render(content, request, page="tasks", person=p)


@app.get("/tasks/new", response_class=HTMLResponse)
async def task_new_form(request: Request, p: str = ""):
    return await _render_task_form(request, "Neue Aufgabe", "tasks", "Aufgabe anlegen",
                                   person=p)


@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def task_edit_form(task_id: str, request: Request, p: str = ""):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404)
    return await _render_task_form(
        request, "Aufgabe bearbeiten", f"tasks/{task_id}/edit",
        "Speichern", task=task, person=p)


@app.post("/tasks/{task_id}/edit")
async def task_edit(task_id: str, request: Request,
                    name: str = Form(...), room: str = Form(...),
                    interval_days: int = Form(...), assigned_to: str = Form(""),
                    points: int = Form(10)):
    updated = edit_task(task_id, name=name, room=room, interval_days=interval_days,
                        assigned_to=assigned_to or None, points=points)
    if not updated:
        raise HTTPException(404)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


@app.post("/tasks")
async def task_create(request: Request, name: str = Form(...), room: str = Form(...),
                      interval_days: int = Form(...), assigned_to: str = Form(""),
                      points: int = Form(10)):
    task = Task(name=name, room=room, interval_days=interval_days,
                assigned_to=assigned_to or None, points=points)
    create_task(task)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


@app.post("/tasks/{task_id}/done")
async def task_done(task_id: str, request: Request):
    form = await request.form()
    done_by = form.get("done_by") or None
    task = mark_done(task_id, done_by=done_by)
    if not task:
        raise HTTPException(404)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


@app.get("/tasks/{task_id}/delete")
async def task_delete(task_id: str, request: Request):
    delete_task(task_id)
    return RedirectResponse(_base(request) + "tasks", status_code=303)


async def _render_task_form(request: Request, title: str, action: str,
                             submit_label: str, task=None, person: str = "") -> HTMLResponse:
    areas = await get_areas()
    persons = await get_persons()
    cur_room = task.room if task else ""
    cur_interval = task.interval_days if task else 7
    cur_person = task.assigned_to if task else ""
    cur_points = task.points if task else 10
    cur_name = task.name if task else ""

    room_opts = "".join(
        f'<option value="{r}"{_selected(r, cur_room)}>{r}</option>' for r in areas)
    person_opts = (f'<option value=""{_selected("", cur_person or "")}>— Niemand —</option>'
                   + "".join(f'<option value="{p}"{_selected(p, cur_person or "")}>{p}</option>'
                              for p in persons))
    interval_opts = "".join(
        f'<option value="{d}"{_selected(d, cur_interval)}>{label}</option>'
        for d, label in INTERVALS.items())

    content = f"""
    <h2>{title}</h2>
    <div class="card">
      <form method="post" action="{action}">
        <div class="form-group">
          <label>Was ist zu erledigen?</label>
          <input name="name" required placeholder="z.B. Staubsaugen" value="{cur_name}">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>Raum</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>Intervall</label>
            <select name="interval_days">{interval_opts}</select>
          </div>
          <div class="form-group">
            <label>Zugewiesen an</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
          <div class="form-group">
            <label>Punkte</label>
            <input name="points" type="number" value="{cur_points}" min="1" max="100">
          </div>
        </div>
        <button class="btn btn-primary btn-full" type="submit">{submit_label}</button>
        <a class="btn btn-ghost btn-full" href="tasks" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="tasks", person=person)


# ── Projekte ───────────────────────────────────────────────────────────────

@app.get("/projects", response_class=HTMLResponse)
async def projects_list(request: Request, room: str = None, p: str = ""):
    areas = await get_areas()
    projects = list_projects(room=room)

    filters = '<div class="filters">'
    filters += f'<a class="filter-btn {"active" if not room else ""}" href="projects">Alle</a>'
    for r in areas:
        filters += f'<a class="filter-btn {"active" if room == r else ""}" href="projects?room={r}">{r}</a>'
    filters += '</div>'

    rows = ""
    if not projects:
        rows = '<div class="empty">Noch keine Ordnungsprojekte.</div>'
    else:
        for proj in projects:
            steps = list_steps(proj.id)
            done, total = proj.progress(steps)
            pct = int(done / total * 100) if total else 0
            assigned = f"<span class='task-meta'>→ {proj.assigned_to}</span>" if proj.assigned_to else ""
            rows += f"""
            <div class="task-row">
              <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:center;gap:0.5rem">
                  <a href="projects/{proj.id}" class="task-name"
                     style="text-decoration:none;color:inherit">{proj.name}</a>
                  {assigned}
                </div>
                <div class="task-meta" style="margin-top:0.2rem">{proj.room} · {done}/{total} Schritte</div>
                <div class="progress-track" style="margin-top:0.4rem">
                  <div class="progress-fill" style="width:{pct}%"></div>
                </div>
              </div>
              <a class="btn btn-ghost btn-sm" href="projects/{proj.id}/edit">✎</a>
              <a class="btn btn-danger btn-sm" href="projects/{proj.id}/delete"
                 onclick="return confirm('Projekt löschen?')">✕</a>
            </div>"""

    content = f"""
    <div class="page-header">
      <h2>Ordnungsprojekte ({len(projects)})</h2>
      <a class="btn btn-primary btn-sm" href="projects/new">+ Neu</a>
    </div>
    {filters}
    <div class="card card-flush">{rows}</div>"""
    return render(content, request, page="projects", person=p)


@app.get("/projects/new", response_class=HTMLResponse)
async def project_new_form(request: Request, p: str = ""):
    areas = await get_areas()
    persons = await get_persons()
    room_opts = "".join(f'<option value="{r}">{r}</option>' for r in areas)
    person_opts = '<option value="">— Niemand —</option>' + "".join(
        f'<option value="{pn}">{pn}</option>' for pn in persons)
    content = f"""
    <h2>Neues Ordnungsprojekt</h2>
    <div class="card">
      <form method="post" action="projects">
        <div class="form-group">
          <label>Projektname</label>
          <input name="name" required placeholder="z.B. Keller aufräumen">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>Raum</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>Zugewiesen an</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
        </div>
        <div class="form-group">
          <label>Beschreibung (optional)</label>
          <input name="description" placeholder="Was soll erreicht werden?">
        </div>
        <button class="btn btn-primary btn-full" type="submit">Projekt anlegen</button>
        <a class="btn btn-ghost btn-full" href="projects" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@app.post("/projects")
async def project_create(request: Request, name: str = Form(...), room: str = Form(...),
                          assigned_to: str = Form(""), description: str = Form("")):
    proj = Project(name=name, room=room, assigned_to=assigned_to or None,
                   description=description or None)
    create_project(proj)
    return RedirectResponse(_base(request) + f"projects/{proj.id}", status_code=303)


@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str, request: Request, p: str = ""):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    steps = list_steps(project_id)
    done, total = proj.progress(steps)
    pct = int(done / total * 100) if total else 0
    persons = await get_persons()
    person_opts = '<option value="">— Niemand —</option>' + "".join(
        f'<option value="{pn}">{pn}</option>' for pn in persons)

    step_rows = ""
    for s in steps:
        if s.completed:
            who = f" · {s.completed_by}" if s.completed_by else ""
            step_rows += f"""
            <div class="task-row" style="opacity:0.5">
              <span style="color:var(--success);font-size:1.1rem">✓</span>
              <span class="task-name" style="text-decoration:line-through">{s.name}</span>
              <span class="task-meta">{s.points} Pkt{who}</span>
            </div>"""
        else:
            step_rows += f"""
            <div class="task-row">
              <span class="task-name" style="flex:1">{s.name}</span>
              <span class="task-meta" style="margin-right:0.5rem">{s.points} Pkt</span>
              <form class="inline" method="post" action="steps/{s.id}/done">
                <select name="done_by" style="width:auto;padding:0.2rem 0.4rem;
                  font-size:0.78rem;margin-right:0.3rem;border-radius:0.4rem">
                  {person_opts}
                </select>
                <button class="btn btn-success btn-sm">✓</button>
              </form>
              <a class="btn btn-danger btn-sm" style="margin-left:0.3rem"
                 href="steps/{s.id}/delete" onclick="return confirm('Schritt löschen?')">✕</a>
            </div>"""

    if not steps:
        step_rows = '<div class="empty">Noch keine Schritte. Füge unten den ersten hinzu.</div>'

    assigned = f" · → {proj.assigned_to}" if proj.assigned_to else ""
    desc = (f'<p class="muted" style="margin-bottom:1rem">{proj.description}</p>'
            if proj.description else "")

    content = f"""
    <div class="page-header">
      <div>
        <h2>{proj.name}</h2>
        <div class="muted">{proj.room}{assigned}</div>
      </div>
      <a class="btn btn-ghost btn-sm" href="edit">✎ Bearbeiten</a>
    </div>
    {desc}
    <div class="card" style="padding:1rem;margin-bottom:1rem">
      <div style="display:flex;justify-content:space-between;font-size:0.78rem;
                  color:var(--muted);margin-bottom:0.4rem">
        <span>{done} von {total} Schritten</span><span>{pct}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill {'green' if pct == 100 else ''}" style="width:{pct}%"></div>
      </div>
    </div>
    <div class="card card-flush" style="margin-bottom:1rem">{step_rows}</div>
    <div class="card">
      <h3 style="margin-bottom:0.75rem">Schritt hinzufügen</h3>
      <form method="post" action="steps">
        <div class="grid-2">
          <div class="form-group">
            <label>Beschreibung</label>
            <input name="name" required placeholder="z.B. Kartons sortieren">
          </div>
          <div class="form-group">
            <label>Punkte</label>
            <input name="points" type="number" value="5" min="1" max="100">
          </div>
        </div>
        <button class="btn btn-primary btn-sm" type="submit">Hinzufügen</button>
        <a class="btn btn-ghost btn-sm" href="projects" style="margin-left:0.5rem">← Alle Projekte</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@app.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def project_edit_form(project_id: str, request: Request, p: str = ""):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    areas = await get_areas()
    persons = await get_persons()
    room_opts = "".join(
        f'<option value="{r}"{_selected(r, proj.room)}>{r}</option>' for r in areas)
    person_opts = (f'<option value=""{_selected("", proj.assigned_to or "")}>— Niemand —</option>'
                   + "".join(f'<option value="{pn}"{_selected(pn, proj.assigned_to or "")}>{pn}</option>'
                              for pn in persons))
    content = f"""
    <h2>Projekt bearbeiten</h2>
    <div class="card">
      <form method="post" action="edit">
        <div class="form-group">
          <label>Name</label>
          <input name="name" required value="{proj.name}">
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>Raum</label>
            <select name="room">{room_opts}</select>
          </div>
          <div class="form-group">
            <label>Zugewiesen an</label>
            <select name="assigned_to">{person_opts}</select>
          </div>
        </div>
        <div class="form-group">
          <label>Beschreibung</label>
          <input name="description" value="{proj.description or ''}">
        </div>
        <button class="btn btn-primary btn-full" type="submit">Speichern</button>
        <a class="btn btn-ghost btn-full" href="../{project_id}" style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""
    return render(content, request, page="projects", person=p)


@app.post("/projects/{project_id}/edit")
async def project_edit(project_id: str, request: Request, name: str = Form(...),
                        room: str = Form(...), assigned_to: str = Form(""),
                        description: str = Form("")):
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(404)
    proj.name = name
    proj.room = room
    proj.assigned_to = assigned_to or None
    proj.description = description or None
    update_project(proj)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@app.get("/projects/{project_id}/delete")
async def project_delete(project_id: str, request: Request):
    delete_project(project_id)
    return RedirectResponse(_base(request) + "projects", status_code=303)


@app.post("/projects/{project_id}/steps")
async def step_add(project_id: str, request: Request,
                   name: str = Form(...), points: int = Form(5)):
    if not get_project(project_id):
        raise HTTPException(404)
    add_step(Step(project_id=project_id, name=name, points=points))
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@app.post("/projects/{project_id}/steps/{step_id}/done")
async def step_done(project_id: str, step_id: str, request: Request):
    form = await request.form()
    complete_step(step_id, done_by=form.get("done_by") or None)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


@app.get("/projects/{project_id}/steps/{step_id}/delete")
async def step_delete(project_id: str, step_id: str, request: Request):
    delete_step(step_id)
    return RedirectResponse(_base(request) + f"projects/{project_id}", status_code=303)


# ── Punkte ─────────────────────────────────────────────────────────────────

@app.get("/scores", response_class=HTMLResponse)
async def scores(request: Request, p: str = ""):
    data = get_scores()
    rows = ""
    if not data:
        rows = '<div class="empty">Noch keine Punkte vergeben.</div>'
    else:
        for i, s in enumerate(data):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i + 1}."
            t_done = s.get("tasks_done", 0)
            pr_done = s.get("project_steps_done", 0)
            rows += f"""
            <div class="score-row">
              <span style="font-size:1.2rem;min-width:1.5rem">{medal}</span>
              <span class="score-name">{s["person"]}</span>
              <span class="task-meta">{t_done} Aufg. · {pr_done} Schritte</span>
              <span class="score-pts">{s["points"]} Pkt</span>
            </div>"""
    content = f'<h2>Bestenliste</h2><div class="card card-flush" style="padding:0 1.25rem">{rows}</div>'
    return render(content, request, page="scores", person=p)


# ── Einstellungen ──────────────────────────────────────────────────────────

@app.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request, p: str = ""):
    persons = await get_persons()
    cards = ""
    for pn in persons:
        cfg = get_person_settings(pn)
        time_val = cfg.get("notify_time", "08:00")
        checked = "checked" if cfg.get("enabled") else ""
        services = cfg.get("services") or []
        svc_info = (f'<div class="muted" style="margin-bottom:0.75rem">Geräte: {", ".join(services)}</div>'
                    if services else
                    '<div class="muted" style="margin-bottom:0.75rem">Keine Geräte (Admin konfiguriert diese)</div>')
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


@app.post("/settings")
async def settings_save(request: Request, person: str = Form(...),
                         notify_time: str = Form("08:00"), enabled: str = Form("")):
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=cfg.get("services") or [],
                         notify_time=_parse_time(notify_time), enabled=(enabled == "1"))
    return RedirectResponse(_base(request) + "settings", status_code=303)


# ── Admin ──────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
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


@app.post("/admin")
async def admin_save(request: Request, person: str = Form(...), services: str = Form("")):
    if not ADMINS:
        raise HTTPException(403)
    svc_list = [s.strip() for s in services.split(",") if s.strip()]
    cfg = get_person_settings(person)
    save_person_settings(person=person, services=svc_list,
                         notify_time=cfg.get("notify_time", "08:00"),
                         enabled=cfg.get("enabled", False))
    return RedirectResponse(_base(request) + "admin", status_code=303)


# ── Scheduler ─────────────────────────────────────────────────────────────

def _parse_time(raw: str) -> str:
    try:
        hh, mm = raw.strip().split(":", 1)
        return f"{int(hh):02d}:{int(mm):02d}"
    except Exception:
        return "08:00"


async def _notify_person(person: str, services: list[str]) -> None:
    tasks = [t for t in list_tasks(assigned_to=person) if t.days_until_due() <= 0]
    if not tasks:
        return
    lines = [f"• {t.name} ({'heute' if t.days_until_due() == 0 else f'{abs(t.days_until_due())}d überfällig'})"
             for t in tasks]
    await send_notification(
        *services[0].split(".", 1) if "." in services[0] else ("notify", services[0]),
        title=f"TidyHome: {len(tasks)} Aufgabe(n) fällig",
        message="\n".join(lines)
    ) if len(services) == 1 else None
    for svc in services:
        domain, service = ("notify", svc) if "." not in svc else svc.split(".", 1)
        ok = await send_notification(f"{domain}.{service}", "", "")
        logger.info("Notify %s -> %s.%s: %s", person, domain, service, ok)


async def _notify_person_now(person: str) -> None:
    cfg = get_person_settings(person)
    if not cfg.get("enabled") or not cfg.get("services"):
        return
    await _do_notify(person, cfg["services"])


async def _do_notify(person: str, services: list[str]) -> None:
    tasks = [t for t in list_tasks(assigned_to=person) if t.days_until_due() <= 0]
    if not tasks:
        logger.info("Keine faelligen Aufgaben für %s", person)
        return
    lines = [f"• {t.name} ({'heute' if t.days_until_due() == 0 else f'{abs(t.days_until_due())}d überfällig'})"
             for t in tasks]
    title = f"TidyHome: {len(tasks)} Aufgabe(n) fällig"
    message = "\n".join(lines)
    for svc in services:
        ok = await send_notification(svc.strip(), title, message)
        logger.info("Notify %s -> %s: %s", person, svc, "ok" if ok else "fehler")


async def _scheduler_loop() -> None:
    logger.info("Scheduler gestartet")
    notified_today: set[str] = set()
    last_date = datetime.now().date()
    while True:
        try:
            await asyncio.sleep(60)
            now = datetime.now()
            if now.date() != last_date:
                notified_today.clear()
                last_date = now.date()
            hhmm = now.strftime("%H:%M")
            for cfg in list_person_settings():
                if not cfg.get("enabled") or not cfg.get("services"):
                    continue
                person = cfg["person"]
                key = f"{person}:{now.date().isoformat()}"
                if hhmm == _parse_time(cfg.get("notify_time", "08:00")) and key not in notified_today:
                    notified_today.add(key)
                    await _do_notify(person, cfg["services"])
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("Scheduler Fehler: %s", e)


@app.on_event("startup")
async def _start_scheduler():
    asyncio.create_task(_scheduler_loop())


@app.get("/notify-now/{person}")
async def notify_now(person: str, request: Request):
    await _notify_person_now(person)
    return RedirectResponse(_base(request) + "settings", status_code=303)


@app.get("/healthz")
async def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    ingress_path = os.environ.get("INGRESS_PATH", "")
    logger.info("TidyHome startet auf Port 8099 (ingress: %s)", ingress_path or "/")
    uvicorn.run(app, host="0.0.0.0", port=8099, root_path=ingress_path,
                log_level=log_level.lower())
