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
    admins = set(get_admins())

    # Hidden rooms for active person
    hidden_rooms: set[str] = set()
    if p:
        hidden_rooms = set(get_person_settings(p).get("hidden_rooms", []))
    visible_areas = [r for r in areas if r not in hidden_rooms]

    # Role detection for foreign-room logic
    is_admin = p in admins
    cfg = get_person_settings(p) if p else {}
    is_parent = cfg.get("role") == "parent"
    show_foreign = is_admin or is_parent

    # Own tasks (role-filtered = only assigned to current person)
    own_tasks_raw = list_tasks()
    if hidden_rooms:
        own_tasks_raw = [t for t in own_tasks_raw if t.room not in hidden_rooms]
    own_tasks = filter_tasks_by_role(own_tasks_raw, p, admins)

    # Own projects (filtered to current person)
    own_projects_raw = list_projects()
    if hidden_rooms:
        own_projects_raw = [pr for pr in own_projects_raw if pr.room not in hidden_rooms]
    if p:
        own_projects = [
            pr for pr in own_projects_raw
            if pr.assigned_to == p
            or any((s.assigned_to or pr.assigned_to or "") == p
                   for s in list_steps(pr.id))
        ]
    else:
        own_projects = own_projects_raw

    # For ring-chart stats use own_tasks
    all_tasks = own_tasks
    overdue_tasks = [t for t in all_tasks if t.days_until_due() < 0]
    due_today     = [t for t in all_tasks if t.days_until_due() == 0]
    done_today    = [t for t in all_tasks if t.last_done == today]

    total = len(all_tasks)
    health_pct   = int((total - len(overdue_tasks)) / total * 100) if total else 100
    done_of_due  = len(due_today) + len(done_today)
    done_pct     = int(len(done_today) / done_of_due * 100) if done_of_due else 100

    greeting = f"Hallo{' ' + p if p else ''}!"

    # ── Ring-Charts ─────────────────────────────────────────────────────────
    done_color    = "var(--success)" if len(done_today) >= done_of_due else "var(--primary)"
    overdue_color = "var(--danger)"  if overdue_tasks else "var(--success)"
    health_color  = ("var(--success)" if health_pct > 80
                     else "var(--warning)" if health_pct > 50
                     else "var(--danger)")

    ring_done    = _ring_chart(f"{len(done_today)}/{done_of_due}", done_pct, done_color, "Erledigt")
    ring_overdue = _ring_chart(str(len(overdue_tasks)), min(len(overdue_tasks) * 20, 100), overdue_color, "Überfällig")
    ring_health  = _ring_chart(f"{health_pct}%", health_pct, health_color, "Zustand")

    rings_row = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.55rem;margin-bottom:1rem">
      <div class="card" style="padding:1rem 0.5rem;margin-bottom:0">{ring_done}</div>
      <div class="card" style="padding:1rem 0.5rem;margin-bottom:0">{ring_overdue}</div>
      <div class="card" style="padding:1rem 0.5rem;margin-bottom:0">{ring_health}</div>
    </div>"""

    # ── Schnellaktionen ──────────────────────────────────────────────────────
    base = _base(request)
    psuffix_q = f"?p={p}" if p else ""
    plus = _icon("plus", 15)
    quick_actions = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:1rem">
      <a class="btn btn-primary btn-sm"
         href="{base}tasks/new{psuffix_q}"
         style="display:flex;align-items:center;justify-content:center;gap:0.35rem">
        {plus} Aufgabe
      </a>
      <a class="btn btn-outline btn-sm"
         href="{base}projects/new{psuffix_q}"
         style="display:flex;align-items:center;justify-content:center;gap:0.35rem">
        {plus} Projekt
      </a>
    </div>"""

    # ── Nächste Aufgaben ─────────────────────────────────────────────────────
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
                + (f'<input type="hidden" name="return_p" value="{p}">' if p else "")
                + f'<button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>'
                f'</form>'
            )

            task_rows += f"""
            <div class="dash-task{important_cls}">
              {_task_icon(t.name, t.room, icon=t.icon, size=36)}
              <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:center;gap:0.35rem;
                            justify-content:space-between;margin-bottom:0.18rem">
                  <span class="task-name" style="font-size:0.87rem;line-height:1.3">
                    {star}{t.name}
                  </span>
                  <div style="display:flex;align-items:center;gap:0.25rem;flex-shrink:0">
                    {onetime_badge}
                    <span class="badge {badge_cls}" style="font-size:0.65rem">{badge_text}</span>
                  </div>
                </div>
                <div class="task-date">{cal_icon}
                  <span class="task-meta">{date_text}</span>
                </div>
              </div>
              {done_btn}
            </div>"""

        next_tasks_section = f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:0.6rem">
          <h2 style="margin:0;font-size:0.95rem">Nächste Aufgaben</h2>
          <a href="{base}tasks{psuffix_q}" style="font-size:0.78rem;
             color:var(--primary);text-decoration:none;font-weight:600;
             display:flex;align-items:center;gap:0.1rem">
             Alle{chev}
          </a>
        </div>
        <div class="card card-flush" style="margin-bottom:1rem">{task_rows}</div>"""
    else:
        next_tasks_section = f"""
        <div class="card" style="text-align:center;padding:1.5rem;margin-bottom:1rem">
          <div style="font-size:1.8rem;margin-bottom:0.5rem">🎉</div>
          <div style="font-weight:600;font-size:0.9rem">Alles erledigt!</div>
          <div class="muted" style="margin-top:0.25rem">Keine offenen Aufgaben.</div>
        </div>"""

    # ── Räume ermitteln ──────────────────────────────────────────────────────
    # Räume mit eigenen Aufgaben/Projekten
    own_rooms_set = (
        {t.room for t in own_tasks} | {pr.room for pr in own_projects}
    )
    own_room_list = [r for r in visible_areas if r in own_rooms_set]

    # Räume mit nur fremden Aufgaben/Projekten (nur für Admin/Elternteil)
    foreign_room_list: list[str] = []
    if show_foreign and p:
        all_tasks_full = own_tasks_raw          # bereits hidden-rooms-gefiltert, ungefiltert nach Person
        all_proj_full  = own_projects_raw
        foreign_rooms_set = (
            {t.room for t in all_tasks_full if p not in t.assigned_to}
            | {pr.room for pr in all_proj_full if pr.assigned_to != p
               and not any((s.assigned_to or pr.assigned_to or "") == p
                           for s in list_steps(pr.id))}
        ) - own_rooms_set
        foreign_room_list = [r for r in visible_areas if r in foreign_rooms_set]

    def _render_room_row(r: str, tasks_src: list, proj_src: list, muted: bool = False) -> str:
        r_tasks    = [t for t in tasks_src if t.room == r]
        r_projects = [pr for pr in proj_src if pr.room == r]
        r_overdue  = sum(1 for t in r_tasks if t.days_until_due() < 0)
        sub = f"{len(r_tasks)} Aufg." if r_tasks else ""
        if r_projects:
            sub += (" · " if sub else "") + f"{len(r_projects)} Proj."
        badge = (
            f'<span class="badge overdue" style="font-size:0.62rem;margin-right:0.3rem">'
            f'{r_overdue}×</span>'
        ) if r_overdue else ""
        opacity = ' style="opacity:0.72"' if muted else ""
        return (
            f'<a class="room-row" href="{base}tasks?room={r}{("&p=" + p) if p else ""}"{opacity}>'
            f'{_room_icon(r, 40, stored_room_icons)}'
            f'<span style="flex:1;font-weight:600;font-size:0.9rem">{r}</span>'
            f'<span style="font-size:0.74rem;color:var(--muted)">{sub}</span>'
            f'{badge}{chev}'
            f'</a>'
        )

    # ── Räume-Block aufbauen ─────────────────────────────────────────────────
    if own_room_list or foreign_room_list:
        room_block_parts = []

        if own_room_list:
            rows = "".join(
                _render_room_row(r, own_tasks, own_projects)
                for r in own_room_list
            )
            room_block_parts.append(
                f'<h2 style="font-size:0.95rem;margin-bottom:0.6rem">Räume</h2>'
                f'<div class="card card-flush" style="margin-bottom:1rem">{rows}</div>'
            )

        if foreign_room_list:
            # Für fremde Räume alle Tasks/Projekte dieser Räume anzeigen (nicht nur eigene)
            rows = "".join(
                _render_room_row(r, own_tasks_raw, own_projects_raw, muted=True)
                for r in foreign_room_list
            )
            room_block_parts.append(
                f'<h2 style="font-size:0.95rem;margin-bottom:0.6rem;color:var(--muted)">'
                f'Weitere Räume</h2>'
                f'<div class="card card-flush" style="margin-bottom:1rem">{rows}</div>'
            )

        room_block = "".join(room_block_parts)
    else:
        room_block = (
            '<div class="empty"><div class="empty-icon">🏠</div>'
            '<div>Noch keine Aufgaben oder Projekte vorhanden.</div></div>'
        )

    content = f"""
    <h2 style="font-size:1.25rem;font-weight:800;margin-bottom:0.875rem">{greeting}</h2>
    {rings_row}{quick_actions}{next_tasks_section}
    {room_block}"""

    return render(content, request, page="home", person=p)
