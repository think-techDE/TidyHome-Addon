from datetime import date, datetime
import os
import uuid

from tinydb import Query

from models import Comment, Task
from storage_runtime import MAX_PHOTO_BYTES, PHOTO_DIR, _db
from storage_people import _add_score


def get_tasks_table():
    return _db.table("tasks")


def get_comments_table():
    return _db.table("comments")


def get_photos_table():
    return _db.table("photos")


def get_task_templates_table():
    return _db.table("task_templates")


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
        tasks = [t for t in tasks if not t.is_paused() and t.is_overdue()]

    if effort:
        tasks = [t for t in tasks if t.effort == effort]

    tasks.sort(key=lambda t: (t.is_paused(), not t.important, t.days_until_due()))
    return tasks


def list_task_history() -> list[Task]:
    table = get_tasks_table()
    tasks = [
        Task(**row)
        for row in table.all()
        if row.get("last_done") or not row.get("active", True)
    ]
    tasks.sort(
        key=lambda t: (t.last_done or t.created_at[:10], t.created_at),
        reverse=True,
    )
    return tasks


def list_task_templates() -> list[dict]:
    rows = get_task_templates_table().all()
    rows.sort(key=lambda r: (r.get("name", "").casefold(), r.get("created_at", "")))
    return rows


def get_task_template(template_id: str) -> dict | None:
    Q = Query()
    row = get_task_templates_table().get(Q.id == template_id)
    return dict(row) if row else None


def save_task_template(name: str, task_name: str, room: str,
                       interval_days: int, assigned_to: list[str],
                       points: int = 10, important: bool = False,
                       onetime: bool = True, icon: str = "",
                       effort: str = "") -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "name": (name or task_name or "Neue Vorlage").strip(),
        "task_name": (task_name or name or "Neue Aufgabe").strip(),
        "room": room,
        "interval_days": max(int(interval_days or 0), 0),
        "assigned_to": assigned_to or [],
        "points": max(int(points or 1), 1),
        "important": bool(important),
        "onetime": bool(onetime),
        "icon": icon or "",
        "effort": effort or "",
        "created_at": datetime.now().isoformat(),
    }
    get_task_templates_table().insert(row)
    return row


def update_task_template(template_id: str, name: str, task_name: str, room: str,
                         interval_days: int, assigned_to: list[str],
                         points: int = 10, important: bool = False,
                         onetime: bool = True, icon: str = "",
                         effort: str = "") -> dict | None:
    row = get_task_template(template_id)
    if not row:
        return None
    updated = dict(row)
    updated.update({
        "name": (name or task_name or row.get("name") or "Vorlage").strip(),
        "task_name": (task_name or name or row.get("task_name") or "Neue Aufgabe").strip(),
        "room": room,
        "interval_days": max(int(interval_days or 0), 0),
        "assigned_to": assigned_to or [],
        "points": max(int(points or 1), 1),
        "important": bool(important),
        "onetime": bool(onetime),
        "icon": icon or "",
        "effort": effort or "",
        "updated_at": datetime.now().isoformat(),
    })
    Q = Query()
    get_task_templates_table().update(updated, Q.id == template_id)
    return updated


def delete_task_template(template_id: str) -> bool:
    Q = Query()
    return bool(get_task_templates_table().remove(Q.id == template_id))


def create_task_from_template(template_id: str, assigned_to: list[str] | None = None,
                              start_date: str = "") -> Task | None:
    row = get_task_template(template_id)
    if not row:
        return None
    assignees = assigned_to if assigned_to is not None else row.get("assigned_to", [])
    task = Task(
        name=row.get("task_name") or row.get("name", "Neue Aufgabe"),
        room=row.get("room", ""),
        interval_days=int(row.get("interval_days", 0) or 0),
        assigned_to=assignees or [],
        points=int(row.get("points", 10) or 10),
        important=bool(row.get("important")),
        onetime=bool(row.get("onetime", True)),
        icon=row.get("icon", ""),
        effort=row.get("effort", ""),
        start_date=start_date or None,
    )
    return create_task(task)


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
              start_date: str = "", snooze_until: str = "",
              paused: bool = False, pause_until: str = "",
              pause_reason: str = "") -> Task | None:
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
    task.paused = bool(paused)
    task.pause_until = pause_until or None
    task.pause_reason = pause_reason.strip() or None
    return update_task(task)


