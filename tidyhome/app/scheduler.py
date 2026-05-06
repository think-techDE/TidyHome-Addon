import asyncio
import logging
from datetime import datetime

from storage import list_tasks, list_person_settings, get_person_settings
from ha_client import send_notification

logger = logging.getLogger("tidyhome")


def parse_time(raw: str) -> str:
    try:
        hh, mm = raw.strip().split(":", 1)
        return f"{int(hh):02d}:{int(mm):02d}"
    except Exception:
        return "08:00"


async def _do_notify(person: str, services: list[str]) -> None:
    tasks = [t for t in list_tasks(assigned_to=person) if t.days_until_due() <= 0]
    if not tasks:
        logger.info("Keine faelligen Aufgaben fuer %s", person)
        return
    lines = [
        f"* {t.name} ({'heute' if t.days_until_due() == 0 else f'{abs(t.days_until_due())}d ueberfaellig'})"
        for t in tasks
    ]
    title = f"TidyHome: {len(tasks)} Aufgabe(n) faellig"
    message = "\n".join(lines)
    for svc in services:
        ok = await send_notification(svc.strip(), title, message)
        logger.info("Notify %s -> %s: %s", person, svc, "ok" if ok else "fehler")


async def notify_person_now(person: str) -> None:
    cfg = get_person_settings(person)
    if not cfg.get("enabled") or not cfg.get("services"):
        return
    await _do_notify(person, cfg["services"])


async def scheduler_loop() -> None:
    logger.info("Scheduler gestartet")
    notified_today: set[str] = set()
    last_date = datetime.now().date()
    while True:
        try:
            await asyncio.sleep(60)
            now = datetime.now()
            if now.date() != last_date:
                notified_today.clear()
                last_date = now.date()
            hhmm = now.strftime("%H:%M")
            for cfg in list_person_settings():
                if not cfg.get("enabled") or not cfg.get("services"):
                    continue
                person = cfg["person"]
                key = f"{person}:{now.date().isoformat()}"
                if hhmm == parse_time(cfg.get("notify_time", "08:00")) and key not in notified_today:
                    notified_today.add(key)
                    await _do_notify(person, cfg["services"])
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("Scheduler Fehler: %s", e)
