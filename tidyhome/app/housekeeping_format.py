from datetime import date

from i18n import tr


def current_month() -> str:
    return date.today().strftime("%Y-%m")


def month_value(month: str = "") -> str:
    return month[:7] if month and len(month) >= 7 else current_month()


def money(value: float) -> str:
    return f"{value:,.2f} \u20ac".replace(",", "X").replace(".", ",").replace("X", ".")


def hours(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def decimal(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def status_label(status: str) -> str:
    return {
        "open": tr("housekeeping.status.open"),
        "reviewed": tr("housekeeping.status.reviewed"),
        "paid": tr("housekeeping.status.paid"),
    }.get(status, tr("housekeeping.status.open"))


def status_badge(status: str) -> str:
    cls = "ok" if status == "paid" else "warn" if status == "reviewed" else "neutral"
    return f'<span class="badge {cls}">{status_label(status)}</span>'


def month_from_date(value: str = "") -> str:
    return value[:7] if value and len(value) >= 7 else current_month()
