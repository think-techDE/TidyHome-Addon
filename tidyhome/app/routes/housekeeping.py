from datetime import date
from html import escape

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from housekeeping_exports import (housekeeping_csv_content,
                                  housekeeping_export_filename,
                                  housekeeping_pdf_content)
from housekeeping_format import (hours as _hours, money as _money,
                                 month_from_date as _month_from_date,
                                 month_value as _month_value,
                                 status_badge as _status_badge)
from housekeeping_ui import (billing_status_form as _billing_status_form,
                             entries_for_person as _entries_for_person,
                             entry_form as _entry_form,
                             export_actions as _export_actions,
                             housekeeping_warning as _housekeeping_warning,
                             month_nav as _month_nav,
                             monthly_cards as _monthly_cards,
                             quick_time_script as _quick_time_script,
                             wage_history as _wage_history)
from i18n import tr
from render import _base, person_suffix, render, resolve_person
from storage import (add_housekeeping_entry, delete_housekeeping_entry, get_admins,
                     get_housekeeping_billing,
                     get_housekeeping_entry, get_housekeeping_month_summary,
                     get_person_settings, is_housekeeping_month_paid,
                     list_people_by_role,
                     save_housekeeper_wage, set_housekeeping_billing_status,
                     update_housekeeper_wage, update_housekeeping_entry)

router = APIRouter(prefix="/housekeeping")


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
    filename = housekeeping_export_filename(person, month, "csv")
    return Response(
        housekeeping_csv_content(person, month),
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
    filename = housekeeping_export_filename(person, month, "pdf")
    return Response(
        housekeeping_pdf_content(person, month),
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
