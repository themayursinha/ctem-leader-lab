import csv
import io
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from data import (
    ASSETS,
    ATTACK_PATHS,
    BUSINESS_SERVICES,
    DATA,
    EXPOSURES,
    MATURITY,
    REMEDIATION_ACTIONS,
    WORKSHOP_ARTIFACTS,
)
from models import (
    Asset,
    AttackPath,
    BusinessService,
    Exposure,
    MaturityDomain,
    PrioritizedExposure,
    ProgramSummary,
    RemediationAction,
    WorkshopArtifacts,
)
from scoring import prioritized_exposures


MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_ROWS = 10_000


app = FastAPI(title="CTEM Leader Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _sanitize_csv(value: Any) -> str:
    s = str(value) if value is not None else ""
    if s and s[0] in ("=", "+", "-", "@", "|", "\t", "\r"):
        s = "'" + s
    return s


def _model_to_csv_rows(items: list, fields: list[str]) -> list[list[str]]:
    rows = []
    for item in items:
        row = []
        for field in fields:
            raw = getattr(item, field, "")
            if isinstance(raw, list):
                raw = ";".join(str(x) for x in raw)
            row.append(_sanitize_csv(raw))
        rows.append(row)
    return rows


ASSET_FIELDS = [
    "id", "name", "type", "service_id", "owner", "environment",
    "criticality", "crown_jewel", "internet_exposed",
    "reachable_from_internet", "tags",
]

EXPOSURE_FIELDS = [
    "id", "title", "description", "exposure_type", "asset_id", "severity",
    "cvss", "epss_probability", "kev_signal", "ransomware_observed",
    "identity_risk", "control_gap", "attack_path_proximity",
    "remediation_effort", "evidence_confidence", "evidence", "suggested_action",
]

REMEDIATION_FIELDS = [
    "id", "exposure_id", "title", "owner", "team", "status", "priority",
    "sla", "due_in_days", "playbook", "dependency", "retest_status",
    "risk_acceptance_required",
]


def _csv_response(rows: list[list[str]], headers: list[str], filename: str):
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


def _parse_upload(file: UploadFile) -> list[dict[str, str]]:
    if file.content_type not in ("text/csv", "application/octet-stream", None):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {file.content_type}. Only CSV files are accepted.",
        )

    contents = file.file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 10 MB limit.",
        )

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


def _coerce_value(value: str, field_type: type) -> Any:
    if field_type is bool:
        return value.strip().lower() in ("true", "1", "yes")
    if field_type is int:
        return int(value.strip()) if value.strip() else 0
    if field_type is float:
        return float(value.strip()) if value.strip() else 0.0
    return value.strip()


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


def _validate_rows(
    rows: list[dict[str, str]], model_class: type, fields: list[str],
) -> tuple[list, list[dict]]:
    valid = []
    errors = []
    for i, row in enumerate(rows):
        field_errors = []
        coerced = {}
        for field in fields:
            raw = row.get(field, "").strip()
            if raw == "" and field in ("cvss", "epss_probability"):
                coerced[field] = None
                continue
            if raw == "":
                field_errors.append({"row": i + 2, "field": field, "message": f"{field} is required"})
                continue
            if field in LIST_FIELDS:
                coerced[field] = [x.strip() for x in raw.split(";") if x.strip()]
                continue
            ftype = FIELD_TYPE_MAP.get(field, str)
            try:
                coerced[field] = _coerce_value(raw, ftype)
            except (ValueError, TypeError):
                field_errors.append({"row": i + 2, "field": field, "message": f"Invalid value for {field}: {raw!r}"})
                continue
        if field_errors:
            errors.extend(field_errors)
            continue
        try:
            valid.append(model_class(**coerced))
        except Exception as exc:
            errors.append({"row": i + 2, "field": "_model", "message": str(exc)})
    return valid, errors


# ---------- Existing read-only endpoints ----------


