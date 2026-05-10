from datetime import date

from tinydb import Query

from models import Project, Step
from storage_runtime import _db
from storage_people import _add_score


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
