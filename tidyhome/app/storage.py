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

    if room:
        rows = table.search(Q.room == room)
    elif assigned_to:
        rows = table.search(Q.assigned_to == assigned_to)
    else:
        rows = table.all()

    tasks = [Task(**r) for r in rows if r.get("active", True)]

    if overdue_only:
        tasks = [t for t in tasks if t.is_overdue()]

    tasks.sort(key=lambda t: t.days_until_due())
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
              assigned_to: str | None, points: int) -> Task | None:
    task = get_task(task_id)
    if not task:
        return None
    task.name = name
    task.room = room
    task.interval_days = interval_days
    task.assigned_to = assigned_to
    task.points = points
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
    person = done_by or task.assigned_to

    if person:
        _add_score(person, task.points, task_type="task")

    return update_task(task)


def _add_score(person: str, points: int, task_type: str = "task"):
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


def get_scores() -> list[dict]:
    table = get_scores_table()
    scores = table.all()
    return sorted(scores, key=lambda s: s["points"], reverse=True)


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
    return step


def delete_step(step_id: str) -> bool:
    Q = Query()
    removed = get_steps_table().remove(Q.id == step_id)
    return len(removed) > 0


def get_settings_table():
    return _db.table("person_settings")


def get_person_settings(person: str) -> dict:
    Q = Query()
    row = get_settings_table().get(Q.person == person)
    return row or {"person": person, "services": [], "notify_time": "08:00", "enabled": False}


def save_person_settings(person: str, services: list[str], notify_time: str, enabled: bool) -> dict:
    Q = Query()
    data = {"person": person, "services": services,
            "notify_time": notify_time, "enabled": enabled}
    if get_settings_table().get(Q.person == person):
        get_settings_table().update(data, Q.person == person)
    else:
        get_settings_table().insert(data)
    return data


def list_person_settings() -> list[dict]:
    return get_settings_table().all()
