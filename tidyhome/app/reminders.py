from ha_client import send_notification
from models import Task
from storage import add_comment, get_person_settings, is_vacation_mode_active


async def send_task_reminder(task: Task, target_person: str, message: str,
                             sender: str = "") -> bool:
    clean_message = message.strip()
    cfg = get_person_settings(target_person)
    services = [s for s in (cfg.get("services") or []) if s.strip()]
    title = f"TidyHome: Erinnerung von {sender or 'TidyHome'}"
    body = f"{clean_message}\n\nAufgabe: {task.name}\nRaum: {task.room}"

    sent = False
    if services and not is_vacation_mode_active(target_person):
        for svc in services:
            sent = await send_notification(svc.strip(), title, body) or sent

    if sent:
        note = f"Erinnerung an {target_person} gesendet: {clean_message}"
    else:
        note = (
            f"Erinnerung für {target_person} als Notiz gespeichert "
            f"(kein aktives Gerät oder Versand fehlgeschlagen): {clean_message}"
        )
    add_comment("task", task.id, note, author=sender)
    return sent
