import csv
from io import StringIO

from housekeeping_format import decimal, money, status_label
from storage import (get_housekeeping_billing, get_housekeeping_month_summary,
                     housekeeping_entry_cost, housekeeping_entry_has_wage,
                     housekeeping_entry_hours, housekeeping_entry_wage,
                     list_housekeeping_entries)


def housekeeping_export_filename(person: str, month: str, suffix: str) -> str:
    return f"tidyhome-{person}-{month}.{suffix}".replace(" ", "_")


def housekeeping_export_rows(person: str, month: str) -> list[dict]:
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


def housekeeping_csv_content(person: str, month: str) -> str:
    output = StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Person", "Monat", "Status", "Datum", "Start", "Ende", "Pause Minuten",
        "Stunden", "Stundensatz", "Kosten", "Stundensatz vorhanden", "Notiz",
    ])
    status = status_label(get_housekeeping_billing(person, month).get("status", "open"))
    for row in housekeeping_export_rows(person, month):
        writer.writerow([
            person, month, status, row["date"], row["start"], row["end"], row["break"],
            decimal(row["hours"]), decimal(row["wage"]), decimal(row["cost"]),
            "ja" if row["has_wage"] else "nein", row["note"],
        ])
    return output.getvalue()


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
        f"Status: {status_label(billing.get('status', 'open'))}",
        f"Stunden: {decimal(item['hours'])}",
        f"Gesamt: {money(item['cost'])}",
        "",
        "Datum       Start  Ende   Pause  Stunden  Satz       Kosten    Notiz",
    ]
    for row in housekeeping_export_rows(person, month):
        lines.append(
            f"{row['date']}  {row['start']:>5}  {row['end']:>5}  "
            f"{str(row['break']).rjust(5)}  {decimal(row['hours']).rjust(7)}  "
            f"{money(row['wage']).rjust(9)}  {money(row['cost']).rjust(9)}  {row['note']}"
        )
    if item.get("missing_wage_entries"):
        lines.extend(["", "Hinweis: Es gibt Eintr\u00e4ge ohne g\u00fcltigen Stundensatz."])
    return lines


def housekeeping_pdf_content(person: str, month: str) -> bytes:
    return _simple_pdf(_invoice_lines(person, month))
