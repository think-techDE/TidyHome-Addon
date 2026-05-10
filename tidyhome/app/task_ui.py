from datetime import date, timedelta
from html import escape

from i18n import tr
from models import Task
from ui_helpers import INTERVALS, _selected, format_date_de, interval_label, person_suffix
from ui_icons import _icon, _icon_chooser, _task_icon

_EFFORT_LABELS = {"low": tr("effort.low"), "medium": tr("effort.medium"), "high": tr("effort.high")}
_ONETIME_INTERVAL = "once"


def _parse_interval_choice(value: str, legacy_onetime: str = "") -> tuple[int, bool]:
    value = str(value or _ONETIME_INTERVAL).strip()
    if value == _ONETIME_INTERVAL:
        return 0, True
    try:
        days = int(value)
    except ValueError:
        return 0, True
    if days <= 0:
        return 0, True
    return days, legacy_onetime == "1"


def _task_return_path(return_to: str = "") -> str:
    return "tasks/history" if return_to == "history" else "tasks"


def _valid_day(raw: str = "") -> str:
    try:
        return date.fromisoformat(raw or "").isoformat()
    except ValueError:
        return ""


def _week_strip(tasks: list[Task], selected_day: str = "", person: str = "") -> str:
    today = date.today()
    psuffix_amp = person_suffix(person, "&")
    reset_suffix = person_suffix(person)
    items = ""
    for offset in range(7):
        day = today + timedelta(days=offset)
        iso = day.isoformat()
        due_tasks = [
            t for t in tasks
            if not t.is_paused() and t.next_due().isoformat() == iso
        ]
        active = " active" if selected_day == iso else ""
        label = tr("date.today") if offset == 0 else tr("date.tomorrow") if offset == 1 else day.strftime("%a")
        items += (
            f'<a class="week-day{active}" href="tasks?day={iso}{psuffix_amp}">'
            f'<span>{label}</span><strong>{len(due_tasks)}</strong>'
            f'<small>{day.strftime("%d.%m.")}</small></a>'
        )
    all_active = "" if selected_day else " active"
    return (
        '<div class="week-strip">'
        f'<a class="week-day week-day-all{all_active}" href="tasks{reset_suffix}">'
        f'<span>{tr("common.all")}</span><strong>•</strong><small>{tr("tasks.filter")}</small></a>'
        f'{items}</div>'
    )


def _task_history_row(task: Task, person: str = "") -> str:
    psuffix = person_suffix(person)
    qs = f"{psuffix}{'&' if psuffix else '?'}return_to=history"
    assigned = ", ".join(task.assigned_to) if task.assigned_to else "Nicht zugeordnet"
    done_label = format_date_de(task.last_done or "")
    if task.active:
        status_badge = '<span class="badge ok">Erledigt</span>'
        action_label = "Erneut öffnen"
    else:
        status_badge = '<span class="badge today">Archiviert</span>'
        action_label = "Wieder aktivieren"
    interval = "Einmalig" if task.onetime else interval_label(task.interval_days)
    done_meta = f"Erledigt am {done_label}" if done_label else "Archiviert"
    return f"""
    <div class="task-row history-row">
      {_task_icon(task.name, task.room, icon=task.icon, size=40)}
      <div class="task-body">
        <div class="task-header">
          <span class="task-name">{escape(task.name)}</span>
          <div class="task-badges">{status_badge}</div>
        </div>
        <div class="task-date">
          <span>{escape(done_meta)}</span>
          <span>· {escape(task.room)}</span>
          <span>· {escape(assigned)}</span>
          <span>· {escape(interval)}</span>
        </div>
      </div>
      <div class="task-actions">
        <a class="icon-btn" href="tasks/{task.id}/edit{qs}"
           title="Bearbeiten">{_icon("edit", 16)}</a>
        <form class="inline" method="post" action="tasks/{task.id}/reactivate">
          <input type="hidden" name="return_p" value="{escape(person)}">
          <input type="hidden" name="return_to" value="history">
          <button class="icon-btn success" title="{action_label}">{_icon("plus", 17)}</button>
        </form>
        <a class="icon-btn danger" href="tasks/{task.id}/delete{qs}"
           onclick="return confirm('Aufgabe endgültig löschen?')" title="Löschen">
          {_icon("trash", 16)}
        </a>
      </div>
    </div>"""


