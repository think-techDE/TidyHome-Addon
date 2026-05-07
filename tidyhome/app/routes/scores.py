from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from render import render
from storage import get_scores

router = APIRouter()

_PERIODS = [
    ("all",        "Gesamt"),
    ("month",      "Dieser Monat"),
    ("last_month", "Letzter Monat"),
]


@router.get("/scores", response_class=HTMLResponse)
async def scores(request: Request, period: str = "all", p: str = ""):
    data = get_scores(period=period)

    tabs = '<div class="filters">'
    for key, label in _PERIODS:
        active = "active" if period == key else ""
        tabs += f'<a class="filter-btn {active}" href="scores?period={key}">{label}</a>'
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
            rows += f"""
            <div class="score-row">
              <span style="font-size:1.2rem;min-width:1.5rem">{medal}</span>
              <span class="score-name">{s["person"]}</span>
              <span class="task-meta">{t_done} Aufg. · {pr_done} Schritte</span>
              <span class="score-pts">{s["points"]} Pkt</span>
            </div>"""

    note = ""
    if period != "all":
        note = '<div class="muted" style="margin-top:0.5rem;font-size:0.75rem">Nur Aktivitäten seit Einführung des Zeitraum-Trackings werden gezählt.</div>'

    content = f"""
    <h2>Bestenliste</h2>
    {tabs}
    <div class="card card-flush" style="padding:0 1.25rem">{rows}</div>
    {note}"""
    return render(content, request, page="scores", person=p)
