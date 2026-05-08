from tinydb import TinyDB, Query
from models import Comment, Project, Step, Task
from datetime import date, datetime
import os

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "tidyhome.json")

os.makedirs(DATA_DIR, exist_ok=True)
_db = TinyDB(DB_PATH)


def get_tasks_table():
    return _db.table("tasks")


def get_scores_table():
    return _db.table("scores")


def get_comments_table():
    return _db.table("comments")


def list_tasks(room: str = None, assigned_to: str = None, overdue_only: bool = False,
               effort: str = None) -> list[Task]:
    table = get_tasks_table()
    Q = Query()

    rows = table.search(Q.room == room) if room else table.all()
    tasks = [Task(**r) for r in rows if r.get("active", True)]

    # Aufgaben mit Startdatum in der Zukunft ausblenden
    today = date.today().isoformat()
    tasks = [t for t in tasks if not t.start_date or t.start_date <= today]

    # assigned_to ist jetzt eine Liste – Python-seitig filtern
    if assigned_to:
        tasks = [t for t in tasks if assigned_to in t.assigned_to]

    if overdue_only:
        tasks = [t for t in tasks if t.is_overdue()]

    if effort:
        tasks = [t for t in tasks if t.effort == effort]

    tasks.sort(key=lambda t: (not t.important, t.days_until_due()))
    return tasks


def get_task(task_id: str) -> Task | None:
    table = get_tasks_table()
    Q = Query()
    row = table.get(Q.id == task_id)
    return Task(**row) if row else None


def create_task(task: Task) -> Task:
    table = get_tasks_table()
    table.insert(task.model_dump())
    return task


def update_task(task: Task) -> Task:
    table = get_tasks_table()
    Q = Query()
    table.update(task.model_dump(), Q.id == task.id)
    return task


def edit_task(task_id: str, name: str, room: str, interval_days: int,
              assigned_to: list[str], points: int,
              important: bool = False, onetime: bool = False,
              icon: str = "", effort: str = "",
              start_date: str = "", snooze_until: str = "") -> Task | None:
    task = get_task(task_id)
    if not task:
        return None
    task.name = name
    task.room = room
    task.interval_days = interval_days
    task.assigned_to = assigned_to
    task.points = points
    task.important = important
    task.onetime = onetime
    task.icon = icon
    task.effort = effort
    task.start_date = start_date or None
    task.snooze_until = snooze_until or None
    return update_task(task)


def snooze_task(task_id: str, until_date: str) -> Task | None:
    """Verschiebt die Fälligkeit einer Aufgabe einmalig auf until_date."""
    task = get_task(task_id)
    if not task:
        return None
    task.snooze_until = until_date or None
    return update_task(task)


def delete_task(task_id: str) -> bool:
    table = get_tasks_table()
    Q = Query()
    removed = table.remove(Q.id == task_id)
    return len(removed) > 0


def mark_done(task_id: str, done_by: str = None, done_at: str = None) -> Task | None:
    task = get_task(task_id)
    if not task:
        return None

    done_date = done_at or date.today().isoformat()
    task.last_done = done_date
    task.snooze_until = None  # Snooze nach Erledigung aufheben
    person = done_by or (task.assigned_to[0] if task.assigned_to else None)

    if person:
        _add_score(person, task.points, task_type="task")

    # Einmalige Aufgaben nach Erledigung archivieren
    if task.onetime:
        task.active = False

    return update_task(task)


def _add_score(person: str, points: int, task_type: str = "task"):
    # Gesamtpunkte aktualisieren
    table = get_scores_table()
    Q = Query()
    row = table.get(Q.person == person)
    if row:
        update = {"points": row["points"] + points}
        if task_type == "project":
            update["project_steps_done"] = row.get("project_steps_done", 0) + 1
        else:
            update["tasks_done"] = row.get("tasks_done", 0) + 1
        table.update(update, Q.person == person)
    else:
        entry = {"person": person, "points": points,
                 "tasks_done": 0, "project_steps_done": 0}
        if task_type == "project":
            entry["project_steps_done"] = 1
        else:
            entry["tasks_done"] = 1
        table.insert(entry)
    # Einzelnen Eintrag ins Log schreiben (für Zeitraum-Auswertung)
    _db.table("score_log").insert({
        "person": person,
        "points": points,
        "type": task_type,
        "date": date.today().isoformat(),
    })


