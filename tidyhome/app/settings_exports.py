import csv
import json
from io import StringIO

from fastapi.responses import Response


def json_backup_response(payload: dict, filename: str = "tidyhome-backup.json") -> Response:
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return Response(
        body,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _csv_response(filename: str, rows: list[dict]) -> Response:
    out = StringIO()
    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["empty"]
    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return Response(
        out.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
