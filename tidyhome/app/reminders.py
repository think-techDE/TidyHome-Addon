from ha_client import send_notification
from models import Project, Step, Task
from storage import add_comment, get_person_settings, is_vacation_mode_active


def task_reminder_recipients(task: Task, sender: str = "") -> list[str]:
    sender = (sender or "").strip()
    recipients: list[str] = []
    for person in task.assigned_to:
        person = person.strip()
        if person and person != sender and person not in recipients:
            recipients.append(person)
    return recipients


def _notify_services(person: str) -> list[str]:
    cfg = get_person_settings(person)
    return [s.strip() for s in (cfg.get("services") or []) if s.strip()]


async def _send_to_person(person: str, title: str, body: str) -> bool:
    if is_vacation_mode_active(person):
        return False

    sent = False
    for svc in _notify_services(person):
        sent = await send_notification(svc, title, body) or sent
    return sent


async def send_task_reminder(task: Task, target_person: str, message: str,
                             sender: str = "") -> bool:
    clean_message = message.strip()
    actor = sender or "TidyHome"
    title = f"TidyHome: Erinnerung von {actor}"
    body = f"{clean_message}\n\nAufgabe: {task.name}\nRaum: {task.room}"
    sent = await _send_to_person(target_person, title, body)

    if sent:
        note = f"{actor} hat {target_person} erinnert: {clean_message}"
    else:
        note = (
            f"{actor} wollte {target_person} erinnern "
            f"(kein aktives Gerät oder Versand fehlgeschlagen): {clean_message}"
        )
    add_comment("task", task.id, note, author=sender)
    return sent


async def send_task_reminders(task: Task, recipients: list[str], message: str,
                              sender: str = "") -> bool:
    sent_any = False
    for person in recipients:
        sent_any = await send_task_reminder(task, person, message, sender=sender) or sent_any
    return sent_any


async def send_project_step_reminder(project: Project, step: Step,
                                     target_person: str, message: str,
                                     sender: str = "") -> bool:
    clean_message = message.strip()
    actor = sender or "TidyHome"
    title = f"TidyHome: Erinnerung von {actor}"
    body = (
        f"{clean_message}\n\n"
        f"Projekt: {project.name}\n"
        f"Schritt: {step.name}\n"
        f"Raum: {project.room}"
    )
    sent = await _send_to_person(target_person, title, body)

    if sent:
        note = f"{actor} hat {target_person} an Schritt \"{step.name}\" erinnert: {clean_message}"
    else:
        note = (
            f"{actor} wollte {target_person} an Schritt \"{step.name}\" erinnern "
            f"(kein aktives Gerät oder Versand fehlgeschlagen): {clean_message}"
        )
    add_comment("project", project.id, note, author=sender)
    return sent
