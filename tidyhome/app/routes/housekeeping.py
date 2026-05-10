from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from housekeeping_exports import (housekeeping_csv_content,
                                  housekeeping_export_filename,
                                  housekeeping_pdf_content)
from housekeeping_format import (month_from_date as _month_from_date,
                                 month_value as _month_value)
from housekeeping_ui import dashboard_content, log_content
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
    content = dashboard_content(base, actor, month, helpers, summary)
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
    content = log_content(base, actor, month, item, billing, read_only)
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
