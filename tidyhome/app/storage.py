from tinydb import TinyDB, Query
from models import Task
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
        _add_score(person, task.points)

    return update_task(task)


def _add_score(person: str, points: int):
    table = get_scores_table()
    Q = Query()
    row = table.get(Q.person == person)
    if row:
        table.update(
            {"points": row["points"] + points, "tasks_done": row["tasks_done"] + 1},
            Q.person == person
        )
    else:
        table.insert({"person": person, "points": points, "tasks_done": 1})


def get_scores() -> list[dict]:
    table = get_scores_table()
    scores = table.all()
    return sorted(scores, key=lambda s: s["points"], reverse=True)
