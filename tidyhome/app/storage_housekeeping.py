from datetime import date, datetime, timedelta
import uuid

from tinydb import Query

from storage_runtime import _db


def _list_people_by_role(role: str) -> set[str]:
    return {
        row["person"] for row in _db.table("person_settings").all()
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
    helpers = [person] if person else sorted(_list_people_by_role("housekeeper"))
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
