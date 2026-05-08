from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from html import escape

from render import _icon, format_date_de, render, resolve_person
from storage import (get_person_settings, get_person_stats,
                     get_recent_score_events, get_scores)

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
    all_time = get_scores(period="all")
    month_data = get_scores(period="month")

    tabs = '<div class="filters">'
    for key, label in _PERIODS:
        active = "active" if period == key else ""
        tabs += f'<a class="filter-btn {active}" href="scores?period={key}{("&p=" + p) if p else ""}">{label}</a>'
    tabs += '</div>'

    rows = ""
    if not data:
        hint = "Noch keine Punkte in diesem Zeitraum." if period != "all" else "Noch keine Punkte vergeben."
        rows = (
            f'<div class="empty">'
            f'<div class="empty-icon">★</div>'
            f'<div style="font-weight:700">{hint}</div>'
            f'<div class="muted" style="font-size:0.8rem">Erledigte Aufgaben und Projektschritte erscheinen hier automatisch.</div>'
            f'</div>'
        )
    else:
        for i, s in enumerate(data):
            rank = f"{i + 1}"
            t_done = s.get("tasks_done", 0)
            pr_done = s.get("project_steps_done", 0)
            me_cls = " is-me" if s["person"] == p else ""
            top_cls = " is-top" if i == 0 else ""
            source_meta = []
            if t_done:
                source_meta.append(f"{t_done} Aufgaben")
            if pr_done:
                source_meta.append(f"{pr_done} Projektschritte")
            source_txt = " · ".join(source_meta) if source_meta else "Noch keine Details"
            rows += f"""
            <div class="score-row-modern{me_cls}{top_cls}">
              <div class="score-rank">{rank}</div>
              <div class="score-main">
                <div class="score-name">{s["person"]}</div>
                <div class="score-meta"><span>{source_txt}</span></div>
              </div>
              <div class="score-points">
                <strong>{s["points"]}</strong>
                <span>Punkte</span>
              </div>
            </div>"""

    note = ""
    if period != "all":
        note = '<div class="muted" style="margin-top:0.5rem;font-size:0.75rem">Nur Aktivitäten seit Einführung des Zeitraum-Trackings werden gezählt.</div>'

    # Persönliche Statistik (nur wenn Person aktiv)
    personal_section = ""
    if p:
        stats = get_person_stats(p)
        cfg = get_person_settings(p)
        recent = get_recent_score_events(p, limit=5)
        goal = cfg.get("weekly_goal", 0)
        rank_all = next((i + 1 for i, s in enumerate(all_time) if s["person"] == p), None)
        rank_month = next((i + 1 for i, s in enumerate(month_data) if s["person"] == p), None)

        streak_txt = f"{stats['streak']} Tag{'e' if stats['streak'] != 1 else ''}" if stats["streak"] else "–"
        streak_hint = "Serie aktiv" if stats["streak"] >= 3 else "Dranbleiben"

        goal_bar = ""
        goal_hint = "Kein Wochenziel gesetzt"
        if goal:
            pct = min(int(stats["week_tasks"] / goal * 100), 100)
            fill_cls = "green" if pct >= 100 else ""
            remaining = max(goal - stats["week_tasks"], 0)
            goal_hint = "Wochenziel erreicht" if remaining == 0 else f"Noch {remaining} Aufgabe{'n' if remaining != 1 else ''} bis zum Ziel"
            goal_bar = f"""
            <div style="margin-top:0.75rem">
              <div style="display:flex;justify-content:space-between;
                          font-size:0.75rem;color:var(--muted);margin-bottom:0.3rem">
                <span>{goal_hint}</span><span>{stats['week_tasks']}/{goal} Aufgaben</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill {fill_cls}" style="width:{pct}%"></div>
              </div>
            </div>"""
        else:
            goal_bar = """
            <div class="muted" style="margin-top:0.75rem;font-size:0.8rem">
              Kein Wochenziel gesetzt. Mit einem Ziel werden Fortschritt und Restaufgaben hier sichtbar.
            </div>"""

        activity_rows = ""
        for event in recent:
            event_type = "Projektschritt" if event.get("type") == "project" else "Aufgabe"
            label = event.get("label") or event_type
            activity_rows += f"""
            <div class="score-activity-row">
              <div class="score-activity-icon">{_icon("check", 15, "var(--success)")}</div>
              <div class="score-activity-main">
                <div class="score-activity-title">{escape(label)}</div>
                <div class="score-activity-meta">{event_type} · {format_date_de(event.get("date", ""))}</div>
              </div>
              <div class="score-activity-points">+{event.get("points", 0)}</div>
            </div>"""
        if not activity_rows:
            activity_rows = (
                '<div class="empty" style="padding:1.25rem 1rem">'
                '<div style="font-weight:700">Noch keine Erfolge sichtbar</div>'
                '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
                'Erledigte Aufgaben erscheinen hier als Verlauf.</div></div>'
            )

        personal_section = f"""
        <div class="hero-card">
          <div class="hero-eyebrow">Dein Fortschritt</div>
          <div class="page-hero">
            <div>
              <div class="hero-title">{p}</div>
              <div class="muted">Jede erledigte Aufgabe zählt sichtbar.</div>
            </div>
            <div class="page-hero-actions">
              <span class="badge ok">#{rank_all or "–"} gesamt</span>
            </div>
          </div>
          {goal_bar}
        </div>
        <div class="achievement-strip">
          <div class="achievement-card">
            <div class="today-value">{stats['week_points']}</div>
            <div class="today-label">Punkte diese Woche</div>
          </div>
          <div class="achievement-card">
            <div class="today-value">{streak_txt}</div>
            <div class="today-label">{streak_hint}</div>
          </div>
          <div class="achievement-card">
            <div class="today-value">#{rank_month or "–"}</div>
            <div class="today-label">Monatsrang</div>
          </div>
        </div>
        <div class="today-grid" style="margin-bottom:1rem">
          <div class="today-stat">
            <div class="today-value">{stats['tasks_done']}</div>
            <div class="today-label">Aufgaben</div>
          </div>
          <div class="today-stat">
            <div class="today-value">{stats['proj_steps']}</div>
            <div class="today-label">Projektschritte</div>
          </div>
          <div class="today-stat">
            <div class="today-value">{stats['total_points']}</div>
            <div class="today-label">Gesamtpunkte</div>
          </div>
        </div>
        <div class="card card-flush score-activity-card">
          <div class="score-activity-head">
            <div>
              <h3>Letzte Erfolge</h3>
              <div class="muted">Was zuletzt Punkte gebracht hat</div>
            </div>
          </div>
          {activity_rows}
        </div>"""

    total_points_period = sum(s.get("points", 0) for s in data)
    total_done_period = sum(s.get("tasks_done", 0) + s.get("project_steps_done", 0) for s in data)
    leader = data[0]["person"] if data else "–"
    content = f"""
    {personal_section}
    <div class="page-header">
      <div>
        <h2>Bestenliste</h2>
        <div class="muted">{total_points_period} Punkte · {total_done_period} Erledigungen · Spitze: {leader}</div>
      </div>
      <div style="color:var(--primary);display:flex;align-items:center">{_icon("star", 22, "var(--primary)")}</div>
    </div>
    {tabs}
    <div class="card card-flush">{rows}</div>
    {note}"""
    return render(content, request, page="scores", person=p)