def snooze_task(task_id: str, until_date: str) -> Task | None:
    """Verschiebt die Fälligkeit einer Aufgabe einmalig auf until_date."""
    task = get_task(task_id)
    if not task:
        return None
    task.snooze_until = until_date or None
    return update_task(task)


def pause_task(task_id: str, paused: bool = True,
               pause_until: str = "", reason: str = "") -> Task | None:
    task = get_task(task_id)
    if not task:
        return None
    task.paused = bool(paused)
    task.pause_until = pause_until or None if paused else None
    task.pause_reason = reason.strip() or None if paused else None
    return update_task(task)


def reactivate_task(task_id: str) -> Task | None:
    task = get_task(task_id)
    if not task:
        return None
    task.active = True
    task.last_done = None
    task.snooze_until = None
    task.paused = False
    task.pause_until = None
    task.pause_reason = None
    if task.onetime:
        task.start_date = date.today().isoformat()
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
    task.paused = False
    task.pause_until = None
    task.pause_reason = None
    person = done_by or (task.assigned_to[0] if task.assigned_to else None)

    if person:
        _add_score(person, task.points, task_type="task",
                   label=task.name, source_id=task.id)

    # Einmalige Aufgaben nach Erledigung archivieren
    if task.onetime:
        task.active = False

    return update_task(task)


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


def _photo_extension(filename: str, content_type: str = "") -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    if ext in allowed:
        return ext
    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    if content_type == "image/gif":
        return ".gif"
    return ".jpg"


def add_photo(entity_type: str, entity_id: str, photo_type: str,
              filename: str, content_type: str, data: bytes,
              author: str = "") -> dict | None:
    if entity_type not in {"task", "project", "step"}:
        return None
    if photo_type not in {"before", "after"}:
        photo_type = "before"
    if not data:
        return None
    if len(data) > MAX_PHOTO_BYTES:
        return None
    if content_type and not content_type.startswith("image/"):
        return None
    ext = _photo_extension(filename, content_type)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(PHOTO_DIR, stored_name)
    with open(path, "wb") as handle:
        handle.write(data)
    row = {
        "id": str(uuid.uuid4()),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "photo_type": photo_type,
        "filename": stored_name,
        "original_name": filename or stored_name,
        "content_type": content_type or "image/jpeg",
        "author": author or None,
        "created_at": datetime.now().isoformat(),
    }
    get_photos_table().insert(row)
    return row


def list_photos(entity_type: str, entity_id: str) -> list[dict]:
    Q = Query()
    rows = get_photos_table().search(
        (Q.entity_type == entity_type) & (Q.entity_id == entity_id)
    )
    rows.sort(key=lambda r: r.get("created_at", ""))
    return rows


def count_photos(entity_type: str, entity_id: str) -> int:
    return len(list_photos(entity_type, entity_id))


def delete_photo(photo_id: str, entity_type: str = "", entity_id: str = "") -> bool:
    Q = Query()
    table = get_photos_table()
    row = table.get(Q.id == photo_id)
    if not row:
        return False
    if entity_type and row.get("entity_type") != entity_type:
        return False
    if entity_id and row.get("entity_id") != entity_id:
        return False
    filename = os.path.basename(row.get("filename", ""))
    if filename:
        path = os.path.join(PHOTO_DIR, filename)
        if os.path.isfile(path):
            os.remove(path)
    removed = table.remove(Q.id == photo_id)
    return len(removed) > 0


def task_export_rows() -> list[dict]:
    return [
        {
            "id": t.id,
            "name": t.name,
            "room": t.room,
            "assigned_to": ", ".join(t.assigned_to),
            "interval_days": t.interval_days,
            "onetime": t.onetime,
            "points": t.points,
            "effort": t.effort,
            "important": t.important,
            "active": t.active,
            "paused": t.is_paused(),
            "pause_until": t.pause_until or "",
            "start_date": t.start_date or "",
            "snooze_until": t.snooze_until or "",
            "last_done": t.last_done or "",
            "next_due": t.next_due().isoformat() if t.active else "",
        }
        for t in [Task(**row) for row in get_tasks_table().all()]
    ]
