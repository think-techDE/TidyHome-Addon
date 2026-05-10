import csv
from datetime import date
from html import escape
from io import StringIO

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from i18n import tr
from render import _base, _icon, format_date_de, person_suffix, render, resolve_person
from storage import (add_housekeeping_entry, delete_housekeeping_entry, get_admins,
                     get_housekeeping_billing,
                     get_housekeeper_wage, get_housekeeping_entry,
                     get_housekeeping_month_summary, get_person_settings,
                     housekeeping_entry_cost, housekeeping_entry_has_wage,
                     housekeeping_entry_hours, housekeeping_entry_wage,
                     is_housekeeping_month_paid, list_housekeeping_entries,
                     list_housekeeper_wages, list_people_by_role,
                     save_housekeeper_wage, set_housekeeping_billing_status,
                     update_housekeeper_wage, update_housekeeping_entry)

router = APIRouter(prefix="/housekeeping")


def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def _month_value(month: str = "") -> str:
    return month[:7] if month and len(month) >= 7 else _current_month()


def _money(value: float) -> str:
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _hours(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def _decimal(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def _status_label(status: str) -> str:
    return {
        "open": tr("housekeeping.status.open"),
        "reviewed": tr("housekeeping.status.reviewed"),
        "paid": tr("housekeeping.status.paid"),
    }.get(status, tr("housekeeping.status.open"))


def _status_badge(status: str) -> str:
    cls = "ok" if status == "paid" else "warn" if status == "reviewed" else "neutral"
    return f'<span class="badge {cls}">{_status_label(status)}</span>'


def _month_from_date(value: str = "") -> str:
    return value[:7] if value and len(value) >= 7 else _current_month()


def _can_manage(person: str) -> bool:
    if not person:
        return False
    return person in set(get_admins()) or get_person_settings(person).get("role") == "parent"


def _is_housekeeper(person: str) -> bool:
    return get_person_settings(person).get("role") == "housekeeper"


def _is_known_housekeeper(person: str) -> bool:
    return person in set(list_people_by_role("housekeeper"))


def _month_locked_for(actor: str, person: str, month: str) -> bool:
    return (
        bool(actor and person and actor == person)
        and not _can_manage(actor)
        and is_housekeeping_month_paid(person, month)
    )


def _month_nav(base: str, month: str, person: str) -> str:
    psuffix = person_suffix(person, "&") if person else ""
    return f"""
    <form class="month-filter" method="get" action="{base}housekeeping">
      <input type="hidden" name="p" value="{escape(person, quote=True)}">
      <label>{tr("housekeeping.month")}</label>
      <input type="month" name="month" value="{escape(month, quote=True)}">
      <button class="btn btn-ghost btn-sm" type="submit">{tr("housekeeping.show")}</button>
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping?month={_current_month()}{psuffix}">{tr("housekeeping.current_month")}</a>
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
    button = tr("housekeeping.correct") if entry.get("id") else tr("housekeeping.save_time")
    person_field = f'<input type="hidden" name="person" value="{escape(target, quote=True)}">'
    if not force_person and helpers:
        opts = "".join(
            f'<option value="{escape(pn, quote=True)}"{" selected" if pn == target else ""}>{escape(pn)}</option>'
            for pn in helpers
        )
        person_field = f"""
        <div class="form-group">
          <label>{tr("role.housekeeper")}</label>
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
            f'onclick="return confirm(\'{tr("housekeeping.delete_entry_confirm")}\')">{tr("common.delete")}</button>'
        )
    return f"""
    <form class="{wrapper_cls}" method="post" action="{action}">
      <input type="hidden" name="return_p" value="{escape(actor, quote=True)}">
      <input type="hidden" name="month" value="{escape(month, quote=True)}">
      {person_field}
      <div class="quick-time-actions">
        <button class="btn btn-ghost btn-sm" type="button" data-hk-quick="today">{tr("housekeeping.today")}</button>
        <button class="btn btn-ghost btn-sm" type="button" data-hk-quick="start">{tr("housekeeping.start_now")}</button>
        <button class="btn btn-ghost btn-sm" type="button" data-hk-quick="end">{tr("housekeeping.end_now")}</button>
        <button class="btn btn-ghost btn-sm" type="button" data-hk-break="0">0 Min.</button>
        <button class="btn btn-ghost btn-sm" type="button" data-hk-break="15">15 Min.</button>
        <button class="btn btn-ghost btn-sm" type="button" data-hk-break="30">30 Min.</button>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label>{tr("housekeeping.date")}</label>
          <input type="date" name="work_date" value="{date_val}" required>
        </div>
        <div class="form-group">
          <label>{tr("housekeeping.break_minutes")}</label>
          <input type="number" name="break_minutes" min="0" max="600" value="{break_val}">
        </div>
        <div class="form-group">
          <label>{tr("housekeeping.start")}</label>
          <input type="time" name="start_time" value="{start_val}" required>
        </div>
        <div class="form-group">
          <label>{tr("housekeeping.end")}</label>
          <input type="time" name="end_time" value="{end_val}" required>
        </div>
      </div>
      <div class="form-group">
        <label>{tr("housekeeping.note_optional")}</label>
        <input name="note" value="{note_val}" placeholder="{tr("housekeeping.note_placeholder")}">
      </div>
      <div class="settings-actions">
        <button class="btn btn-primary btn-sm" type="submit">{button}</button>
        {delete_button}
      </div>
    </form>"""


def _entries_for_person(base: str, person: str, actor: str, month: str,
                        read_only: bool = False) -> str:
    entries = list_housekeeping_entries(person, month)
    if not entries:
        return f'<div class="empty" style="padding:1rem">{tr("housekeeping.no_entries_month")}</div>'
    rows = ""
    for entry in entries:
        hours = housekeeping_entry_hours(entry)
        wage = get_housekeeper_wage(entry.get("person", ""), entry.get("date", ""))
        cost = hours * wage
        note = escape(entry.get("note", ""))
        note_part = f'<span>· {note}</span>' if note else ""
        wage_part = f"· {_money(wage)}/h" if housekeeping_entry_has_wage(entry) else f"· {tr('housekeeping.no_rate')}"
        summary = f"""
            <span>
              <strong>{format_date_de(entry.get("date", ""))}</strong>
              <small>{escape(entry.get("start_time", ""))} - {escape(entry.get("end_time", ""))}{note_part}</small>
            </span>
            <span class="work-entry-total">{_hours(hours)} h · {_money(cost)} {wage_part}</span>"""
        if read_only:
            rows += f'<div class="work-entry-summary work-entry-readonly">{summary}</div>'
            continue
        rows += f"""
        <details class="work-entry-details">
          <summary class="work-entry-summary">
            {summary}
          </summary>
          {_entry_form(base, [person], actor, month, entry=entry, compact=True)}
        </details>"""
    return rows


def _wage_history(base: str, person: str, actor: str, month: str) -> str:
    rows = list_housekeeper_wages(person)
    if not rows:
        return f'<div class="muted wage-history-empty">{tr("housekeeping.no_wage_history")}</div>'
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
            period = tr("housekeeping.no_period")
        wage_id = escape(row.get("id", ""), quote=True)
        valid_from = escape(valid_from, quote=True)
        valid_to = escape(valid_to, quote=True)
        items += (
            '<details class="wage-history-row">'
            '<summary>'
            f'<strong>{_money(row.get("hourly_wage", 0))}/h</strong>'
            f'<span>{escape(period)}</span>'
            '</summary>'
            f'<form class="wage-edit-form" method="post" action="{base}housekeeping/wage/{wage_id}">'
            f'<input type="hidden" name="return_p" value="{escape(actor, quote=True)}">'
            f'<input type="hidden" name="month" value="{escape(month, quote=True)}">'
            f'<input type="hidden" name="person" value="{escape(person, quote=True)}">'
            '<div class="grid-2">'
            f'<div class="form-group"><label>{tr("housekeeping.hourly_wage")}</label>'
            f'<input name="hourly_wage" inputmode="decimal" value="{row.get("hourly_wage", 0):.2f}"></div>'
            f'<div class="form-group"><label>{tr("housekeeping.valid_from")}</label>'
            f'<input type="date" name="valid_from" value="{valid_from}"></div>'
            f'<div class="form-group"><label>{tr("housekeeping.valid_to")}</label>'
            f'<input type="date" name="valid_to" value="{valid_to}"></div>'
            '</div>'
            f'<button class="btn btn-ghost btn-sm" type="submit">{tr("housekeeping.correct_rate")}</button>'
            '</form>'
            '</details>'
        )
    return f'<div class="wage-history">{items}</div>'


def _housekeeping_warning(item: dict) -> str:
    warnings = []
    if not item.get("has_wage_history"):
        warnings.append(tr("housekeeping.no_rate_configured"))
    if item.get("missing_wage_entries"):
        dates = ", ".join(format_date_de(d) for d in item.get("missing_wage_dates", [])[:3])
        suffix = f" ({dates})" if dates else ""
        warnings.append(f"{item['missing_wage_entries']} {tr('housekeeping.entries_without_rate')}{suffix}.")
    if not warnings:
        return ""
    return '<div class="housekeeping-warning">' + " ".join(escape(w) for w in warnings) + "</div>"


def _billing_status_form(base: str, person: str, month: str, actor: str,
                         status: str) -> str:
    options = "".join(
        f'<option value="{key}"{" selected" if key == status else ""}>{label}</option>'
        for key, label in [("open", tr("housekeeping.status.open")), ("reviewed", tr("housekeeping.status.reviewed")), ("paid", tr("housekeeping.status.paid"))]
    )
    return f"""
    <form class="billing-status-form" method="post" action="{base}housekeeping/status">
      <input type="hidden" name="return_p" value="{escape(actor, quote=True)}">
      <input type="hidden" name="month" value="{escape(month, quote=True)}">
      <input type="hidden" name="person" value="{escape(person, quote=True)}">
      <select name="status">{options}</select>
      <button class="btn btn-ghost btn-sm" type="submit">{tr("housekeeping.save_status")}</button>
    </form>"""


def _export_actions(base: str, person: str, month: str) -> str:
    person_q = escape(person, quote=True)
    month_q = escape(month, quote=True)
    return f"""
    <div class="billing-export-actions">
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping/export.csv?person={person_q}&month={month_q}">CSV</a>
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping/export.pdf?person={person_q}&month={month_q}">PDF</a>
    </div>"""


def _monthly_cards(summary: dict, base: str, month: str) -> str:
    cards = ""
    for item in summary["people"]:
        person = item["person"]
        cards += f"""
        <div class="housekeeping-month-card">
          <div class="housekeeping-month-card-head">
            <strong>{escape(person)}</strong>
            {_status_badge(item.get("status", "open"))}
          </div>
          <div class="housekeeping-month-values">
            <span>{_hours(item['hours'])} h</span>
            <span>{_money(item['cost'])}</span>
          </div>
          {_housekeeping_warning(item)}
          {_export_actions(base, person, month)}
        </div>"""
    return f'<div class="housekeeping-person-grid">{cards}</div>' if cards else ""


def _quick_time_script() -> str:
    return """
    <script>
    (function(){
      function pad(value){ return String(value).padStart(2, '0'); }
      function localDate(now){ return now.getFullYear() + '-' + pad(now.getMonth()+1) + '-' + pad(now.getDate()); }
      function localTime(now){ return pad(now.getHours()) + ':' + pad(now.getMinutes()); }
      document.addEventListener('click', function(event){
        var quick = event.target.closest('[data-hk-quick]');
        var pause = event.target.closest('[data-hk-break]');
        if (!quick && !pause) return;
        var form = event.target.closest('form');
        if (!form) return;
        if (quick) {
          var now = new Date();
          var action = quick.getAttribute('data-hk-quick');
          if (action === 'today') {
            var dateInput = form.querySelector('input[name="work_date"]');
            if (dateInput) dateInput.value = localDate(now);
          }
          if (action === 'start') {
            var startInput = form.querySelector('input[name="start_time"]');
            if (startInput) startInput.value = localTime(now);
          }
          if (action === 'end') {
            var endInput = form.querySelector('input[name="end_time"]');
            if (endInput) endInput.value = localTime(now);
          }
        }
        if (pause) {
          var breakInput = form.querySelector('input[name="break_minutes"]');
          if (breakInput) breakInput.value = pause.getAttribute('data-hk-break') || '0';
        }
      });
    })();
    </script>"""


def _housekeeping_export_rows(person: str, month: str) -> list[dict]:
    entries = sorted(
        list_housekeeping_entries(person, month),
        key=lambda e: (e.get("date", ""), e.get("start_time", "")),
    )
    rows = []
    for entry in entries:
        hours = housekeeping_entry_hours(entry)
        wage = housekeeping_entry_wage(entry)
        cost = housekeeping_entry_cost(entry)
        rows.append({
            "date": entry.get("date", ""),
            "start": entry.get("start_time", ""),
            "end": entry.get("end_time", ""),
            "break": entry.get("break_minutes", 0),
            "hours": hours,
            "wage": wage,
            "cost": cost,
            "note": entry.get("note", ""),
            "has_wage": housekeeping_entry_has_wage(entry),
        })
    return rows


def _pdf_escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf(lines: list[str]) -> bytes:
    per_page = 45
    pages = [lines[i:i + per_page] for i in range(0, len(lines), per_page)] or [[]]
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    kids = []
    for index, page_lines in enumerate(pages):
        page_obj = 4 + index * 2
        content_obj = page_obj + 1
        kids.append(f"{page_obj} 0 R")
        commands = ["BT", "/F1 10 Tf", "14 TL", "50 800 Td"]
        for line_index, line in enumerate(page_lines):
            prefix = "" if line_index == 0 else "T* "
            commands.append(f"{prefix}({_pdf_escape(line)}) Tj")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", "replace")
        objects[page_obj] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj} 0 R >>"
        ).encode("latin-1")
        objects[content_obj] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") +
            stream +
            b"\nendstream"
        )
    objects[2] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>".encode("latin-1")

    output = bytearray(b"%PDF-1.4\n")
    offsets = {0: 0}
    for obj_id in sorted(objects):
        offsets[obj_id] = len(output)
        output.extend(f"{obj_id} 0 obj\n".encode("latin-1"))
        output.extend(objects[obj_id])
        output.extend(b"\nendobj\n")
    xref_pos = len(output)
    max_id = max(objects)
    output.extend(f"xref\n0 {max_id + 1}\n".encode("latin-1"))
    output.extend(b"0000000000 65535 f \n")
    for obj_id in range(1, max_id + 1):
        output.extend(f"{offsets.get(obj_id, 0):010d} 00000 n \n".encode("latin-1"))
    output.extend(
        f"trailer\n<< /Size {max_id + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
        .encode("latin-1")
    )
    return bytes(output)


