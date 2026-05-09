from datetime import date
from html import escape

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from render import _base, _icon, format_date_de, person_suffix, render, resolve_person
from storage import (add_housekeeping_entry, delete_housekeeping_entry, get_admins,
                     get_housekeeper_wage, get_housekeeping_entry,
                     get_housekeeping_month_summary, get_person_settings,
                     housekeeping_entry_hours, list_housekeeping_entries,
                     list_housekeeper_wages, list_people_by_role, save_housekeeper_wage,
                     update_housekeeping_entry)

router = APIRouter(prefix="/housekeeping")


def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def _month_value(month: str = "") -> str:
    return month[:7] if month and len(month) >= 7 else _current_month()


def _money(value: float) -> str:
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _hours(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def _can_manage(person: str) -> bool:
    if not person:
        return False
    return person in set(get_admins()) or get_person_settings(person).get("role") == "parent"


def _is_housekeeper(person: str) -> bool:
    return get_person_settings(person).get("role") == "housekeeper"


def _is_known_housekeeper(person: str) -> bool:
    return person in set(list_people_by_role("housekeeper"))


def _month_nav(base: str, month: str, person: str) -> str:
    psuffix = person_suffix(person, "&") if person else ""
    return f"""
    <form class="month-filter" method="get" action="{base}housekeeping">
      <input type="hidden" name="p" value="{escape(person, quote=True)}">
      <label>Monat</label>
      <input type="month" name="month" value="{escape(month, quote=True)}">
      <button class="btn btn-ghost btn-sm" type="submit">Anzeigen</button>
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping?month={_current_month()}{psuffix}">Aktueller Monat</a>
    </form>"""


def _entry_form(base: str, helpers: list[str], actor: str, month: str,
                entry: dict | None = None, compact: bool = False,
                force_person: str = "") -> str:
    entry = entry or {}
    target = force_person or entry.get("person") or (helpers[0] if helpers else actor)
    action = (
        f"{base}housekeeping/entries/{entry['id']}"
        if entry.get("id") else
        f"{base}housekeeping/entries"
    )
    button = "Korrigieren" if entry.get("id") else "Arbeitszeit speichern"
    person_field = f'<input type="hidden" name="person" value="{escape(target, quote=True)}">'
    if not force_person and helpers:
        opts = "".join(
            f'<option value="{escape(pn, quote=True)}"{" selected" if pn == target else ""}>{escape(pn)}</option>'
            for pn in helpers
        )
        person_field = f"""
        <div class="form-group">
          <label>Haushaltshilfe</label>
          <select name="person">{opts}</select>
        </div>"""
    note_val = escape(entry.get("note", ""), quote=True)
    date_val = escape(entry.get("date", date.today().isoformat()), quote=True)
    start_val = escape(entry.get("start_time", ""), quote=True)
    end_val = escape(entry.get("end_time", ""), quote=True)
    break_val = int(entry.get("break_minutes", 0) or 0)
    wrapper_cls = "work-entry-form compact" if compact else "work-entry-form"
    delete_button = ""
    if entry.get("id"):
        delete_button = (
            f'<button class="btn btn-ghost btn-sm danger-text" type="submit" '
            f'formaction="{base}housekeeping/entries/{entry["id"]}/delete" '
            f'onclick="return confirm(\'Eintrag löschen?\')">Löschen</button>'
        )
    return f"""
    <form class="{wrapper_cls}" method="post" action="{action}">
      <input type="hidden" name="return_p" value="{escape(actor, quote=True)}">
      <input type="hidden" name="month" value="{escape(month, quote=True)}">
      {person_field}
      <div class="grid-2">
        <div class="form-group">
          <label>Datum</label>
          <input type="date" name="work_date" value="{date_val}" required>
        </div>
        <div class="form-group">
          <label>Pause (Min.)</label>
          <input type="number" name="break_minutes" min="0" max="600" value="{break_val}">
        </div>
        <div class="form-group">
          <label>Start</label>
          <input type="time" name="start_time" value="{start_val}" required>
        </div>
        <div class="form-group">
          <label>Ende</label>
          <input type="time" name="end_time" value="{end_val}" required>
        </div>
      </div>
      <div class="form-group">
        <label>Notiz (optional)</label>
        <input name="note" value="{note_val}" placeholder="z.B. Fenster, Bad, Küche">
      </div>
      <div class="settings-actions">
        <button class="btn btn-primary btn-sm" type="submit">{button}</button>
        {delete_button}
      </div>
    </form>"""


def _entries_for_person(base: str, person: str, actor: str, month: str) -> str:
    entries = list_housekeeping_entries(person, month)
    if not entries:
        return '<div class="empty" style="padding:1rem">Noch keine Arbeitszeiten in diesem Monat.</div>'
    rows = ""
    for entry in entries:
        hours = housekeeping_entry_hours(entry)
        wage = get_housekeeper_wage(entry.get("person", ""), entry.get("date", ""))
        cost = hours * wage
        note = escape(entry.get("note", ""))
        note_part = f'<span>· {note}</span>' if note else ""
        rows += f"""
        <details class="work-entry-details">
          <summary class="work-entry-summary">
            <span>
              <strong>{format_date_de(entry.get("date", ""))}</strong>
              <small>{escape(entry.get("start_time", ""))} - {escape(entry.get("end_time", ""))}{note_part}</small>
            </span>
            <span class="work-entry-total">{_hours(hours)} h · {_money(cost)} · {_money(wage)}/h</span>
          </summary>
          {_entry_form(base, [person], actor, month, entry=entry, compact=True)}
        </details>"""
    return rows


def _wage_history(person: str) -> str:
    rows = list_housekeeper_wages(person)
    if not rows:
        return '<div class="muted wage-history-empty">Noch kein Stundensatz hinterlegt.</div>'
    items = ""
    for row in rows:
        valid_from = row.get("valid_from") or ""
        valid_to = row.get("valid_to") or ""
        if valid_from and valid_to:
            period = f"{format_date_de(valid_from)} bis {format_date_de(valid_to)}"
        elif valid_from:
            period = f"ab {format_date_de(valid_from)}"
        elif valid_to:
            period = f"bis {format_date_de(valid_to)}"
        else:
            period = "ohne Zeitraum"
        items += (
            '<div class="wage-history-row">'
            f'<strong>{_money(row.get("hourly_wage", 0))}/h</strong>'
            f'<span>{escape(period)}</span>'
            '</div>'
        )
    return f'<div class="wage-history">{items}</div>'


@router.get("", response_class=HTMLResponse)
async def housekeeping_dashboard(request: Request, month: str = "", p: str = ""):
    actor = resolve_person(request, p)
    base = _base(request)
    if not _can_manage(actor):
        if _is_housekeeper(actor):
            return RedirectResponse(base + f"housekeeping/log{person_suffix(actor)}", status_code=303)
        raise HTTPException(403)

    month = _month_value(month)
    helpers = sorted(list_people_by_role("housekeeper"))
    summary = get_housekeeping_month_summary(month=month)

    helper_cards = ""
    for item in summary["people"]:
        person = item["person"]
        helper_cards += f"""
        <section class="card housekeeping-person-card">
          <div class="admin-section-head">
            <div>
              <h3>{escape(person)}</h3>
              <p class="muted">{item['entries']} Einträge · {_hours(item['hours'])} h · {_money(item['cost'])}</p>
            </div>
            <span class="badge ok">aktuell {_money(item['hourly_wage'])}/h</span>
          </div>
          <details class="housekeeping-subdetails">
            <summary class="housekeeping-subsummary">
              <span>
                <strong>Stundensatz und Historie</strong>
                <small>Gültigkeit und vergangene Sätze</small>
              </span>
              <span class="details-caret">▾</span>
            </summary>
            <div class="housekeeping-subbody">
              <form class="wage-form" method="post" action="{base}housekeeping/wage">
                <input type="hidden" name="return_p" value="{escape(actor, quote=True)}">
                <input type="hidden" name="month" value="{escape(month, quote=True)}">
                <input type="hidden" name="person" value="{escape(person, quote=True)}">
                <div class="form-group">
                  <label>Stundenlohn</label>
                  <input name="hourly_wage" inputmode="decimal" value="{item['hourly_wage']:.2f}">
                </div>
                <div class="form-group">
                  <label>Gültig ab</label>
                  <input type="date" name="valid_from" value="{date.today().isoformat()}" required>
                </div>
                <div class="form-group">
                  <label>Gültig bis</label>
                  <input type="date" name="valid_to">
                </div>
                <button class="btn btn-ghost btn-sm" type="submit">Stundensatz hinzufügen</button>
              </form>
              {_wage_history(person)}
            </div>
          </details>
          <div class="work-entry-list">{_entries_for_person(base, person, actor, month)}</div>
        </section>"""

    entry_card = ""
    if helpers:
        entry_card = f"""
        <details class="card housekeeping-foldout">
          <summary class="housekeeping-foldout-head">
            <span>
              <strong>Arbeitszeit erfassen</strong>
              <small>Neue Arbeitszeit für eine Haushaltshilfe eintragen</small>
            </span>
            <span class="details-caret">▾</span>
          </summary>
          <div class="housekeeping-foldout-body">
            {_entry_form(base, helpers, actor, month)}
          </div>
        </details>"""

    if not helpers:
        helper_cards = """
        <div class="card">
          <h3>Keine Haushaltshilfen angelegt</h3>
          <p class="muted" style="margin-top:0.25rem">
            Lege in den Personeneinstellungen zuerst mindestens eine Person mit Rolle Haushaltshilfe fest.
          </p>
        </div>"""

    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">Haushaltshilfen</div>
        <div class="hero-title">Arbeitszeiten</div>
        <div class="muted">Monatsübersicht, Stundensätze und Korrekturen.</div>
      </div>
      <div class="page-hero-actions">
        <span class="badge ok">{escape(month)}</span>
      </div>
    </div>
    <div class="housekeeping-summary-grid">
      <div class="today-stat"><div class="today-value">{_hours(summary['total_hours'])}</div><div class="today-label">Stunden</div></div>
      <div class="today-stat"><div class="today-value">{_money(summary['total_cost'])}</div><div class="today-label">Gesamtkosten</div></div>
      <div class="today-stat"><div class="today-value">{len(helpers)}</div><div class="today-label">Haushaltshilfen</div></div>
    </div>
    {_month_nav(base, month, actor)}
    {entry_card}
    <div class="admin-stack">{helper_cards}</div>"""
    return render(content, request, page="home", person=actor)


@router.get("/log", response_class=HTMLResponse)
async def housekeeping_log(request: Request, month: str = "", p: str = ""):
    actor = resolve_person(request, p)
    if not actor or not (_is_housekeeper(actor) or _can_manage(actor)):
        raise HTTPException(403)
    month = _month_value(month)
    base = _base(request)
    summary = get_housekeeping_month_summary(actor, month)
    item = summary["people"][0] if summary["people"] else {
        "hours": 0, "cost": 0, "hourly_wage": 0, "entries": 0
    }
    entries = _entries_for_person(base, actor, actor, month)
    psuffix = person_suffix(actor)
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">Arbeitszeit</div>
        <div class="hero-title">{escape(actor)}</div>
        <div class="muted">Erfasster Stand für {escape(month)}</div>
      </div>
      <div class="page-hero-actions">
        <a class="btn btn-ghost btn-sm" href="{base}{psuffix}">Zuhause</a>
      </div>
    </div>
    <div class="housekeeping-summary-grid">
      <div class="today-stat"><div class="today-value">{_hours(item['hours'])}</div><div class="today-label">Stunden</div></div>
      <div class="today-stat"><div class="today-value">{_money(item['cost'])}</div><div class="today-label">Erarbeitet</div></div>
      <div class="today-stat"><div class="today-value">{_money(item['hourly_wage'])}</div><div class="today-label">aktueller Satz</div></div>
    </div>
    <form class="month-filter" method="get" action="{base}housekeeping/log">
      <input type="hidden" name="p" value="{escape(actor, quote=True)}">
      <label>Monat</label>
      <input type="month" name="month" value="{escape(month, quote=True)}">
      <button class="btn btn-ghost btn-sm" type="submit">Anzeigen</button>
    </form>
    <details class="card housekeeping-foldout">
      <summary class="housekeeping-foldout-head">
        <span>
          <strong>Arbeitszeit eintragen</strong>
          <small>Neue Arbeitszeit für diesen Monat erfassen</small>
        </span>
        <span class="details-caret">▾</span>
      </summary>
      <div class="housekeeping-foldout-body">
        {_entry_form(base, [actor], actor, month, force_person=actor)}
      </div>
    </details>
    <div class="card card-flush">
      <div class="score-activity-head">
        <h3>Erfasste Zeiten</h3>
        <div class="muted">Du kannst deine Einträge nachträglich korrigieren.</div>
      </div>
      {entries}
    </div>"""
    return render(content, request, page="home", person=actor)


@router.post("/wage")
async def housekeeping_wage_save(request: Request, person: str = Form(...),
                                 hourly_wage: str = Form("0"),
                                 valid_from: str = Form(""),
                                 valid_to: str = Form(""),
                                 month: str = Form(""), return_p: str = Form("")):
    actor = resolve_person(request, return_p)
    if not _can_manage(actor) or not _is_known_housekeeper(person):
        raise HTTPException(403)
    save_housekeeper_wage(person, hourly_wage, valid_from=valid_from, valid_to=valid_to)
    return RedirectResponse(
        _base(request) + f"housekeeping?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )


@router.post("/entries")
async def housekeeping_entry_create(request: Request, person: str = Form(""),
                                    work_date: str = Form(...),
                                    start_time: str = Form(...),
                                    end_time: str = Form(...),
                                    break_minutes: int = Form(0),
                                    note: str = Form(""), month: str = Form(""),
                                    return_p: str = Form("")):
    actor = resolve_person(request, return_p)
    target = person or actor
    if not (_can_manage(actor) or (actor == target and _is_housekeeper(actor))):
        raise HTTPException(403)
    if _can_manage(actor) and not _is_known_housekeeper(target):
        raise HTTPException(403)
    add_housekeeping_entry(target, work_date, start_time, end_time,
                           break_minutes=break_minutes, note=note, created_by=actor)
    path = "housekeeping" if _can_manage(actor) and person else "housekeeping/log"
    return RedirectResponse(
        _base(request) + f"{path}?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )


@router.post("/entries/{entry_id}")
async def housekeeping_entry_update(entry_id: str, request: Request,
                                    person: str = Form(""),
                                    work_date: str = Form(...),
                                    start_time: str = Form(...),
                                    end_time: str = Form(...),
                                    break_minutes: int = Form(0),
                                    note: str = Form(""), month: str = Form(""),
                                    return_p: str = Form("")):
    actor = resolve_person(request, return_p)
    entry = get_housekeeping_entry(entry_id)
    target = person or (entry or {}).get("person", actor)
    if not entry or not (_can_manage(actor) or (actor == entry.get("person") and target == actor)):
        raise HTTPException(403)
    if _can_manage(actor) and not _is_known_housekeeper(target):
        raise HTTPException(403)
    update_housekeeping_entry(entry_id, target, work_date, start_time, end_time,
                              break_minutes=break_minutes, note=note)
    path = "housekeeping" if _can_manage(actor) and actor != target else "housekeeping/log"
    return RedirectResponse(
        _base(request) + f"{path}?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )


@router.post("/entries/{entry_id}/delete")
async def housekeeping_entry_delete(entry_id: str, request: Request,
                                    month: str = Form(""), return_p: str = Form("")):
    actor = resolve_person(request, return_p)
    entry = get_housekeeping_entry(entry_id)
    if not entry or not (_can_manage(actor) or actor == entry.get("person")):
        raise HTTPException(403)
    delete_housekeeping_entry(entry_id)
    path = "housekeeping" if _can_manage(actor) and actor != entry.get("person") else "housekeeping/log"
    return RedirectResponse(
        _base(request) + f"{path}?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )
