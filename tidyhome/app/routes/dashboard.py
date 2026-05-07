from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ha_client import get_areas
from render import render, resolve_person, ROOM_ICONS
from storage import get_person_settings, list_tasks, list_projects

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, p: str = ""):
    p = resolve_person(request, p)
    areas = await get_areas()
    today = date.today().isoformat()

    # Räume ausblenden für aktive Person
    hidden_rooms: set[str] = set()
    if p:
        hidden_rooms = set(get_person_settings(p).get("hidden_rooms", []))
    visible_areas = [r for r in areas if r not in hidden_rooms]

    all_tasks = list_tasks()
    if hidden_rooms:
        all_tasks = [t for t in all_tasks if t.room not in hidden_rooms]
    overdue = [t for t in all_tasks if t.days_until_due() < 0]
    due_today = [t for t in all_tasks if t.days_until_due() == 0]
    done_today = [t for t in all_tasks if t.last_done == today]
    all_projects = list_projects()
    if hidden_rooms:
        all_projects = [pr for pr in all_projects if pr.room not in hidden_rooms]

    total = len(all_tasks)
    health_pct = int((total - len(overdue)) / total * 100) if total else 100
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
    for r in visible_areas:
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
    <div class="room-grid">{room_cards}</div>"""

    return render(content, request, page="home", person=p)
