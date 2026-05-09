from tinydb import TinyDB, Query
from models import Comment, Project, Step, Task
from datetime import date, datetime, timedelta
import os
import uuid

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "tidyhome.json")

os.makedirs(DATA_DIR, exist_ok=True)
_db = TinyDB(DB_PATH)
PHOTO_DIR = os.path.join(DATA_DIR, "photos")
os.makedirs(PHOTO_DIR, exist_ok=True)
MAX_PHOTO_BYTES = 8 * 1024 * 1024


def get_tasks_table():
    return _db.table("tasks")


def get_scores_table():
    return _db.table("scores")


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


def _add_score(person: str, points: int, task_type: str = "task",
               label: str = "", source_id: str = ""):
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
        "created_at": datetime.now().isoformat(),
        "label": label,
        "source_id": source_id,
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


def get_recent_score_events(person: str = "", limit: int = 8) -> list[dict]:
    rows = _db.table("score_log").all()
    if person:
        rows = [r for r in rows if r.get("person") == person]
    rows.sort(key=lambda r: r.get("created_at") or r.get("date", ""), reverse=True)
    return rows[:limit]


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
        proj = get_project(step.project_id)
        label = f"{proj.name}: {step.name}" if proj else step.name
        _add_score(step.completed_by, step.points, task_type="project",
                   label=label, source_id=step.id)
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


def get_housekeeper_settings_table():
    return _db.table("housekeeper_settings")


def get_housekeeping_entries_table():
    return _db.table("housekeeping_entries")


def get_housekeeping_billing_table():
    return _db.table("housekeeping_billing")


def _coerce_money(value) -> float:
    try:
        clean = str(value or "0").replace(",", ".").strip()
        return max(float(clean), 0.0)
    except ValueError:
        return 0.0


def _coerce_minutes(value) -> int:
    try:
        return max(int(value or 0), 0)
    except ValueError:
        return 0


def _valid_date(value: str = "") -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        date.fromisoformat(value)
        return value
    except ValueError:
        return ""


def _normalize_wage_row(row: dict) -> dict:
    data = dict(row)
    data.setdefault("id", "")
    data["hourly_wage"] = _coerce_money(data.get("hourly_wage", 0))
    data["valid_from"] = _valid_date(data.get("valid_from", ""))
    data["valid_to"] = _valid_date(data.get("valid_to", ""))
    return data


def list_housekeeper_wages(person: str) -> list[dict]:
    Q = Query()
    table = get_housekeeper_settings_table()
    rows = []
    for row in table.search(Q.person == person):
        data = _normalize_wage_row(row)
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())
            table.update({"id": data["id"]}, doc_ids=[row.doc_id])
        rows.append(data)
    rows.sort(
        key=lambda r: (
            r.get("valid_from") or "0001-01-01",
            r.get("created_at", ""),
        ),
        reverse=True,
    )
    return rows


def get_housekeeper_wage_record(wage_id: str) -> dict | None:
    Q = Query()
    row = get_housekeeper_settings_table().get(Q.id == wage_id)
    return _normalize_wage_row(row) if row else None


def update_housekeeper_wage(wage_id: str, person: str, hourly_wage,
                            valid_from: str = "", valid_to: str = "") -> dict | None:
    row = get_housekeeper_wage_record(wage_id)
    if not row or row.get("person") != person:
        return None
    valid_from = _valid_date(valid_from)
    valid_to = _valid_date(valid_to)
    if valid_to and valid_from and valid_to < valid_from:
        valid_to = ""
    updated = dict(row)
    updated.update({
        "hourly_wage": _coerce_money(hourly_wage),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "updated_at": datetime.now().isoformat(),
    })
    Q = Query()
    get_housekeeper_settings_table().update(updated, Q.id == wage_id)
    return updated


def _housekeeper_wage_record_for_date(person: str, on_date: str = "") -> dict | None:
    target_date = _valid_date(on_date) or date.today().isoformat()
    candidates = []
    for row in list_housekeeper_wages(person):
        valid_from = row.get("valid_from") or "0001-01-01"
        valid_to = row.get("valid_to") or "9999-12-31"
        if valid_from <= target_date <= valid_to:
            candidates.append(row)
    if not candidates:
        return None
    candidates.sort(
        key=lambda r: (
            r.get("valid_from") or "0001-01-01",
            r.get("created_at", ""),
        ),
        reverse=True,
    )
    return candidates[0]


