from datetime import date

from tinydb import Query

from storage_runtime import _db


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


def _person_vacation_settings(person: str) -> dict:
    if not person:
        return {}
    Q = Query()
    row = _db.table("person_settings").get(Q.person == person) or {}
    return {
        "enabled": bool(row.get("vacation_enabled")),
        "until": row.get("vacation_until") or "",
    }


def get_vacation_mode(person: str = "") -> dict:
    if person:
        return _person_vacation_settings(person)
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