def get_scores(period: str = "all") -> list[dict]:
    if period == "all":
        scores = get_scores_table().all()
        return sorted(scores, key=lambda s: s["points"], reverse=True)

    # Zeitraum-Filterung über score_log
    today = date.today()
    if period == "month":
        from_date = today.replace(day=1).isoformat()
        to_date = None
    elif period == "last_month":
        if today.month == 1:
            from_date = date(today.year - 1, 12, 1).isoformat()
            to_date = date(today.year, 1, 1).isoformat()
        else:
            from_date = date(today.year, today.month - 1, 1).isoformat()
            to_date = today.replace(day=1).isoformat()
    else:
        from_date = None
        to_date = None

    log = _db.table("score_log").all()
    entries = [
        e for e in log
        if (from_date is None or e["date"] >= from_date)
        and (to_date is None or e["date"] < to_date)
    ]

    agg: dict[str, dict] = {}
    for e in entries:
        p = e["person"]
        if p not in agg:
            agg[p] = {"person": p, "points": 0, "tasks_done": 0, "project_steps_done": 0}
        agg[p]["points"] += e["points"]
        if e.get("type") == "project":
            agg[p]["project_steps_done"] += 1
        else:
            agg[p]["tasks_done"] += 1

    return sorted(agg.values(), key=lambda s: s["points"], reverse=True)


def get_projects_table():
    return _db.table("projects")


def get_steps_table():
    return _db.table("project_steps")


def list_projects(room: str = None, assigned_to: str = None) -> list[Project]:
    Q = Query()
    table = get_projects_table()
    if room:
        rows = table.search((Q.room == room) & (Q.active == True))
    elif assigned_to:
        rows = table.search((Q.assigned_to == assigned_to) & (Q.active == True))
    else:
        rows = table.search(Q.active == True)
    return [Project(**r) for r in rows]


def get_project(project_id: str) -> Project | None:
    Q = Query()
    row = get_projects_table().get(Q.id == project_id)
    return Project(**row) if row else None


def create_project(project: Project) -> Project:
    get_projects_table().insert(project.model_dump())
    return project


def update_project(project: Project) -> Project:
    Q = Query()
    get_projects_table().update(project.model_dump(), Q.id == project.id)
    return project


def delete_project(project_id: str) -> bool:
    Q = Query()
    get_projects_table().update({"active": False}, Q.id == project_id)
    return True


def list_steps(project_id: str) -> list[Step]:
    Q = Query()
    rows = get_steps_table().search(Q.project_id == project_id)
    return [Step(**r) for r in rows]


def get_step(step_id: str) -> Step | None:
    Q = Query()
    row = get_steps_table().get(Q.id == step_id)
    return Step(**row) if row else None


def add_step(step: Step) -> Step:
    get_steps_table().insert(step.model_dump())
    return step


def assign_step(step_id: str, assigned_to: str = None) -> Step | None:
    step = get_step(step_id)
    if not step:
        return None
    step.assigned_to = assigned_to or None
    Q = Query()
    get_steps_table().update(step.model_dump(), Q.id == step_id)
    return step


def complete_step(step_id: str, done_by: str = None) -> Step | None:
    step = get_step(step_id)
    if not step or step.completed:
        return step
    step.completed = True
    step.completed_by = done_by or step.assigned_to
    step.completed_at = date.today().isoformat()
    Q = Query()
    get_steps_table().update(step.model_dump(), Q.id == step_id)
    if step.completed_by:
        _add_score(step.completed_by, step.points, task_type="project")
    # Projekt auto-abschließen wenn alle Schritte erledigt
    all_steps = list_steps(step.project_id)
    if all_steps and all(s.completed for s in all_steps):
        proj = get_project(step.project_id)
        if proj and not proj.completed:
            proj.completed = True
            update_project(proj)
    return step


def delete_step(step_id: str) -> bool:
    Q = Query()
    removed = get_steps_table().remove(Q.id == step_id)
    return len(removed) > 0


def list_comments(entity_type: str, entity_id: str) -> list[Comment]:
    Q = Query()
    rows = get_comments_table().search(
        (Q.entity_type == entity_type) & (Q.entity_id == entity_id)
    )
    comments = [Comment(**r) for r in rows]
    comments.sort(key=lambda c: c.created_at)
    return comments


def add_comment(entity_type: str, entity_id: str, text: str,
                author: str = "") -> Comment | None:
    clean_text = text.strip()
    if not clean_text:
        return None
    comment = Comment(
        entity_type=entity_type,
        entity_id=entity_id,
        text=clean_text,
        author=author or None,
        created_at=datetime.now().isoformat(),
    )
    get_comments_table().insert(comment.model_dump())
    return comment


def get_settings_table():
    return _db.table("person_settings")


# Verfügbare Rollen
ROLES = {
    "parent":      "Elternteil",
    "child":       "Kind",
    "housekeeper": "Haushaltshilfe",
    "member":      "Mitglied",
}


def get_person_settings(person: str) -> dict:
    Q = Query()
    row = get_settings_table().get(Q.person == person)
    return row or {"person": person, "services": [], "notify_time": "08:00",
                   "enabled": False, "hidden_rooms": [], "weekly_goal": 0,
                   "role": "member", "can_see_children": False,
                   "vacation_enabled": False, "vacation_until": ""}


def save_person_settings(person: str, services: list[str], notify_time: str,
                         enabled: bool, hidden_rooms: list[str] | None = None,
                         weekly_goal: int = 0, role: str = "member",
                         can_see_children: bool = False,
                         vacation_enabled: bool = False,
                         vacation_until: str = "") -> dict:
    Q = Query()
    data = {"person": person, "services": services,
            "notify_time": notify_time, "enabled": enabled,
            "hidden_rooms": hidden_rooms or [], "weekly_goal": weekly_goal,
            "role": role, "can_see_children": can_see_children,
            "vacation_enabled": vacation_enabled,
            "vacation_until": vacation_until or ""}
    if get_settings_table().get(Q.person == person):
        get_settings_table().update(data, Q.person == person)
    else:
        get_settings_table().insert(data)
    return data


def list_people_by_role(role: str) -> set[str]:
    return {
        row["person"] for row in get_settings_table().all()
        if row.get("role") == role
    }


def filter_tasks_by_role(tasks: list, person: str, admins: set[str]) -> list:
    """Filtert Aufgaben nach Rolle der Person.
    Standardansichten sind persönlich; Admin-Rechte werden in expliziten
    Gruppierungsansichten ausgewertet.
    Kind mit Berechtigung: eigene + andere Kinder.
    Sonst: nur eigene."""
    if not person:
        return tasks
    cfg = get_person_settings(person)
    role = cfg.get("role", "member")
    if role == "child" and cfg.get("can_see_children"):
        child_persons = list_people_by_role("child")
        return [t for t in tasks
                if person in t.assigned_to
                or any(p in child_persons for p in t.assigned_to)]
    # member / housekeeper / child ohne Berechtigung
    return [t for t in tasks if person in t.assigned_to]


def get_person_stats(person: str) -> dict:
    """Persönliche Statistik aus score_log: Streak, Woche, Gesamt."""
    from datetime import timedelta
    log = _db.table("score_log").all()
    plog = [e for e in log if e["person"] == person]

    total_points = sum(e["points"] for e in plog)
    tasks_done = sum(1 for e in plog if e.get("type") != "project")
    proj_steps = sum(1 for e in plog if e.get("type") == "project")

    today = date.today()
    week_start = (today - timedelta(days=today.weekday())).isoformat()
    wlog = [e for e in plog if e["date"] >= week_start]
    week_points = sum(e["points"] for e in wlog)
    week_tasks = sum(1 for e in wlog if e.get("type") != "project")

    # Streak: aufeinanderfolgende Tage mit mindestens einer Erledigung
    active_dates = sorted(set(e["date"] for e in plog), reverse=True)
    streak = 0
    if active_dates:
        yesterday = (today - timedelta(days=1)).isoformat()
        if active_dates[0] >= yesterday:
            expected = date.fromisoformat(active_dates[0])
            for d_str in active_dates:
                d = date.fromisoformat(d_str)
                if d == expected:
                    streak += 1
                    expected = d - timedelta(days=1)
                else:
                    break

    return {
        "total_points": total_points,
        "tasks_done": tasks_done,
        "proj_steps": proj_steps,
        "week_points": week_points,
        "week_tasks": week_tasks,
        "streak": streak,
    }


def list_person_settings() -> list[dict]:
    return get_settings_table().all()


# ── App-weite Einstellungen (Admins) ───────────────────────────────────────

def _get_app_table():
    return _db.table("app_settings")


def _get_app_value(key: str, default=None):
    Q = Query()
    row = _get_app_table().get(Q.key == key)
    return row.get("value") if row else default


def _save_app_value(key: str, value) -> None:
    Q = Query()
    data = {"key": key, "value": value}
    if _get_app_table().get(Q.key == key):
        _get_app_table().update(data, Q.key == key)
    else:
        _get_app_table().insert(data)


def get_admins() -> set[str]:
    return set(_get_app_value("admins", []))


def save_admins(persons: list[str]) -> None:
    _save_app_value("admins", sorted(persons))


def get_room_icons() -> dict[str, str]:
    """Returns {room_name: icon_key} for rooms with custom icon assignment."""
    return dict(_get_app_value("room_icons", {}))


def save_room_icons(icons: dict[str, str]) -> None:
    _save_app_value("room_icons", icons)


def get_vacation_mode(person: str = "") -> dict:
    if person:
        cfg = get_person_settings(person)
        return {
            "enabled": bool(cfg.get("vacation_enabled")),
            "until": cfg.get("vacation_until") or "",
        }
    cfg = _get_app_value("vacation_mode", {}) or {}
    return {
        "enabled": bool(cfg.get("enabled")),
        "until": cfg.get("until") or "",
    }


def save_vacation_mode(enabled: bool, until: str = "") -> None:
    _save_app_value("vacation_mode", {
        "enabled": bool(enabled),
        "until": until or "",
    })


def is_vacation_mode_active(person: str = "") -> bool:
    cfg = get_vacation_mode(person)
    if not cfg.get("enabled"):
        return False
    until = cfg.get("until") or ""
    if not until:
        return True
    try:
        return date.fromisoformat(until) >= date.today()
    except ValueError:
        return False
