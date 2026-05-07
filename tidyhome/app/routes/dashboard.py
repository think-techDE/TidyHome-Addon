from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ha_client import get_areas
from render import interval_label, render, resolve_person, ROOM_ICONS, urgency_class
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
    greeting = f"Hallo{' ' + p if p else ''}"
    due_total = len(due_today) + len(done_today)

    next_tasks = sorted(
        [t for t in all_tasks if t.days_until_due() <= 3],
        key=lambda t: (t.days_until_due(), not t.important, t.name.lower()),
    )[:4]
    next_rows = ""
    if not next_tasks:
        next_rows = '<div class="empty" style="padding:1.4rem 1rem">Heute ist nichts Dringendes offen.</div>'
    else:
        for t in next_tasks:
            due = t.days_until_due()
            uc = urgency_class(due)
            if due < 0:
                due_text = f"{abs(due)}d überfällig"
            elif due == 0:
                due_text = "Heute"
            elif due == 1:
                due_text = "Morgen"
            else:
                due_text = f"In {due}d"
            assigned = f" · {', '.join(t.assigned_to)}" if t.assigned_to else ""
            next_rows += f"""
            <div class="task-row {'important' if t.important else ''}">
              <div class="task-main">
                <div class="task-top">
                  <span class="task-name">{t.name}</span>
                  <span class="badge {uc}">{due_text}</span>
                </div>
                <div class="task-meta" style="margin-top:0.25rem">
                  {t.room} · {interval_label(t.interval_days)}{assigned}
                </div>
              </div>
              <form class="inline" method="post" action="tasks/{t.id}/done">
                <button class="btn btn-success btn-icon" title="Erledigt">✓</button>
              </form>
            </div>"""

    today_card = f"""
    <section class="hero-card">
      <div class="hero-eyebrow">Heute</div>
      <div class="hero-title">{greeting}</div>
      <div class="today-grid">
        <div class="today-stat">
          <div class="today-value">{len(done_today)}<span style="font-size:0.78rem;color:var(--muted)">/{due_total}</span></div>
          <div class="today-label">erledigt</div>
        </div>
        <div class="today-stat">
          <div class="today-value" style="color:{'var(--success)' if not overdue else 'var(--danger)'}">{len(overdue)}</div>
          <div class="today-label">überfällig</div>
        </div>
        <div class="today-stat">
          <div class="today-value">{health_pct}%</div>
          <div class="today-label">Zustand</div>
        </div>
      </div>
      <div style="margin-top:0.85rem">
        <div style="display:flex;justify-content:space-between;font-size:0.74rem;
                    color:var(--muted);margin-bottom:0.35rem;font-weight:650">
          <span>Gesamtzustand</span><span>{total} Aufgaben · {len(all_projects)} Projekte</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill {'green' if health_pct > 80 else ''}" style="width:{health_pct}%"></div>
        </div>
      </div>
    </section>"""

    room_cards = ""
    for r in visible_areas:
        icon = ROOM_ICONS.get(r, "RM")
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
    {today_card}
    <div class="section-title">
      <h2 style="margin:0">Nächste Aufgaben</h2>
      <a class="btn btn-ghost btn-sm" href="tasks">Alle ansehen</a>
    </div>
    <div class="card card-flush">{next_rows}</div>
    <div class="section-title">
      <h2 style="margin:0">Räume</h2>
      <a class="btn btn-primary btn-sm" href="tasks/new">+ Aufgabe</a>
    </div>
    <div class="room-grid">{room_cards}</div>"""

    return render(content, request, page="home", person=p)
