from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ha_client import get_areas
from render import _base, _icon, _ring_chart, _room_icon, _task_icon, render, resolve_person
from storage import (filter_tasks_by_role, get_admins, get_person_settings,
                     get_room_icons, list_projects, list_steps, list_tasks)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, p: str = ""):
    p = resolve_person(request, p)
    areas = await get_areas()
    stored_room_icons = get_room_icons()
    today = date.today().isoformat()

    # Hidden rooms for active person
    hidden_rooms: set[str] = set()
    if p:
        hidden_rooms = set(get_person_settings(p).get("hidden_rooms", []))
    visible_areas = [r for r in areas if r not in hidden_rooms]

    all_tasks = list_tasks()
    if hidden_rooms:
        all_tasks = [t for t in all_tasks if t.room not in hidden_rooms]
    all_tasks = filter_tasks_by_role(all_tasks, p, set(get_admins()))
    overdue_tasks = [t for t in all_tasks if t.days_until_due() < 0]
    due_today     = [t for t in all_tasks if t.days_until_due() == 0]
    done_today    = [t for t in all_tasks if t.last_done == today]
    all_projects  = list_projects()
    if hidden_rooms:
        all_projects = [pr for pr in all_projects if pr.room not in hidden_rooms]
    if p:
        all_projects = [
            pr for pr in all_projects
            if pr.assigned_to == p
            or any((s.assigned_to or pr.assigned_to or "") == p
                   for s in list_steps(pr.id))
        ]

    total = len(all_tasks)
    health_pct   = int((total - len(overdue_tasks)) / total * 100) if total else 100
    done_of_due  = len(due_today) + len(done_today)
    done_pct     = int(len(done_today) / done_of_due * 100) if done_of_due else 100

    greeting = f"Hallo{' ' + p if p else ''}!"

    # ── 3 Ring-Charts ───────────────────────────────────────────────────────
    done_color    = "var(--success)" if len(done_today) >= done_of_due else "var(--primary)"
    overdue_color = "var(--danger)"  if overdue_tasks else "var(--success)"
    health_color  = "var(--success)" if health_pct > 80 else "var(--warning)" if health_pct > 50 else "var(--danger)"

    ring_done    = _ring_chart(
        f"{len(done_today)}/{done_of_due}",
        done_pct, done_color, "Erledigt"
    )
    ring_overdue = _ring_chart(
        str(len(overdue_tasks)),
        min(len(overdue_tasks) * 20, 100), overdue_color, "Überfällig"
    )
    ring_health  = _ring_chart(
        f"{health_pct}%",
        health_pct, health_color, "Zustand"
    )

    rings_row = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.55rem;margin-bottom:1rem">
      <div class="card" style="padding:1rem 0.5rem;margin-bottom:0">{ring_done}</div>
      <div class="card" style="padding:1rem 0.5rem;margin-bottom:0">{ring_overdue}</div>
      <div class="card" style="padding:1rem 0.5rem;margin-bottom:0">{ring_health}</div>
    </div>"""

    # ── Nächste Aufgaben ─────────────────────────────────────────────────────
    base = _base(request)
    upcoming = sorted(all_tasks, key=lambda t: t.days_until_due())[:5]
    cal_icon = _icon("calendar", 13, "var(--muted)")
    chev     = _icon("chevron_r", 16, "var(--muted)")

    if upcoming:
        task_rows = ""
        for t in upcoming:
            d = t.days_until_due()
            if d < 0:
                badge_text, badge_cls = "Überfällig", "overdue"
                date_text = f"{abs(d)}d überfällig"
            elif d == 0:
                badge_text, badge_cls = "Heute", "today"
                date_text = "Heute"
            else:
                badge_text, badge_cls = "Geplant", "ok"
                date_text = "Morgen" if d == 1 else f"In {d} Tagen"

            important_cls = " important" if t.important else ""
            star = _icon("star", 13, "var(--warning)", 2.5) if t.important else ""
            onetime_badge = (
                '<span class="badge" style="background:var(--muted);color:#fff;'
                'font-size:0.62rem;flex-shrink:0">1×</span>'
            ) if t.onetime else ""

            done_btn = (
                f'<form class="inline" method="post" action="{base}tasks/{t.id}/done">'
                + (f'<input type="hidden" name="done_by" value="{p}">' if p else "")
                + f'<button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>'
                f'</form>'
            )

            task_rows += f"""
            <div class="task-row{important_cls}">
              {_task_icon(t.name, t.room, icon=t.icon)}
              <div class="task-body">
                <div class="task-header">
                  <span class="task-name">{star}{t.name}</span>
                  <div style="display:flex;align-items:center;gap:0.3rem;flex-shrink:0">
                    {onetime_badge}
                    <span class="badge {badge_cls}">{badge_text}</span>
                  </div>
                </div>
                <div class="task-date">{cal_icon}
                  <span class="task-meta">{date_text}</span>
                </div>
                <div class="task-actions">{done_btn}</div>
              </div>
            </div>"""

        next_tasks_section = f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:0.6rem">
          <h2 style="margin:0;font-size:0.95rem">Nächste Aufgaben</h2>
          <a href="{base}tasks{('?p=' + p) if p else ''}" style="font-size:0.78rem;
             color:var(--primary);text-decoration:none;font-weight:600;
             display:flex;align-items:center;gap:0.1rem">
             Alle{chev}
          </a>
        </div>
        <div class="card card-flush list-card" style="margin-bottom:1rem">{task_rows}</div>"""
    else:
        next_tasks_section = f"""
        <div class="card" style="text-align:center;padding:1.5rem;margin-bottom:1rem">
          <div style="font-size:1.8rem;margin-bottom:0.5rem">🎉</div>
          <div style="font-weight:600;font-size:0.9rem">Alles erledigt!</div>
          <div class="muted" style="margin-top:0.25rem">Keine offenen Aufgaben.</div>
        </div>"""

    # ── Räume als Liste ──────────────────────────────────────────────────────
    if visible_areas:
        room_rows = ""
        for r in visible_areas:
            r_tasks    = [t for t in all_tasks if t.room == r]
            r_projects = [pr for pr in all_projects if pr.room == r]
            r_overdue  = sum(1 for t in r_tasks if t.days_until_due() < 0)
            sub = f"{len(r_tasks)} Aufg."
            if r_projects: sub += f" · {len(r_projects)} Proj."
            badge = (
                f'<span class="badge overdue" style="font-size:0.62rem;margin-right:0.3rem">'
                f'{r_overdue}×</span>'
            ) if r_overdue else ""
            room_rows += f"""
            <a class="room-row" href="{base}tasks?room={r}{('&p=' + p) if p else ''}">
              {_room_icon(r, 40, stored_room_icons)}
              <span style="flex:1;font-weight:600;font-size:0.9rem">{r}</span>
              <span style="font-size:0.74rem;color:var(--muted)">{sub}</span>
              {badge}
              {chev}
            </a>"""
        room_block = (
            f'<h2 style="font-size:0.95rem;margin-bottom:0.6rem">Räume</h2>'
            f'<div class="card card-flush list-card">{room_rows}</div>'
        )
    else:
        room_block = (
            '<div class="empty"><div class="empty-icon">🏠</div>'
            '<div>Noch keine Räume in Home Assistant konfiguriert.</div></div>'
        )

    content = f"""
    <h2 style="font-size:1.25rem;font-weight:800;margin-bottom:0.875rem">{greeting}</h2>
    {rings_row}{next_tasks_section}
    {room_block}"""

    return render(content, request, page="home", person=p)
