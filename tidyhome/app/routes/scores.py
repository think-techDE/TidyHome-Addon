from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from render import render
from storage import get_scores

router = APIRouter()


@router.get("/scores", response_class=HTMLResponse)
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
