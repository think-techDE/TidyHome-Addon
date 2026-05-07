from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from render import render, resolve_person
from storage import get_person_settings, get_person_stats, get_scores

router = APIRouter()

_PERIODS = [
    ("all",        "Gesamt"),
    ("month",      "Dieser Monat"),
    ("last_month", "Letzter Monat"),
]


@router.get("/scores", response_class=HTMLResponse)
async def scores(request: Request, period: str = "all", p: str = ""):
    p = resolve_person(request, p)
    data = get_scores(period=period)

    tabs = '<div class="filters">'
    for key, label in _PERIODS:
        active = "active" if period == key else ""
        tabs += f'<a class="filter-btn {active}" href="scores?period={key}{("&p=" + p) if p else ""}">{label}</a>'
    tabs += '</div>'

    rows = ""
    if not data:
        hint = "Noch keine Punkte in diesem Zeitraum." if period != "all" else "Noch keine Punkte vergeben."
        rows = f'<div class="empty">{hint}</div>'
    else:
        for i, s in enumerate(data):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i + 1}."
            t_done = s.get("tasks_done", 0)
            pr_done = s.get("project_steps_done", 0)
            highlight = "background:var(--primary-light);" if s["person"] == p else ""
            rows += f"""
            <div class="score-row" style="{highlight}">
              <span style="font-size:1.2rem;min-width:1.5rem">{medal}</span>
              <span class="score-name">{s["person"]}</span>
              <span class="task-meta">{t_done} Aufg. · {pr_done} Schritte</span>
              <span class="score-pts">{s["points"]} Pkt</span>
            </div>"""

    note = ""
    if period != "all":
        note = '<div class="muted" style="margin-top:0.5rem;font-size:0.75rem">Nur Aktivitäten seit Einführung des Zeitraum-Trackings werden gezählt.</div>'

    # Persönliche Statistik (nur wenn Person aktiv)
    personal_section = ""
    if p:
        stats = get_person_stats(p)
        cfg = get_person_settings(p)
        goal = cfg.get("weekly_goal", 0)

        streak_txt = f"{stats['streak']} Tag{'e' if stats['streak'] != 1 else ''}" if stats["streak"] else "–"
        streak_fire = " 🔥" if stats["streak"] >= 3 else ""

        goal_bar = ""
        if goal:
            pct = min(int(stats["week_tasks"] / goal * 100), 100)
            fill_cls = "green" if pct >= 100 else ""
            goal_bar = f"""
            <div style="margin-top:0.75rem">
              <div style="display:flex;justify-content:space-between;
                          font-size:0.75rem;color:var(--muted);margin-bottom:0.3rem">
                <span>Wochenziel</span><span>{stats['week_tasks']}/{goal} Aufgaben</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill {fill_cls}" style="width:{pct}%"></div>
              </div>
            </div>"""

        personal_section = f"""
        <div class="card" style="margin-bottom:1rem">
          <h3 style="margin-bottom:0.75rem">Meine Statistik – {p}</h3>
          <div class="stat-grid" style="grid-template-columns:repeat(3,1fr);gap:0.5rem;margin-bottom:0">
            <div class="stat-card">
              <div class="stat-value" style="font-size:1.5rem">{stats['week_tasks']}</div>
              <div class="stat-label">Diese Woche</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" style="font-size:1.5rem">{stats['total_points']}</div>
              <div class="stat-label">Gesamt-Pkt</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" style="font-size:1.5rem">{streak_txt}{streak_fire}</div>
              <div class="stat-label">Streak</div>
            </div>
          </div>
          {goal_bar}
        </div>"""

    content = f"""
    <h2>Bestenliste</h2>
    {personal_section}
    {tabs}
    <div class="card card-flush" style="padding:0 1.25rem">{rows}</div>
    {note}"""
    return render(content, request, page="scores", person=p)
