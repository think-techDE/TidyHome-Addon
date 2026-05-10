from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from html import escape

from i18n import tr
from render import _icon, format_date_de, person_suffix, render, resolve_person
from storage import (get_person_achievements, get_person_score_history,
                     get_person_settings, get_person_stats,
                     get_recent_score_events, get_scores)

router = APIRouter()

_PERIODS = [
    ("all",        "score.period.all"),
    ("month",      "score.period.month"),
    ("last_month", "score.period.last_month"),
]


@router.get("/scores", response_class=HTMLResponse)
async def scores(request: Request, period: str = "all", p: str = ""):
    p = resolve_person(request, p)
    data = get_scores(period=period)
    all_time = get_scores(period="all")
    month_data = get_scores(period="month")

    tabs = '<div class="filters">'
    for key, label_key in _PERIODS:
        active = "active" if period == key else ""
        tabs += f'<a class="filter-btn {active}" href="scores?period={key}{("&p=" + p) if p else ""}">{tr(label_key)}</a>'
    tabs += '</div>'

    rows = ""
    if not data:
        hint = tr("score.no_points_period") if period != "all" else tr("score.no_points_all")
        rows = (
            f'<div class="empty">'
            f'<div class="empty-icon">★</div>'
            f'<div style="font-weight:700">{hint}</div>'
            f'<div class="muted" style="font-size:0.8rem">{tr("score.auto_hint")}</div>'
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
                source_meta.append(f"{t_done} {tr('tasks.title')}")
            if pr_done:
                source_meta.append(f"{pr_done} {tr('score.project_steps')}")
            source_txt = " · ".join(source_meta) if source_meta else tr("score.no_details")
            rows += f"""
            <div class="score-row-modern{me_cls}{top_cls}">
              <div class="score-rank">{rank}</div>
              <div class="score-main">
                <div class="score-name">{escape(s["person"])}</div>
                <div class="score-meta"><span>{source_txt}</span></div>
              </div>
              <div class="score-points">
                <strong>{s["points"]}</strong>
                <span>{tr("score.points")}</span>
              </div>
            </div>"""

    note = ""
    if period != "all":
        note = f'<div class="muted" style="margin-top:0.5rem;font-size:0.75rem">{tr("score.period_note")}</div>'

    # Persönliche Statistik (nur wenn Person aktiv)
    personal_section = ""
    if p:
        stats = get_person_stats(p)
        cfg = get_person_settings(p)
        recent = get_recent_score_events(p, limit=5)
        achievements = get_person_achievements(p)
        goal = cfg.get("weekly_goal", 0)
        rank_all = next((i + 1 for i, s in enumerate(all_time) if s["person"] == p), None)
        rank_month = next((i + 1 for i, s in enumerate(month_data) if s["person"] == p), None)

        streak_txt = f"{stats['streak']} {tr('score.days') if stats['streak'] != 1 else tr('score.day')}" if stats["streak"] else "–"
        streak_hint = tr("score.streak_active") if stats["streak"] >= 3 else tr("score.keep_going")

        goal_bar = ""
        goal_hint = tr("score.no_weekly_goal")
        if goal:
            pct = min(int(stats["week_tasks"] / goal * 100), 100)
            fill_cls = "green" if pct >= 100 else ""
            remaining = max(goal - stats["week_tasks"], 0)
            task_label = tr("task.task") if remaining == 1 else tr("tasks.title")
            goal_hint = tr("score.weekly_goal_done") if remaining == 0 else f"{tr('score.goal_remaining_prefix')} {remaining} {task_label} {tr('score.goal_remaining_suffix')}"
            goal_bar = f"""
            <div style="margin-top:0.75rem">
              <div style="display:flex;justify-content:space-between;
                          font-size:0.75rem;color:var(--muted);margin-bottom:0.3rem">
                <span>{goal_hint}</span><span>{stats['week_tasks']}/{goal} {tr("tasks.title")}</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill {fill_cls}" style="width:{pct}%"></div>
              </div>
            </div>"""
        else:
            goal_bar = """
            <div class="muted" style="margin-top:0.75rem;font-size:0.8rem">
              """ + tr("score.no_weekly_goal_hint") + """
            </div>"""

        activity_rows = ""
        for event in recent:
            event_type = tr("score.project_step") if event.get("type") == "project" else tr("task.task")
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
                f'<div style="font-weight:700">{tr("score.no_success_title")}</div>'
                '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
                f'{tr("score.no_success_text")}</div></div>'
            )

        unlocked_count = len([a for a in achievements if a["unlocked"]])
        achievement_rows = ""
        for ach in achievements[:6]:
            state = "unlocked" if ach["unlocked"] else "locked"
            icon = "star" if ach["unlocked"] else "flag"
            achievement_rows += f"""
            <div class="mini-achievement {state}">
              <span>{_icon(icon, 15)}</span>
              <div>
                <strong>{escape(ach["title"])}</strong>
                <small>{escape(ach["description"])}</small>
              </div>
            </div>"""

        personal_section = f"""
        <div class="hero-card">
          <div class="hero-eyebrow">{tr("score.progress")}</div>
          <div class="page-hero">
            <div>
              <div class="hero-title">{escape(p)}</div>
              <div class="muted">{tr("score.visible_count_hint")}</div>
            </div>
            <div class="page-hero-actions">
              <span class="badge ok">#{rank_all or "–"} {tr("score.overall")}</span>
              <a class="btn btn-ghost btn-sm" href="scores/history{person_suffix(p)}">
                {_icon("calendar", 14)} {tr("score.history")}
              </a>
            </div>
          </div>
          {goal_bar}
        </div>
        <div class="achievement-strip">
          <div class="achievement-card">
            <div class="today-value">{stats['week_points']}</div>
            <div class="today-label">{tr("score.week_points")}</div>
          </div>
          <div class="achievement-card">
            <div class="today-value">{streak_txt}</div>
            <div class="today-label">{streak_hint}</div>
          </div>
          <div class="achievement-card">
            <div class="today-value">#{rank_month or "–"}</div>
            <div class="today-label">{tr("score.month_rank")}</div>
          </div>
        </div>
        <div class="today-grid" style="margin-bottom:1rem">
          <div class="today-stat">
            <div class="today-value">{stats['tasks_done']}</div>
            <div class="today-label">{tr("tasks.title")}</div>
          </div>
          <div class="today-stat">
            <div class="today-value">{stats['proj_steps']}</div>
            <div class="today-label">{tr("score.project_steps")}</div>
          </div>
          <div class="today-stat">
            <div class="today-value">{stats['total_points']}</div>
            <div class="today-label">{tr("score.total_points")}</div>
          </div>
        </div>
        <div class="card achievement-summary-card">
          <div class="score-activity-head">
            <div>
              <h3>{tr("score.achievements")}</h3>
              <div class="muted">{unlocked_count}/{len(achievements)} {tr("score.unlocked")}</div>
            </div>
            <a class="btn btn-ghost btn-sm" href="scores/history{person_suffix(p)}">{tr("score.view_all")}</a>
          </div>
          <div class="mini-achievement-grid">{achievement_rows}</div>
        </div>
        <div class="card card-flush score-activity-card">
          <div class="score-activity-head">
            <div>
              <h3>{tr("score.recent_success")}</h3>
              <div class="muted">{tr("score.recent_success_hint")}</div>
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
        <h2>{tr("score.leaderboard")}</h2>
        <div class="muted">{total_points_period} {tr("score.points")} · {total_done_period} {tr("score.completions")} · {tr("score.leader")}: {escape(leader)}</div>
      </div>
      <div style="color:var(--primary);display:flex;align-items:center">{_icon("star", 22, "var(--primary)")}</div>
    </div>
    {tabs}
    <div class="card card-flush">{rows}</div>
    {note}"""
    return render(content, request, page="scores", person=p)