def _invoice_lines(person: str, month: str) -> list[str]:
    summary = get_housekeeping_month_summary(person, month)
    item = summary["people"][0] if summary["people"] else {"hours": 0, "cost": 0}
    billing = get_housekeeping_billing(person, month)
    lines = [
        "TidyHome Haushaltshilfe-Abrechnung",
        f"Person: {person}",
        f"Monat: {month}",
        f"Status: {_status_label(billing.get('status', 'open'))}",
        f"Stunden: {_decimal(item['hours'])}",
        f"Gesamt: {_money(item['cost'])}",
        "",
        "Datum       Start  Ende   Pause  Stunden  Satz       Kosten    Notiz",
    ]
    for row in _housekeeping_export_rows(person, month):
        lines.append(
            f"{row['date']}  {row['start']:>5}  {row['end']:>5}  "
            f"{str(row['break']).rjust(5)}  {_decimal(row['hours']).rjust(7)}  "
            f"{_money(row['wage']).rjust(9)}  {_money(row['cost']).rjust(9)}  {row['note']}"
        )
    if item.get("missing_wage_entries"):
        lines.extend(["", "Hinweis: Es gibt Einträge ohne gültigen Stundensatz."])
    return lines


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
              <p class="muted">{item['entries']} {tr("housekeeping.entries")} · {_hours(item['hours'])} h · {_money(item['cost'])}</p>
            </div>
            <div class="housekeeping-card-badges">
              {_status_badge(item.get("status", "open"))}
              <span class="badge ok">{tr("housekeeping.current_rate")} {_money(item['hourly_wage'])}/h</span>
            </div>
          </div>
          {_housekeeping_warning(item)}
          <div class="billing-tools">
            {_billing_status_form(base, person, month, actor, item.get("status", "open"))}
            {_export_actions(base, person, month)}
          </div>
          <details class="housekeeping-subdetails">
            <summary class="housekeeping-subsummary">
              <span>
                <strong>{tr("housekeeping.wage_history")}</strong>
                <small>{tr("housekeeping.wage_history_hint")}</small>
              </span>
              <span class="details-caret">▾</span>
            </summary>
            <div class="housekeeping-subbody">
              <form class="wage-form" method="post" action="{base}housekeeping/wage">
                <input type="hidden" name="return_p" value="{escape(actor, quote=True)}">
                <input type="hidden" name="month" value="{escape(month, quote=True)}">
                <input type="hidden" name="person" value="{escape(person, quote=True)}">
                <div class="form-group">
                  <label>{tr("housekeeping.hourly_wage")}</label>
                  <input name="hourly_wage" inputmode="decimal" value="{item['hourly_wage']:.2f}">
                </div>
                <div class="form-group">
                  <label>{tr("housekeeping.valid_from")}</label>
                  <input type="date" name="valid_from" value="{date.today().isoformat()}" required>
                </div>
                <div class="form-group">
                  <label>{tr("housekeeping.valid_to")}</label>
                  <input type="date" name="valid_to">
                </div>
                <button class="btn btn-ghost btn-sm" type="submit">{tr("housekeeping.add_rate")}</button>
              </form>
              {_wage_history(base, person, actor, month)}
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
              <strong>{tr("housekeeping.record_worktime")}</strong>
              <small>{tr("housekeeping.record_worktime_hint")}</small>
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
          <h3>{tr("housekeeping.no_housekeepers")}</h3>
          <p class="muted" style="margin-top:0.25rem">
            {tr("housekeeping.no_housekeepers_hint")}
          </p>
        </div>"""

    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">{tr("housekeeping.housekeepers")}</div>
        <div class="hero-title">{tr("housekeeping.work_times")}</div>
        <div class="muted">{tr("housekeeping.monthly_overview")}</div>
      </div>
      <div class="page-hero-actions">
        <span class="badge ok">{escape(month)}</span>
      </div>
    </div>
    <div class="housekeeping-summary-grid">
      <div class="today-stat"><div class="today-value">{_hours(summary['total_hours'])}</div><div class="today-label">{tr("housekeeping.hours")}</div></div>
      <div class="today-stat"><div class="today-value">{_money(summary['total_cost'])}</div><div class="today-label">{tr("housekeeping.total_cost")}</div></div>
      <div class="today-stat"><div class="today-value">{len(helpers)}</div><div class="today-label">{tr("housekeeping.housekeepers")}</div></div>
    </div>
    {_month_nav(base, month, actor)}
    {_monthly_cards(summary, base, month)}
    {entry_card}
    <div class="admin-stack">{helper_cards}</div>
    {_quick_time_script()}"""
    return render(content, request, page="home", person=actor)