def _template_form_html(template: dict | None, areas: list[str], persons: list[str],
                        base: str, person: str = "") -> str:
    template = template or {}
    action = (
        f"{base}tasks/templates/{template.get('id')}/edit"
        if template.get("id") else f"{base}tasks/templates"
    )
    title = escape(template.get("name", "Neue Vorlage"))
    task_name = escape(template.get("task_name", ""), quote=True)
    room = template.get("room", "")
    interval = _ONETIME_INTERVAL if template.get("onetime", True) else str(template.get("interval_days", 0))
    points = int(template.get("points", 10) or 10)
    selected_people = set(template.get("assigned_to", []) or ([person] if person else []))
    important_checked = "checked" if template.get("important") else ""
    effort = template.get("effort", "")
    icon = template.get("icon", "")
    room_opts = "".join(
        f'<option value="{escape(r, quote=True)}"{_selected(r, room)}>{escape(r)}</option>'
        for r in areas
    )
    person_boxes = "".join(
        f'<label class="option-card" style="padding:0.55rem 0.7rem">'
        f'<input type="checkbox" name="assigned_to" value="{escape(pn, quote=True)}"'
        f'{" checked" if pn in selected_people else ""}><span>{escape(pn)}</span></label>'
        for pn in persons
    )
    interval_opts = (
        f'<option value="{_ONETIME_INTERVAL}"{_selected(_ONETIME_INTERVAL, interval)}>'
        'Einmalig (nach Erledigung archiviert)</option>'
    )
    interval_opts += "".join(
        f'<option value="{d}"{_selected(d, interval)}>{label}</option>'
        for d, label in INTERVALS.items()
    )
    effort_btns = "".join(
        f'<label class="effort-choice effort-{ef}">'
        f'<input type="radio" name="effort" value="{ef}"'
        f'{" checked" if effort == ef else ""}><span>{label}</span></label>'
        for ef, label in _EFFORT_LABELS.items()
    )
    effort_btns += (
        f'<label class="effort-choice effort-none">'
        f'<input type="radio" name="effort" value=""{" checked" if not effort else ""}>'
        f'<span>{tr("effort.none")}</span></label>'
    )
    return f"""
    <form class="template-form" method="post" action="{action}">
      <input type="hidden" name="return_p" value="{escape(person, quote=True)}">
      <div class="grid-2">
        <div class="form-group">
          <label>{tr("tasks.template_name")}</label>
          <input name="name" required value="{title}" placeholder="z.B. Frühjahrsputz">
        </div>
        <div class="form-group">
          <label>{tr("tasks.name")}</label>
          <input name="task_name" required value="{task_name}" placeholder="z.B. Fenster putzen">
        </div>
        <div class="form-group">
          <label>{tr("form.room")}</label>
          <select name="room">{room_opts}</select>
        </div>
        <div class="form-group">
          <label>Intervall</label>
          <select name="interval_days">{interval_opts}</select>
        </div>
        <div class="form-group">
          <label>{tr("form.points")}</label>
          <input name="points" type="number" min="1" max="100" value="{points}">
        </div>
        <div class="form-group settings-check-field">
          <label class="settings-check">
            <input type="checkbox" name="important" value="1" {important_checked}>
            <span>{tr("task.important")}</span>
          </label>
        </div>
      </div>
      <div class="form-group">
        <label>{tr("effort.label")}</label>
        <div class="effort-picker">{effort_btns}</div>
      </div>
      <div class="form-group">
        <label>{tr("form.assigned_to")}</label>
        <div class="task-assignee-grid">{person_boxes}</div>
      </div>
      <div class="form-group">
        <label>{tr("task.icon")}</label>
        {_icon_chooser(icon)}
      </div>
      <button class="btn btn-primary btn-sm" type="submit">{tr("tasks.save_template")}</button>
    </form>"""
