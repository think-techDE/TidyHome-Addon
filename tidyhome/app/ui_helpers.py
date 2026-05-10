from datetime import date
from urllib.parse import quote

from fastapi import Request

from storage import get_admins


INTERVALS = {
    1: "Täglich", 2: "Alle 2 Tage", 7: "Wöchentlich", 14: "Alle 2 Wochen",
    30: "Monatlich", 90: "Vierteljährlich", 180: "Halbjährlich", 365: "Jährlich",
}


def _ring_chart(value_str: str, pct: int, color: str, label: str, size: int = 70) -> str:
    """SVG donut ring chart with center text label."""
    safe_pct = max(0, min(pct, 100))
    return (
        f'<div style="text-align:center">'
        f'<div style="position:relative;width:{size}px;height:{size}px;margin:0 auto 0.4rem">'
        f'<svg viewBox="0 0 36 36" width="{size}" height="{size}" style="transform:rotate(-90deg)">'
        f'<circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--ring-bg)" stroke-width="3"/>'
        f'<circle cx="18" cy="18" r="15.9" fill="none" stroke="{color}" stroke-width="3"'
        f' stroke-dasharray="{safe_pct} 100" stroke-linecap="round"/>'
        f'</svg>'
        f'<div style="position:absolute;inset:0;display:flex;align-items:center;'
        f'justify-content:center;font-size:0.82rem;font-weight:800;color:var(--text)">'
        f'{value_str}</div>'
        f'</div>'
        f'<div style="font-size:0.65rem;color:var(--muted);font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.05em">{label}</div>'
        f'</div>'
    )


def interval_label(days: int) -> str:
    if days <= 0:
        return "Einmalig"
    return INTERVALS.get(days, f"Alle {days} Tage")


def urgency_class(days: int) -> str:
    if days < 0:
        return "overdue"
    if days == 0:
        return "today"
    if days <= 3:
        return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


def _ha_user(request: Request) -> str:
    return (
        request.headers.get("X-Remote-User-Display-Name") or
        request.headers.get("X-Remote-User-Name", "")
    ).strip()


def person_suffix(person: str = "", separator: str = "?") -> str:
    return f"{separator}p={quote(person)}" if person else ""


def resolve_person(request: Request, p_param: str = "") -> str:
    ha_user = _ha_user(request)
    if p_param and ha_user in get_admins():
        return p_param
    return ha_user or p_param


def _selected(value, current) -> str:
    return " selected" if str(value) == str(current) else ""


def format_date_de(raw: str) -> str:
    if not raw:
        return ""
    try:
        return date.fromisoformat(raw).strftime("%d.%m.%Y")
    except ValueError:
        return raw