def get_housekeeper_wage(person: str, on_date: str = "") -> float:
    row = _housekeeper_wage_record_for_date(person, on_date)
    if not row:
        return 0.0
    return _coerce_money(row.get("hourly_wage", 0))


def save_housekeeper_wage(person: str, hourly_wage,
                          valid_from: str = "", valid_to: str = "") -> dict:
    valid_from = _valid_date(valid_from) or date.today().isoformat()
    valid_to = _valid_date(valid_to)
    if valid_to and valid_to < valid_from:
        valid_to = ""
    now = datetime.now().isoformat()
    data = {
        "id": str(uuid.uuid4()),
        "person": person,
        "hourly_wage": _coerce_money(hourly_wage),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "created_at": now,
    }
    get_housekeeper_settings_table().insert(data)
    return data


def _entry_cost(entry: dict) -> float:
    wage = get_housekeeper_wage(entry.get("person", ""), entry.get("date", ""))
    return round(_entry_hours(entry) * wage, 2)


def housekeeping_entry_wage(entry: dict) -> float:
    return get_housekeeper_wage(entry.get("person", ""), entry.get("date", ""))


def housekeeping_entry_cost(entry: dict) -> float:
    return _entry_cost(entry)


def housekeeping_entry_has_wage(entry: dict) -> bool:
    return _housekeeper_wage_record_for_date(
        entry.get("person", ""), entry.get("date", "")
    ) is not None


def _billing_key(person: str, month: str) -> str:
    return f"{person}|{month}"


def get_housekeeping_billing(person: str, month: str) -> dict:
    month = month or date.today().strftime("%Y-%m")
    Q = Query()
    row = get_housekeeping_billing_table().get(Q.key == _billing_key(person, month))
    if row:
        return dict(row)
    return {
        "key": _billing_key(person, month),
        "person": person,
        "month": month,
        "status": "open",
        "updated_at": "",
        "updated_by": "",
    }


def set_housekeeping_billing_status(person: str, month: str, status: str,
                                    updated_by: str = "") -> dict:
    month = month or date.today().strftime("%Y-%m")
    if status not in {"open", "reviewed", "paid"}:
        status = "open"
    row = {
        "key": _billing_key(person, month),
        "person": person,
        "month": month,
        "status": status,
        "updated_at": datetime.now().isoformat(),
        "updated_by": updated_by or "",
    }
    Q = Query()
    table = get_housekeeping_billing_table()
    if table.get(Q.key == row["key"]):
        table.update(row, Q.key == row["key"])
    else:
        table.insert(row)
    return row


def is_housekeeping_month_paid(person: str, month: str) -> bool:
    return get_housekeeping_billing(person, month).get("status") == "paid"