def _history_rows(items: list[dict]) -> str:
    max_points = max([i.get("points", 0) for i in items] + [1])
    rows = ""
    for item in items:
        pct = int(item.get("points", 0) / max_points * 100) if max_points else 0
        rows += f"""
        <div class="history-row">
          <div class="history-row-head">
            <strong>{escape(item.get("label", ""))}</strong>
            <span>{item.get("points", 0)} {tr("score.points")} · {item.get("tasks", 0)} {tr("tasks.title")} · {item.get("projects", 0)} {tr("project.projects")}</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill green" style="width:{pct}%"></div>
          </div>
        </div>"""
    return rows


@router.get("/scores/history", response_class=HTMLResponse)
async def score_history(request: Request, p: str = ""):
    p = resolve_person(request, p)
    if not p:
        return render(
            f'<div class="empty"><div style="font-weight:700">{tr("score.no_person")}</div></div>',
            request,
            page="scores",
            person=p,
        )
    stats = get_person_stats(p)
    achievements = get_person_achievements(p)
    history = get_person_score_history(p)
    unlocked = [a for a in achievements if a["unlocked"]]
    locked = [a for a in achievements if not a["unlocked"]]
    achievement_cards = ""
    for ach in unlocked + locked:
        state = "unlocked" if ach["unlocked"] else "locked"
        achievement_cards += f"""
        <div class="achievement-tile {state}">
          <div class="achievement-tile-icon">{_icon("star" if ach["unlocked"] else "flag", 18)}</div>
          <strong>{escape(ach["title"])}</strong>
          <span>{escape(ach["description"])}</span>
        </div>"""

    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">{tr("score.personal_development")}</div>
        <div class="hero-title">{tr("score.history_of")} {escape(p)}</div>
        <div class="muted">{stats["total_points"]} {tr("score.points")} · {stats["tasks_done"]} {tr("tasks.title")} · {stats["proj_steps"]} {tr("score.project_steps")}</div>
      </div>
      <div class="page-hero-actions">
        <a class="btn btn-ghost btn-sm" href="scores{person_suffix(p)}">{_icon("chevron_l", 14)} {tr("score.points")}</a>
      </div>
    </div>
    <div class="card achievement-summary-card">
      <div class="score-activity-head">
        <div>
          <h3>{tr("score.achievements")}</h3>
          <div class="muted">{len(unlocked)}/{len(achievements)} {tr("score.unlocked")}</div>
        </div>
      </div>
      <div class="achievement-tile-grid">{achievement_cards}</div>
    </div>
    <div class="grid-2">
      <div class="card">
        <h3 style="margin-bottom:0.75rem">{tr("score.last_weeks")}</h3>
        {_history_rows(history["weeks"])}
      </div>
      <div class="card">
        <h3 style="margin-bottom:0.75rem">{tr("score.last_months")}</h3>
        {_history_rows(history["months"])}
      </div>
    </div>"""
    return render(content, request, page="scores", person=p)