@app.get("/api/program-summary", response_model=ProgramSummary)
def get_program_summary():
    prioritized = prioritized_exposures()
    act_count = len([item for item in prioritized if item.decision == "Act"])
    attend_count = len([item for item in prioritized if item.decision == "Attend"])
    scoped_services = [service for service in BUSINESS_SERVICES if service.in_scope]
    validated_paths = [path for path in ATTACK_PATHS if path.status == "Validated"]

    return ProgramSummary(
        organization="Northstar Financial Services",
        goal="Move from vulnerability backlog management to validated exposure reduction for crown-jewel services.",
        maturity_current=round(sum(domain.score for domain in MATURITY) / len(MATURITY), 1),
        maturity_target=round(sum(domain.target for domain in MATURITY) / len(MATURITY), 1),
        metrics={
            "scoped_services": len(scoped_services),
            "crown_jewel_assets": len([asset for asset in ASSETS if asset.crown_jewel]),
            "raw_exposures": len(EXPOSURES),
            "act_decisions": act_count,
            "attend_decisions": attend_count,
            "validated_attack_paths": len(validated_paths),
            "sla_at_risk": 2,
            "exposure_reduction_goal": "35% validated critical-path reduction in 90 days",
        },
        operating_principles=[
            "Scope starts with business services and crown jewels, not scanner coverage.",
            "Prioritization explains why an exposure matters and what evidence supports action.",
            "Validation proves exploitability, reachability, control performance, and blast radius safely.",
            "Mobilization assigns accountable owners, SLAs, retest criteria, and exception paths.",
        ],
        cycle=[
            {"stage": "Scoping", "leader_question": "Which business services deserve scarce remediation capacity first?"},
            {"stage": "Discovery", "leader_question": "What exposures exist across technology, identity, cloud, SaaS, and controls?"},
            {"stage": "Prioritization", "leader_question": "Which exposures create the most credible path to business harm?"},
            {"stage": "Validation", "leader_question": "What evidence proves the exposure is exploitable or blocked?"},
            {"stage": "Mobilization", "leader_question": "Who will fix, accept, retest, or escalate the risk?"},
        ],
    )


@app.get("/api/maturity", response_model=list[MaturityDomain])
def get_maturity():
    return MATURITY


@app.get("/api/business-services", response_model=list[BusinessService])
def get_business_services():
    return BUSINESS_SERVICES


@app.get("/api/assets", response_model=list[Asset])
def get_assets():
    return ASSETS


@app.get("/api/exposures", response_model=list[Exposure])
def get_exposures():
    return EXPOSURES


@app.get("/api/prioritized-exposures", response_model=list[PrioritizedExposure])
def get_prioritized_exposures():
    return prioritized_exposures()


@app.get("/api/prioritization", response_model=list[PrioritizedExposure])
def get_legacy_prioritization_alias():
    return prioritized_exposures()


@app.get("/api/attack-paths", response_model=list[AttackPath])
def get_attack_paths():
    return ATTACK_PATHS


@app.get("/api/remediation-actions", response_model=list[RemediationAction])
def get_remediation_actions():
    return REMEDIATION_ACTIONS


@app.get("/api/workshop-artifacts", response_model=WorkshopArtifacts)
def get_workshop_artifacts():
    return WORKSHOP_ARTIFACTS


# ---------- CSV export endpoints ----------


@app.get("/api/assets/export")
def export_assets_csv():
    rows = _model_to_csv_rows(ASSETS, ASSET_FIELDS)
    return _csv_response(rows, ASSET_FIELDS, "assets.csv")


@app.get("/api/exposures/export")
def export_exposures_csv():
    rows = _model_to_csv_rows(EXPOSURES, EXPOSURE_FIELDS)
    return _csv_response(rows, EXPOSURE_FIELDS, "exposures.csv")


@app.get("/api/remediation-actions/export")
def export_remediation_csv():
    rows = _model_to_csv_rows(REMEDIATION_ACTIONS, REMEDIATION_FIELDS)
    return _csv_response(rows, REMEDIATION_FIELDS, "remediation-actions.csv")


# ---------- CSV import endpoints ----------


@app.post("/api/assets/import")
async def import_assets_csv(file: UploadFile = File(...)):
    rows = _parse_upload(file)
    valid, errors = _validate_rows(rows, Asset, ASSET_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    DATA.replace_assets(valid)
    return {"imported": len(valid), "errors": []}


@app.post("/api/exposures/import")
async def import_exposures_csv(file: UploadFile = File(...)):
    rows = _parse_upload(file)
    valid, errors = _validate_rows(rows, Exposure, EXPOSURE_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    DATA.replace_exposures(valid)
    return {"imported": len(valid), "errors": []}


@app.post("/api/remediation-actions/import")
async def import_remediation_csv(file: UploadFile = File(...)):
    rows = _parse_upload(file)
    valid, errors = _validate_rows(rows, RemediationAction, REMEDIATION_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    DATA.replace_remediation_actions(valid)
    return {"imported": len(valid), "errors": []}


# ---------- Reset endpoint ----------


@app.post("/api/reset")
def reset_data(confirm: bool = Query(False, alias="X-Confirm-Reset")):
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset requires X-Confirm-Reset=true query parameter.",
        )
    DATA.reset()
    return {"status": "reset to seed data"}