@router.get("/export.csv")
async def housekeeping_export_csv(request: Request, person: str, month: str,
                                  p: str = ""):
    actor = resolve_person(request, p)
    if not _can_manage(actor) or not _is_known_housekeeper(person):
        raise HTTPException(403)
    month = _month_value(month)
    output = StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Person", "Monat", "Status", "Datum", "Start", "Ende", "Pause Minuten",
        "Stunden", "Stundensatz", "Kosten", "Stundensatz vorhanden", "Notiz",
    ])
    status = _status_label(get_housekeeping_billing(person, month).get("status", "open"))
    for row in _housekeeping_export_rows(person, month):
        writer.writerow([
            person, month, status, row["date"], row["start"], row["end"], row["break"],
            _decimal(row["hours"]), _decimal(row["wage"]), _decimal(row["cost"]),
            "ja" if row["has_wage"] else "nein", row["note"],
        ])
    filename = f"tidyhome-{person}-{month}.csv".replace(" ", "_")
    return Response(
        output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export.pdf")
async def housekeeping_export_pdf(request: Request, person: str, month: str,
                                  p: str = ""):
    actor = resolve_person(request, p)
    if not _can_manage(actor) or not _is_known_housekeeper(person):
        raise HTTPException(403)
    month = _month_value(month)
    filename = f"tidyhome-{person}-{month}.pdf".replace(" ", "_")
    return Response(
        _simple_pdf(_invoice_lines(person, month)),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
    billing = get_housekeeping_billing(actor, month)
    read_only = billing.get("status") == "paid" and not _can_manage(actor)
    entries = _entries_for_person(base, actor, actor, month, read_only=read_only)
    psuffix = person_suffix(actor)
    entry_form = (
        f'<div class="housekeeping-warning">{tr("housekeeping.paid_readonly")}</div>'
        if read_only else
        f"""
    <details class="card housekeeping-foldout">
      <summary class="housekeeping-foldout-head">
        <span>
          <strong>{tr("housekeeping.record_time")}</strong>
          <small>{tr("housekeeping.record_time_month")}</small>
        </span>
        <span class="details-caret">▾</span>
      </summary>
      <div class="housekeeping-foldout-body">
        {_entry_form(base, [actor], actor, month, force_person=actor)}
      </div>
    </details>"""
    )
    content = f"""
    <div class="hero-card page-hero">
      <div>
        <div class="hero-eyebrow">{tr("housekeeping.worktime")}</div>
        <div class="hero-title">{escape(actor)}</div>
        <div class="muted">{tr("housekeeping.captured_state")} {escape(month)}</div>
      </div>
      <div class="page-hero-actions">
        {_status_badge(billing.get("status", "open"))}
        <a class="btn btn-ghost btn-sm" href="{base}{psuffix}">{tr("nav.home")}</a>
      </div>
    </div>
    <div class="housekeeping-summary-grid">
      <div class="today-stat"><div class="today-value">{_hours(item['hours'])}</div><div class="today-label">{tr("housekeeping.hours")}</div></div>
      <div class="today-stat"><div class="today-value">{_money(item['cost'])}</div><div class="today-label">{tr("housekeeping.earned")}</div></div>
      <div class="today-stat"><div class="today-value">{_money(item['hourly_wage'])}</div><div class="today-label">{tr("housekeeping.current_rate")}</div></div>
    </div>
    <form class="month-filter" method="get" action="{base}housekeeping/log">
      <input type="hidden" name="p" value="{escape(actor, quote=True)}">
      <label>{tr("housekeeping.month")}</label>
      <input type="month" name="month" value="{escape(month, quote=True)}">
      <button class="btn btn-ghost btn-sm" type="submit">{tr("housekeeping.show")}</button>
    </form>
    {entry_form}
    <div class="card card-flush">
      <div class="score-activity-head">
        <h3>{tr("housekeeping.captured_times")}</h3>
        <div class="muted">{tr("housekeeping.can_correct")}</div>
      </div>
      {entries}
    </div>
    {_quick_time_script()}"""
    return render(content, request, page="home", person=actor)


@router.post("/status")
async def housekeeping_status_save(request: Request, person: str = Form(...),
                                   month: str = Form(""),
                                   status: str = Form("open"),
                                   return_p: str = Form("")):
    actor = resolve_person(request, return_p)
    if not _can_manage(actor) or not _is_known_housekeeper(person):
        raise HTTPException(403)
    set_housekeeping_billing_status(person, _month_value(month), status, updated_by=actor)
    return RedirectResponse(
        _base(request) + f"housekeeping?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )


@router.post("/wage/{wage_id}")
async def housekeeping_wage_update(wage_id: str, request: Request,
                                   person: str = Form(...),
                                   hourly_wage: str = Form("0"),
                                   valid_from: str = Form(""),
                                   valid_to: str = Form(""),
                                   month: str = Form(""),
                                   return_p: str = Form("")):
    actor = resolve_person(request, return_p)
    if not _can_manage(actor) or not _is_known_housekeeper(person):
        raise HTTPException(403)
    updated = update_housekeeper_wage(
        wage_id, person, hourly_wage, valid_from=valid_from, valid_to=valid_to
    )
    if not updated:
        raise HTTPException(404)
    return RedirectResponse(
        _base(request) + f"housekeeping?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )


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
    if _month_locked_for(actor, target, _month_from_date(work_date)):
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
    if _month_locked_for(actor, entry.get("person", ""), _month_from_date(entry.get("date", ""))):
        raise HTTPException(403)
    if _month_locked_for(actor, target, _month_from_date(work_date)):
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
    if _month_locked_for(actor, entry.get("person", ""), _month_from_date(entry.get("date", ""))):
        raise HTTPException(403)
    delete_housekeeping_entry(entry_id)
    path = "housekeeping" if _can_manage(actor) and actor != entry.get("person") else "housekeeping/log"
    return RedirectResponse(
        _base(request) + f"{path}?month={_month_value(month)}{person_suffix(actor, '&')}",
        status_code=303,
    )
