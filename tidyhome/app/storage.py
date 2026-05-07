from tinydb import TinyDB, Query
from models import Task, Project, Step
from datetime import date
import os

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "tidyhome.json")

os.makedirs(DATA_DIR, exist_ok=True)
_db = TinyDB(DB_PATH)


def get_tasks_table():
    return _db.table("tasks")


def get_scores_table():
    return _db.table("scores")


def list_tasks(room: str = None, assigned_to: str = None, overdue_only: bool = False) -> list[Task]:
    table = get_tasks_table()
    Q = Query()

    rows = table.search(Q.room == room) if room else table.all()
    tasks = [Task(**r) for r in rows if r.get("active", True)]

    # assigned_to ist jetzt eine Liste – Python-seitig filtern
    if assigned_to:
        tasks = [t for t in tasks if assigned_to in t.assigned_to]

    if overdue_only:
        tasks = [t for t in tasks if t.is_overdue()]

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
              important: bool = False, onetime: bool = False) -> Task | None:
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


def complete_step(step_id: str, done_by: str = None) -> Step | None:
    step = get_step(step_id)
    if not step or step.completed:
        return step
    step.completed = True
    step.completed_by = done_by
    step.completed_at = date.today().isoformat()
    Q = Query()
    get_steps_table().update(step.model_dump(), Q.id == step_id)
    if done_by:
        _add_score(done_by, step.points, task_type="project")
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
                   "role": "member", "can_see_children": False}


def save_person_settings(person: str, services: list[str], notify_time: str,
                         enabled: bool, hidden_rooms: list[str] | None = None,
                         weekly_goal: int = 0, role: str = "member",
                         can_see_children: bool = False) -> dict:
    Q = Query()
    data = {"person": person, "services": services,
            "notify_time": notify_time, "enabled": enabled,
            "hidden_rooms": hidden_rooms or [], "weekly_goal": weekly_goal,
            "role": role, "can_see_children": can_see_children}
    if get_settings_table().get(Q.person == person):
        get_settings_table().update(data, Q.person == person)
    else:
        get_settings_table().insert(data)
    return data


def filter_tasks_by_role(tasks: list, person: str, admins: set[str]) -> list:
    """Filtert Aufgaben nach Rolle der Person.
    Parent/Admin: alles. Kind mit Berechtigung: eigene + andere Kinder.
    Sonst: nur eigene + nicht zugeordnete."""
    if not person:
        return tasks
    if person in admins:
        return tasks
    cfg = get_person_settings(person)
    role = cfg.get("role", "member")
    if role == "parent":
        return tasks
    if role == "child" and cfg.get("can_see_children"):
        child_persons = {
            r["person"] for r in get_settings_table().all()
            if r.get("role") == "child"
        }
        return [t for t in tasks
                if not t.assigned_to or person in t.assigned_to
                or any(p in child_persons for p in t.assigned_to)]
    # member / housekeeper / child ohne Berechtigung
    return [t for t in tasks if not t.assigned_to or person in t.assigned_to]


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


def get_admins() -> set[str]:
    Q = Query()
    row = _get_app_table().get(Q.key == "admins")
    return set(row["value"]) if row else set()


def save_admins(persons: list[str]) -> None:
    Q = Query()
    data = {"key": "admins", "value": sorted(persons)}
    if _get_app_table().get(Q.key == "admins"):
        _get_app_table().update(data, Q.key == "admins")
    else:
        _get_app_table().insert(data)
