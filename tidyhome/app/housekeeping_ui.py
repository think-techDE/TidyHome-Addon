from datetime import date
from html import escape

from housekeeping_format import current_month, hours, money, status_badge
from i18n import tr
from render import format_date_de, person_suffix
from storage import (get_housekeeper_wage, housekeeping_entry_has_wage,
                     housekeeping_entry_hours, list_housekeeping_entries,
                     list_housekeeper_wages)


def month_nav(base: str, month: str, person: str) -> str:
    psuffix = person_suffix(person, "&") if person else ""
    return f"""
    <form class="month-filter" method="get" action="{base}housekeeping">
      <input type="hidden" name="p" value="{escape(person, quote=True)}">
      <label>{tr("housekeeping.month")}</label>
      <input type="month" name="month" value="{escape(month, quote=True)}">
      <button class="btn btn-ghost btn-sm" type="submit">{tr("housekeeping.show")}</button>
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping?month={current_month()}{psuffix}">{tr("housekeeping.current_month")}</a>
    </form>"""


def entry_form(base: str, helpers: list[str], actor: str, month: str,
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


def entries_for_person(base: str, person: str, actor: str, month: str,
                       read_only: bool = False) -> str:
    entries = list_housekeeping_entries(person, month)
    if not entries:
        return f'<div class="empty" style="padding:1rem">{tr("housekeeping.no_entries_month")}</div>'
    rows = ""
    for entry in entries:
        entry_hours = housekeeping_entry_hours(entry)
        wage = get_housekeeper_wage(entry.get("person", ""), entry.get("date", ""))
        cost = entry_hours * wage
        note = escape(entry.get("note", ""))
        note_part = f'<span>· {note}</span>' if note else ""
        wage_part = f"· {money(wage)}/h" if housekeeping_entry_has_wage(entry) else f"· {tr('housekeeping.no_rate')}"
        summary = f"""
            <span>
              <strong>{format_date_de(entry.get("date", ""))}</strong>
              <small>{escape(entry.get("start_time", ""))} - {escape(entry.get("end_time", ""))}{note_part}</small>
            </span>
            <span class="work-entry-total">{hours(entry_hours)} h · {money(cost)} {wage_part}</span>"""
        if read_only:
            rows += f'<div class="work-entry-summary work-entry-readonly">{summary}</div>'
            continue
        rows += f"""
        <details class="work-entry-details">
          <summary class="work-entry-summary">
            {summary}
          </summary>
          {entry_form(base, [person], actor, month, entry=entry, compact=True)}
        </details>"""
    return rows


def wage_history(base: str, person: str, actor: str, month: str) -> str:
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
            f'<strong>{money(row.get("hourly_wage", 0))}/h</strong>'
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


def housekeeping_warning(item: dict) -> str:
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


def billing_status_form(base: str, person: str, month: str, actor: str,
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


def export_actions(base: str, person: str, month: str) -> str:
    person_q = escape(person, quote=True)
    month_q = escape(month, quote=True)
    return f"""
    <div class="billing-export-actions">
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping/export.csv?person={person_q}&month={month_q}">CSV</a>
      <a class="btn btn-ghost btn-sm" href="{base}housekeeping/export.pdf?person={person_q}&month={month_q}">PDF</a>
    </div>"""


def monthly_cards(summary: dict, base: str, month: str) -> str:
    cards = ""
    for item in summary["people"]:
        person = item["person"]
        cards += f"""
        <div class="housekeeping-month-card">
          <div class="housekeeping-month-card-head">
            <strong>{escape(person)}</strong>
            {status_badge(item.get("status", "open"))}
          </div>
          <div class="housekeeping-month-values">
            <span>{hours(item['hours'])} h</span>
            <span>{money(item['cost'])}</span>
          </div>
          {housekeeping_warning(item)}
          {export_actions(base, person, month)}
        </div>"""
    return f'<div class="housekeeping-person-grid">{cards}</div>' if cards else ""


def quick_time_script() -> str:
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
