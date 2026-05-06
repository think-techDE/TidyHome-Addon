import os
import logging
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from models import Task
from storage import list_tasks, create_task, delete_task, mark_done, get_scores
from ha_client import get_areas, get_persons

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger("tidyhome")

app = FastAPI(title="TidyHome", version="0.5.0")

INTERVALS = {
    1: "Täglich",
    2: "Alle 2 Tage",
    7: "Wöchentlich",
    14: "Alle 2 Wochen",
    30: "Monatlich",
    90: "Vierteljährlich",
    180: "Halbjährlich",
    365: "Jährlich",
}


def interval_label(days: int) -> str:
    return INTERVALS.get(days, f"Alle {days} Tage")


def urgency_class(days: int) -> str:
    if days < 0:
        return "overdue"
    if days == 0:
        return "today"
    if days <= 3:
        return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


HTML_BASE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="{base}">
<title>TidyHome</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background: #f0f4f8; color: #2d3748; }}
  header {{ background: #3182ce; color: white; padding: 1rem 1.5rem;
            display: flex; align-items: center; gap: 1rem; }}
  header h1 {{ font-size: 1.3rem; font-weight: 600; }}
  nav a {{ color: rgba(255,255,255,0.85); text-decoration: none; margin-left: 1.5rem;
           font-size: 0.9rem; }}
  nav a:hover {{ color: white; }}
  main {{ padding: 1.5rem; max-width: 900px; margin: 0 auto; }}
  h2 {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #2d3748; }}
  .card {{ background: white; border-radius: 0.75rem; padding: 1.25rem;
           box-shadow: 0 1px 6px rgba(0,0,0,0.08); margin-bottom: 1rem; }}
  .task-row {{ display: flex; align-items: center; gap: 0.75rem;
               padding: 0.75rem 0; border-bottom: 1px solid #edf2f7; }}
  .task-row:last-child {{ border-bottom: none; }}
  .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
            font-size: 0.75rem; font-weight: 600; }}
  .overdue {{ background: #fed7d7; color: #c53030; }}
  .today   {{ background: #feebc8; color: #c05621; }}
  .soon    {{ background: #fefcbf; color: #975a16; }}
  .ok      {{ background: #c6f6d5; color: #276749; }}
  .task-name {{ flex: 1; font-weight: 500; }}
  .task-meta {{ font-size: 0.8rem; color: #718096; }}
  .btn {{ display: inline-block; padding: 0.4rem 0.9rem; border-radius: 0.4rem;
          border: none; cursor: pointer; font-size: 0.85rem; font-weight: 500;
          text-decoration: none; }}
  .btn-primary {{ background: #3182ce; color: white; }}
  .btn-primary:hover {{ background: #2b6cb0; }}
  .btn-success {{ background: #38a169; color: white; }}
  .btn-success:hover {{ background: #276749; }}
  .btn-danger  {{ background: #e53e3e; color: white; }}
  .btn-danger:hover  {{ background: #c53030; }}
  .btn-sm {{ padding: 0.25rem 0.6rem; font-size: 0.78rem; }}
  form.inline {{ display: inline; }}
  .form-group {{ margin-bottom: 1rem; }}
  label {{ display: block; font-size: 0.85rem; font-weight: 500;
           margin-bottom: 0.3rem; color: #4a5568; }}
  input, select {{ width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #cbd5e0;
                   border-radius: 0.4rem; font-size: 0.9rem; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
  .score-row {{ display: flex; align-items: center; gap: 1rem;
                padding: 0.6rem 0; border-bottom: 1px solid #edf2f7; }}
  .score-row:last-child {{ border-bottom: none; }}
  .score-name {{ flex: 1; font-weight: 500; }}
  .score-pts {{ font-size: 1.1rem; font-weight: 700; color: #3182ce; }}
  .empty {{ color: #a0aec0; text-align: center; padding: 2rem; }}
  .due-label {{ font-size: 0.78rem; }}
  .filters {{ display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }}
  .filter-btn {{ padding: 0.3rem 0.8rem; border-radius: 999px; border: 1px solid #cbd5e0;
                 background: white; cursor: pointer; font-size: 0.8rem; }}
  .filter-btn.active {{ background: #3182ce; color: white; border-color: #3182ce; }}
</style>
</head>
<body>
<header>
  <span style="font-size:1.5rem">🧹</span>
  <h1>TidyHome</h1>
  <nav>
    <a href="./">Aufgaben</a>
    <a href="new">+ Neu</a>
    <a href="scores">Punkte</a>
  </nav>
</header>
<main>
{content}
</main>
</body>
</html>"""


def render(content: str, request: Request) -> HTMLResponse:
    return HTMLResponse(HTML_BASE.format(content=content, base=_base(request)))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, room: str = None, person: str = None, overdue: str = None):
    tasks = list_tasks(room=room, assigned_to=person, overdue_only=(overdue == "1"))
    areas = await get_areas()

    filters = '<div class="filters">'
    active = "active" if not room and not person and not overdue else ""
    filters += f'<a class="filter-btn {active}" href="./">Alle</a>'
    active = "active" if overdue == "1" else ""
    filters += f'<a class="filter-btn {active}" href="./?overdue=1">Ueberfaellig</a>'
    for r in areas:
        active = "active" if room == r else ""
        filters += f'<a class="filter-btn {active}" href="./?room={r}">{r}</a>'
    filters += '</div>'

    rows = ""
    if not tasks:
        rows = '<div class="empty">Keine Aufgaben gefunden.</div>'
    else:
        for t in tasks:
            due = t.days_until_due()
            uc = urgency_class(due)
            if due < 0:
                due_text = f"{abs(due)} Tage ueberfaellig"
            elif due == 0:
                due_text = "Heute faellig"
            elif due == 1:
                due_text = "Morgen faellig"
            else:
                due_text = f"In {due} Tagen"

            assigned = f"<span class='task-meta'>→ {t.assigned_to}</span>" if t.assigned_to else ""
            rows += f"""
            <div class="task-row">
              <span class="badge {uc} due-label">{due_text}</span>
              <div style="flex:1">
                <div class="task-name">{t.name}</div>
                <div class="task-meta">{t.room} · {interval_label(t.interval_days)} · {t.points} Pkt {assigned}</div>
              </div>
              <form class="inline" method="post" action="done/{t.id}">
                <button class="btn btn-success btn-sm">✓</button>
              </form>
              <a class="btn btn-danger btn-sm" href="delete/{t.id}" onclick="return confirm('Loeschen?')">✕</a>
            </div>"""

    content = f"""
    <h2>Aufgaben ({len(tasks)})</h2>
    {filters}
    <div class="card">{rows}</div>
    """
    return render(content, request)


@app.get("/new", response_class=HTMLResponse)
async def new_form(request: Request):
    areas = await get_areas()
    persons = await get_persons()

    room_opts = "".join(f'<option value="{r}">{r}</option>' for r in areas)
    person_opts = '<option value="">— Niemand —</option>' + "".join(
        f'<option value="{p}">{p}</option>' for p in persons
    )
    interval_opts = "".join(
        f'<option value="{d}">{label}</option>' for d, label in INTERVALS.items()
    )

    content = f"""
    <h2>Neue Aufgabe</h2>
    <div class="card">
      <form method="post" action="tasks">
        <div class="grid-2">
          <div class="form-group">
            <label>Name</label>
            <input name="name" required placeholder="z.B. Staubsaugen">
          </div>
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
            <input name="points" type="number" value="10" min="1" max="100">
          </div>
        </div>
        <button class="btn btn-primary" type="submit">Aufgabe anlegen</button>
        <a class="btn" href="./" style="background:#edf2f7;margin-left:0.5rem">Abbrechen</a>
      </form>
    </div>
    """
    return render(content, request)


@app.post("/tasks")
async def create(
    request: Request,
    name: str = Form(...),
    room: str = Form(...),
    interval_days: int = Form(...),
    assigned_to: str = Form(""),
    points: int = Form(10),
):
    task = Task(
        name=name,
        room=room,
        interval_days=interval_days,
        assigned_to=assigned_to or None,
        points=points,
    )
    create_task(task)
    return RedirectResponse(_base(request), status_code=303)


@app.post("/done/{task_id}")
async def done(task_id: str, request: Request):
    form = await request.form()
    done_by = form.get("done_by")
    task = mark_done(task_id, done_by=done_by or None)
    if not task:
        raise HTTPException(404)
    return RedirectResponse(_base(request), status_code=303)


@app.get("/delete/{task_id}")
async def delete(task_id: str, request: Request):
    delete_task(task_id)
    return RedirectResponse(_base(request), status_code=303)


@app.get("/scores", response_class=HTMLResponse)
async def scores(request: Request):
    data = get_scores()
    rows = ""
    if not data:
        rows = '<div class="empty">Noch keine Punkte vergeben.</div>'
    else:
        for i, s in enumerate(data):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
            rows += f"""
            <div class="score-row">
              <span style="font-size:1.2rem">{medal}</span>
              <span class="score-name">{s["person"]}</span>
              <span class="task-meta">{s["tasks_done"]} Aufgaben</span>
              <span class="score-pts">{s["points"]} Pkt</span>
            </div>"""

    content = f"""
    <h2>Bestenliste</h2>
    <div class="card">{rows}</div>
    """
    return render(content, request)


@app.get("/healthz")
async def health():
    return {"status": "ok", "version": "0.4.0"}


if __name__ == "__main__":
    ingress_path = os.environ.get("INGRESS_PATH", "")
    logger.info("TidyHome startet auf Port 8099 (ingress: %s)", ingress_path or "/")
    uvicorn.run(app, host="0.0.0.0", port=8099, root_path=ingress_path, log_level=log_level.lower())
