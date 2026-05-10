from datetime import date, datetime, timedelta

from tinydb import Query

from i18n import normalize_language
from storage_runtime import _db


def get_scores_table():
    return _db.table("scores")


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
    defaults = {"person": person, "services": [], "notify_time": "08:00",
                "enabled": False, "hidden_rooms": [], "weekly_goal": 0,
                "role": "member", "can_see_children": False,
                "vacation_enabled": False, "vacation_until": "",
                "language": "auto"}
    if not row:
        return defaults
    merged = {**defaults, **row}
    merged["language"] = normalize_language(merged.get("language") or "auto")
    return merged


def save_person_settings(person: str, services: list[str], notify_time: str,
                         enabled: bool, hidden_rooms: list[str] | None = None,
                         weekly_goal: int = 0, role: str = "member",
                         can_see_children: bool = False,
                         vacation_enabled: bool = False,
                         vacation_until: str = "",
                         language: str = "auto") -> dict:
    Q = Query()
    data = {"person": person, "services": services,
            "notify_time": notify_time, "enabled": enabled,
            "hidden_rooms": hidden_rooms or [], "weekly_goal": weekly_goal,
            "role": role, "can_see_children": can_see_children,
            "vacation_enabled": vacation_enabled,
            "vacation_until": vacation_until or "",
            "language": normalize_language(language or "auto")}
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


def score_export_rows() -> list[dict]:
    rows = _db.table("score_log").all()
    rows.sort(key=lambda r: (r.get("date", ""), r.get("created_at", "")))
    return rows


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
