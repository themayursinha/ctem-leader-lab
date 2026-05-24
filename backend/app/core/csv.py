import csv
import io
from typing import Any

from fastapi import File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse


MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_ROWS = 10_000
OPTIONAL_CSV_FIELDS = {
    "cvss", "source", "source_reference", "first_seen", "last_seen",
    "validated_at", "evidence_owner", "evidence_expires_at",
}


def sanitize_csv(value: Any) -> str:
    s = str(value) if value is not None else ""
    if s and s[0] in ("=", "+", "-", "@", "|", "\t", "\r"):
        s = "'" + s
    return s


def model_to_csv_rows(items: list, fields: list[str]) -> list[list[str]]:
    rows = []
    for item in items:
        row = []
        for field in fields:
            raw = getattr(item, field, "")
            if isinstance(raw, list):
                raw = ";".join(str(x) for x in raw)
            row.append(sanitize_csv(raw))
        rows.append(row)
    return rows


def csv_response(rows: list[list[str]], headers: list[str], filename: str):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def parse_upload(file: UploadFile) -> list[dict[str, str]]:
    if file.content_type not in ("text/csv", "application/octet-stream", None):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {file.content_type}. Only CSV files are accepted.",
        )

    contents = file.file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File exceeds 10 MB limit.",
        )

    decoded = contents.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    decoded = contents.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)

    if len(rows) > MAX_ROWS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"File exceeds {MAX_ROWS} row limit.",
        )

    file.file.close()
    return rows


FIELD_TYPE_MAP: dict[str, type] = {
    "crown_jewel": bool,
    "internet_exposed": bool,
    "kev_signal": bool,
    "ransomware_observed": bool,
    "risk_acceptance_required": bool,
    "due_in_days": int,
    "identity_risk": int,
    "control_gap": int,
    "cvss": float,
    "epss_probability": float,
}

LIST_FIELDS: set[str] = {"tags", "crown_jewel_asset_ids"}


def coerce_value(value: str, field_type: type) -> Any:
    if field_type is bool:
        return value.strip().lower() in ("true", "1", "yes")
    if field_type is int:
        return int(value.strip()) if value.strip() else 0
    if field_type is float:
        return float(value.strip()) if value.strip() else 0.0
    return value.strip()