def _entry_hours(entry: dict) -> float:
    try:
        start_dt = datetime.fromisoformat(f"{entry['date']}T{entry['start_time']}")
        end_dt = datetime.fromisoformat(f"{entry['date']}T{entry['end_time']}")
    except (KeyError, ValueError):
        return 0.0
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    minutes = int((end_dt - start_dt).total_seconds() // 60)
    minutes -= _coerce_minutes(entry.get("break_minutes", 0))
    return round(max(minutes, 0) / 60, 2)


def add_housekeeping_entry(person: str, work_date: str, start_time: str,
                           end_time: str, break_minutes=0, note: str = "",
                           created_by: str = "") -> dict | None:
    if not person or not work_date or not start_time or not end_time:
        return None
    row = {
        "id": str(uuid.uuid4()),
        "person": person,
        "date": work_date,
        "start_time": start_time,
        "end_time": end_time,
        "break_minutes": _coerce_minutes(break_minutes),
        "note": (note or "").strip(),
        "created_by": created_by or None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    get_housekeeping_entries_table().insert(row)
    return row


def get_housekeeping_entry(entry_id: str) -> dict | None:
    Q = Query()
    return get_housekeeping_entries_table().get(Q.id == entry_id)


def update_housekeeping_entry(entry_id: str, person: str, work_date: str,
                              start_time: str, end_time: str, break_minutes=0,
                              note: str = "") -> dict | None:
    row = get_housekeeping_entry(entry_id)
    if not row or not person or not work_date or not start_time or not end_time:
        return None
    updated = dict(row)
    updated.update({
        "person": person,
        "date": work_date,
        "start_time": start_time,
        "end_time": end_time,
        "break_minutes": _coerce_minutes(break_minutes),
        "note": (note or "").strip(),
        "updated_at": datetime.now().isoformat(),
    })
    Q = Query()
    get_housekeeping_entries_table().update(updated, Q.id == entry_id)
    return updated


def delete_housekeeping_entry(entry_id: str) -> bool:
    Q = Query()
    removed = get_housekeeping_entries_table().remove(Q.id == entry_id)
    return len(removed) > 0


def list_housekeeping_entries(person: str = "", month: str = "") -> list[dict]:
    rows = get_housekeeping_entries_table().all()
    if person:
        rows = [r for r in rows if r.get("person") == person]
    if month:
        rows = [r for r in rows if str(r.get("date", "")).startswith(month)]
    rows.sort(key=lambda r: (r.get("date", ""), r.get("start_time", "")), reverse=True)
    return rows


def housekeeping_entry_hours(entry: dict) -> float:
    return _entry_hours(entry)


def get_housekeeping_month_summary(person: str = "", month: str = "") -> dict:
    month = month or date.today().strftime("%Y-%m")
    helpers = [person] if person else sorted(list_people_by_role("housekeeper"))
    people = []
    total_hours = 0.0
    total_cost = 0.0
    for helper in helpers:
        entries = list_housekeeping_entries(helper, month)
        hours = round(sum(_entry_hours(e) for e in entries), 2)
        wage = get_housekeeper_wage(helper)
        cost = round(sum(_entry_cost(e) for e in entries), 2)
        missing_wage_entries = [
            e for e in entries
            if not housekeeping_entry_has_wage(e)
        ]
        billing = get_housekeeping_billing(helper, month)
        total_hours += hours
        total_cost += cost
        people.append({
            "person": helper,
            "hours": hours,
            "hourly_wage": wage,
            "cost": cost,
            "entries": len(entries),
            "missing_wage_entries": len(missing_wage_entries),
            "missing_wage_dates": sorted({
                e.get("date", "") for e in missing_wage_entries if e.get("date")
            }),
            "has_wage_history": bool(list_housekeeper_wages(helper)),
            "status": billing.get("status", "open"),
            "billing": billing,
        })
    return {
        "month": month,
        "people": people,
        "total_hours": round(total_hours, 2),
        "total_cost": round(total_cost, 2),
        "missing_wage_entries": sum(p["missing_wage_entries"] for p in people),
    }


def export_backup_data() -> dict:
    return {
        "exported_at": datetime.now().isoformat(),
        "format": "tidyhome-tinydb",
        "tables": {
            table_name: _db.table(table_name).all()
            for table_name in sorted(_db.tables())
        },
    }


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


def project_export_rows() -> list[dict]:
    rows = []
    for project in [Project(**row) for row in get_projects_table().all()]:
        steps = list_steps(project.id)
        done, total = project.progress(steps)
        rows.append({
            "id": project.id,
            "name": project.name,
            "room": project.room,
            "assigned_to": project.assigned_to or "",
            "active": project.active,
            "completed": project.completed,
            "steps": total,
            "steps_done": done,
            "created_at": project.created_at,
        })
    return rows


def score_export_rows() -> list[dict]:
    rows = _db.table("score_log").all()
    rows.sort(key=lambda r: (r.get("date", ""), r.get("created_at", "")))
    return rows


def diagnose_data(known_people: list[str], known_rooms: list[str]) -> dict:
    people = set(known_people or [])
    rooms = set(known_rooms or [])
    issues: list[dict] = []
    task_ids = {row.get("id") for row in get_tasks_table().all()}
    project_ids = {row.get("id") for row in get_projects_table().all()}
    step_ids = {row.get("id") for row in get_steps_table().all()}

    for row in get_tasks_table().all():
        name = row.get("name", row.get("id", "Aufgabe"))
        if rooms and row.get("room") not in rooms:
            issues.append({"type": "task_room", "severity": "warn",
                           "label": name, "detail": row.get("room", "")})
        for person in row.get("assigned_to", []) or []:
            if people and person not in people:
                issues.append({"type": "task_person", "severity": "warn",
                               "label": name, "detail": person})

    for row in get_projects_table().all():
        name = row.get("name", row.get("id", "Projekt"))
        if rooms and row.get("room") not in rooms:
            issues.append({"type": "project_room", "severity": "warn",
                           "label": name, "detail": row.get("room", "")})
        person = row.get("assigned_to")
        if person and people and person not in people:
            issues.append({"type": "project_person", "severity": "warn",
                           "label": name, "detail": person})

    for row in get_steps_table().all():
        name = row.get("name", row.get("id", "Schritt"))
        if row.get("project_id") not in project_ids:
            issues.append({"type": "orphan_step", "severity": "error",
                           "label": name, "detail": row.get("project_id", "")})
        person = row.get("assigned_to")
        if person and people and person not in people:
            issues.append({"type": "step_person", "severity": "warn",
                           "label": name, "detail": person})

    for row in get_photos_table().all():
        entity_type = row.get("entity_type")
        entity_id = row.get("entity_id")
        filename = os.path.basename(row.get("filename", ""))
        if filename and not os.path.isfile(os.path.join(PHOTO_DIR, filename)):
            issues.append({"type": "missing_photo_file", "severity": "error",
                           "label": filename, "detail": entity_id})
        valid_entity = (
            entity_type == "task" and entity_id in task_ids
            or entity_type == "project" and entity_id in project_ids
            or entity_type == "step" and entity_id in step_ids
        )
        if not valid_entity:
            issues.append({"type": "orphan_photo", "severity": "warn",
                           "label": filename or row.get("id", "Foto"),
                           "detail": f"{entity_type}:{entity_id}"})

    return {
        "checked_at": datetime.now().isoformat(),
        "issues": issues,
        "counts": {
            "tasks": len(task_ids),
            "projects": len(project_ids),
            "steps": len(step_ids),
            "photos": len(get_photos_table().all()),
            "issues": len(issues),
        },
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


def get_person_achievements(person: str) -> list[dict]:
    stats = get_person_stats(person)
    definitions = [
        ("first_task", "Erster Schritt", "Erste Aufgabe erledigt", stats["tasks_done"] >= 1),
        ("tasks_10", "10 Aufgaben", "10 Haushaltsaufgaben erledigt", stats["tasks_done"] >= 10),
        ("tasks_50", "50 Aufgaben", "50 Haushaltsaufgaben erledigt", stats["tasks_done"] >= 50),
        ("points_100", "100 Punkte", "100 Gesamtpunkte erreicht", stats["total_points"] >= 100),
        ("points_500", "500 Punkte", "500 Gesamtpunkte erreicht", stats["total_points"] >= 500),
        ("streak_3", "3-Tage-Serie", "An 3 Tagen in Folge aktiv", stats["streak"] >= 3),
        ("streak_7", "7-Tage-Serie", "An 7 Tagen in Folge aktiv", stats["streak"] >= 7),
        ("project_step", "Projektstart", "Ersten Projektschritt erledigt", stats["proj_steps"] >= 1),
        ("project_steps_5", "Projektmotor", "5 Projektschritte erledigt", stats["proj_steps"] >= 5),
    ]
    return [
        {"id": key, "title": title, "description": description, "unlocked": unlocked}
        for key, title, description, unlocked in definitions
    ]


def get_person_score_history(person: str, weeks: int = 8, months: int = 6) -> dict:
    today = date.today()
    rows = [
        r for r in _db.table("score_log").all()
        if r.get("person") == person and r.get("date")
    ]

    week_items = []
    current_week_start = today - timedelta(days=today.weekday())
    for offset in range(weeks):
        start = current_week_start - timedelta(days=offset * 7)
        end = start + timedelta(days=7)
        entries = [
            r for r in rows
            if start.isoformat() <= r.get("date", "") < end.isoformat()
        ]
        week_items.append({
            "label": f"KW {start.isocalendar().week}",
            "from": start.isoformat(),
            "to": (end - timedelta(days=1)).isoformat(),
            "points": sum(int(r.get("points", 0) or 0) for r in entries),
            "tasks": sum(1 for r in entries if r.get("type") != "project"),
            "projects": sum(1 for r in entries if r.get("type") == "project"),
        })
    week_items.reverse()

    month_items = []
    year = today.year
    month = today.month
    for offset in range(months):
        m = month - offset
        y = year
        while m <= 0:
            m += 12
            y -= 1
        start = date(y, m, 1)
        next_month = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        entries = [
            r for r in rows
            if start.isoformat() <= r.get("date", "") < next_month.isoformat()
        ]
        month_items.append({
            "label": start.strftime("%m.%Y"),
            "from": start.isoformat(),
            "to": (next_month - timedelta(days=1)).isoformat(),
            "points": sum(int(r.get("points", 0) or 0) for r in entries),
            "tasks": sum(1 for r in entries if r.get("type") != "project"),
            "projects": sum(1 for r in entries if r.get("type") == "project"),
        })
    month_items.reverse()

    return {"weeks": week_items, "months": month_items}


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
