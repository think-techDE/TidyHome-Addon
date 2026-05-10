from datetime import datetime
import os

import storage_tasks as _storage_tasks
from models import Comment, Project, Step, Task
from storage_runtime import DATA_DIR, DB_PATH, MAX_PHOTO_BYTES, PHOTO_DIR, _db
from storage_app import (_get_app_table, _get_app_value, _save_app_value,
                         get_admins, get_room_icons, get_vacation_mode,
                         is_vacation_mode_active, save_admins, save_room_icons,
                         save_vacation_mode)
from storage_tasks import (_photo_extension, add_comment, count_photos,
                           create_task, create_task_from_template, delete_task,
                           delete_task_template, edit_task,
                           get_comments_table, get_photos_table, get_task,
                           get_task_template, get_task_templates_table,
                           get_tasks_table, list_comments, list_photos,
                           list_task_history, list_task_templates, list_tasks,
                           mark_done, pause_task, reactivate_task,
                           save_task_template, snooze_task, task_export_rows,
                           update_task, update_task_template)
from storage_projects import (add_step, assign_step, complete_step, create_project,
                              delete_project, delete_step, get_project,
                              get_projects_table, get_step, get_steps_table,
                              list_projects, list_steps, project_export_rows,
                              update_project)
from storage_people import (ROLES, _add_score, filter_tasks_by_role,
                            get_person_achievements, get_person_score_history,
                            get_person_settings, get_person_stats,
                            get_recent_score_events, get_scores,
                            get_scores_table, get_settings_table,
                            list_people_by_role, list_person_settings,
                            save_person_settings, score_export_rows)

from storage_housekeeping import (
    _coerce_minutes, _coerce_money, _entry_cost, _entry_hours,
    _housekeeper_wage_record_for_date, _valid_date, add_housekeeping_entry,
    delete_housekeeping_entry, get_housekeeper_settings_table,
    get_housekeeper_wage, get_housekeeper_wage_record,
    get_housekeeping_billing, get_housekeeping_billing_table,
    get_housekeeping_entries_table, get_housekeeping_entry,
    get_housekeeping_month_summary, housekeeping_entry_cost,
    housekeeping_entry_has_wage, housekeeping_entry_hours,
    housekeeping_entry_wage, is_housekeeping_month_paid,
    list_housekeeper_wages, list_housekeeping_entries, save_housekeeper_wage,
    set_housekeeping_billing_status, update_housekeeper_wage,
    update_housekeeping_entry,
)


def _sync_storage_task_runtime() -> None:
    _storage_tasks.PHOTO_DIR = PHOTO_DIR
    _storage_tasks.MAX_PHOTO_BYTES = MAX_PHOTO_BYTES


def add_photo(entity_type: str, entity_id: str, photo_type: str,
              filename: str, content_type: str, data: bytes,
              author: str = "") -> dict | None:
    _sync_storage_task_runtime()
    return _storage_tasks.add_photo(
        entity_type, entity_id, photo_type, filename, content_type, data, author
    )


def delete_photo(photo_id: str, entity_type: str = "", entity_id: str = "") -> bool:
    _sync_storage_task_runtime()
    return _storage_tasks.delete_photo(photo_id, entity_type, entity_id)


def export_backup_data() -> dict:
    return {
        "exported_at": datetime.now().isoformat(),
        "format": "tidyhome-tinydb",
        "tables": {
            table_name: _db.table(table_name).all()
            for table_name in sorted(_db.tables())
        },
    }


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
