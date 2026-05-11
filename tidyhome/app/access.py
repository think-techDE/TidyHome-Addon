from collections.abc import Callable

from models import Project, Step, Task
from storage_app import get_admins
from storage_people import get_person_settings, list_people_by_role


UNASSIGNED_LABEL = "--- Nicht zugeordnet ---"


def admin_set(admins: set[str] | list[str] | None = None) -> set[str]:
    return set(get_admins() if admins is None else admins)


def role_for(person: str) -> str:
    if not person:
        return ""
    return get_person_settings(person).get("role", "member")


def is_admin(person: str, admins: set[str] | list[str] | None = None) -> bool:
    return bool(person and person in admin_set(admins))


def is_parent(person: str) -> bool:
    return role_for(person) == "parent"


def is_housekeeper(person: str) -> bool:
    return role_for(person) == "housekeeper"


def can_view_children(person: str) -> bool:
    if not person:
        return False
    cfg = get_person_settings(person)
    return cfg.get("role") == "parent" or bool(cfg.get("can_see_children"))


def child_people() -> set[str]:
    return set(list_people_by_role("child"))


def hidden_rooms_for_person(person: str) -> set[str]:
    if not person:
        return set()
    return set(get_person_settings(person).get("hidden_rooms", []) or [])


def filter_hidden_rooms(items: list, person: str) -> list:
    hidden = hidden_rooms_for_person(person)
    if not hidden:
        return list(items)
    return [item for item in items if getattr(item, "room", "") not in hidden]


def managed_task_people(person: str, admins: set[str] | list[str] | None = None) -> set[str]:
    if not person:
        return set()
    if is_admin(person, admins):
        return set()
    people = {person}
    if can_view_children(person):
        people.update(child_people())
    return people


def can_group_tasks_by_person(person: str, admins: set[str] | list[str] | None = None) -> bool:
    return bool(person and (is_admin(person, admins) or can_view_children(person)))


def task_assignees(task: Task) -> set[str]:
    return set(task.assigned_to or [])


def visible_tasks_for_person(tasks: list[Task], person: str,
                             admins: set[str] | list[str] | None = None,
                             include_managed: bool = False) -> list[Task]:
    if not person:
        return list(tasks)
    if include_managed:
        if is_admin(person, admins):
            return list(tasks)
        managed = managed_task_people(person, admins)
        return [task for task in tasks if task_assignees(task) & managed]
    return [task for task in tasks if person in task_assignees(task)]


def task_group_people(task: Task, viewer: str,
                      admins: set[str] | list[str] | None = None) -> list[str]:
    assignees = sorted(task_assignees(task))
    if is_admin(viewer, admins):
        return assignees or [UNASSIGNED_LABEL]
    managed = managed_task_people(viewer, admins)
    visible = [person for person in assignees if person in managed]
    return visible or [UNASSIGNED_LABEL]


def project_step_assignee(step: Step, project: Project) -> str:
    return step.assigned_to or project.assigned_to or ""


def project_assignees(project: Project, steps: list[Step]) -> set[str]:
    people = {project.assigned_to} if project.assigned_to else set()
    people.update(project_step_assignee(step, project) for step in steps)
    return {person for person in people if person}


def managed_project_people(person: str,
                           admins: set[str] | list[str] | None = None) -> set[str]:
    return managed_task_people(person, admins)


def can_group_projects_by_person(person: str,
                                 admins: set[str] | list[str] | None = None) -> bool:
    return is_admin(person, admins)


def can_view_project(project: Project, steps: list[Step], person: str,
                     admins: set[str] | list[str] | None = None,
                     include_managed: bool = False) -> bool:
    if not person:
        return True
    if include_managed and is_admin(person, admins):
        return True
    allowed = managed_project_people(person, admins) if include_managed else {person}
    return bool(project_assignees(project, steps) & allowed)


def visible_project_steps(project: Project, steps: list[Step], person: str,
                          admins: set[str] | list[str] | None = None,
                          include_managed: bool = False) -> list[Step]:
    if not person:
        return list(steps)
    if include_managed and is_admin(person, admins):
        return list(steps)
    allowed = managed_project_people(person, admins) if include_managed else {person}
    return [
        step for step in steps
        if project_step_assignee(step, project) in allowed
    ]


def project_steps_for_person(project: Project, steps: list[Step],
                             person: str) -> list[Step]:
    return [
        step for step in steps
        if project_step_assignee(step, project) == person
    ]


def project_people(project: Project, steps: list[Step]) -> list[str]:
    return sorted(project_assignees(project, steps)) or [UNASSIGNED_LABEL]


def visible_projects_for_person(projects: list[Project], person: str,
                                steps_for_project: Callable[[str], list[Step]],
                                admins: set[str] | list[str] | None = None,
                                include_managed: bool = False) -> list[Project]:
    return [
        project for project in projects
        if can_view_project(
            project, steps_for_project(project.id), person, admins,
            include_managed=include_managed,
        )
    ]


def can_manage_housekeeping(person: str,
                            admins: set[str] | list[str] | None = None) -> bool:
    return bool(person and (is_admin(person, admins) or is_parent(person)))


def can_open_housekeeping_log(person: str,
                              admins: set[str] | list[str] | None = None) -> bool:
    return bool(person and (is_housekeeper(person) or can_manage_housekeeping(person, admins)))


def is_known_housekeeper(person: str) -> bool:
    return bool(person and person in set(list_people_by_role("housekeeper")))


def can_create_housekeeping_entry(actor: str, target: str,
                                  admins: set[str] | list[str] | None = None) -> bool:
    return can_manage_housekeeping(actor, admins) or (actor == target and is_housekeeper(actor))


def can_update_housekeeping_entry(actor: str, entry_person: str, target: str,
                                  admins: set[str] | list[str] | None = None) -> bool:
    return can_manage_housekeeping(actor, admins) or (
        actor == entry_person and target == actor
    )


def can_delete_housekeeping_entry(actor: str, entry_person: str,
                                  admins: set[str] | list[str] | None = None) -> bool:
    return can_manage_housekeeping(actor, admins) or actor == entry_person
