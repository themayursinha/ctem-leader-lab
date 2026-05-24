import csv
import hmac
import io
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

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
    AuditEvent,
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
OPTIONAL_CSV_FIELDS = {"cvss", "source", "source_reference", "first_seen", "last_seen", "validated_at", "evidence_owner", "evidence_expires_at"}

logger = logging.getLogger("ctem")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("CTEM_ADMIN_TOKEN"):
        logger.warning("CTEM_ADMIN_TOKEN is unset; mutating APIs are running in unsafe local demo mode.")
    yield


app = FastAPI(title="CTEM Leader Lab API", lifespan=lifespan)


def require_admin_token(x_ctem_admin_token: str | None = Header(default=None)):
    expected = os.environ.get("CTEM_ADMIN_TOKEN")
    if not expected:
        return
    if not x_ctem_admin_token or not hmac.compare_digest(x_ctem_admin_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid admin token.")

_default_origins = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175"
_cors_origins = os.environ.get("CORS_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in _cors_origins if origin.strip()],
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
    "source", "source_reference", "first_seen", "last_seen", "validated_at",
    "evidence_owner", "evidence_expires_at",
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
            if raw == "" and field in OPTIONAL_CSV_FIELDS:
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


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


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


@app.post("/api/assets/import", dependencies=[Depends(require_admin_token)])
async def import_assets_csv(file: UploadFile = File(...)):
    rows = _parse_upload(file)
    valid, errors = _validate_rows(rows, Asset, ASSET_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    DATA.replace_assets(valid)
    DATA.record_audit_event(
        "import_assets", "assets", None, f"Imported {len(valid)} asset rows.", {"row_count": len(valid)}
    )
    return {"imported": len(valid), "errors": []}


@app.post("/api/exposures/import", dependencies=[Depends(require_admin_token)])
async def import_exposures_csv(file: UploadFile = File(...)):
    rows = _parse_upload(file)
    valid, errors = _validate_rows(rows, Exposure, EXPOSURE_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    DATA.replace_exposures(valid)
    DATA.record_audit_event(
        "import_exposures", "exposures", None, f"Imported {len(valid)} exposure rows.", {"row_count": len(valid)}
    )
    return {"imported": len(valid), "errors": []}


@app.post("/api/remediation-actions/import", dependencies=[Depends(require_admin_token)])
async def import_remediation_csv(file: UploadFile = File(...)):
    rows = _parse_upload(file)
    valid, errors = _validate_rows(rows, RemediationAction, REMEDIATION_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    DATA.replace_remediation_actions(valid)
    DATA.record_audit_event(
        "import_remediation_actions", "remediation_actions", None, f"Imported {len(valid)} remediation action rows.", {"row_count": len(valid)}
    )
    return {"imported": len(valid), "errors": []}


# ---------- Reset endpoint ----------


@app.post("/api/reset", dependencies=[Depends(require_admin_token)])
def reset_data(confirm: bool = Query(False, alias="X-Confirm-Reset")):
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset requires X-Confirm-Reset=true query parameter.",
        )
    DATA.reset()
    DATA.record_audit_event("reset_data", "workspace", None, "Reset workspace to seed data.", {})
    return {"status": "reset to seed data"}


# ---------- Session endpoints ----------


@app.post("/api/sessions", dependencies=[Depends(require_admin_token)])
def create_session(name: str = Query(..., min_length=1, max_length=200)):
    clean_name = name.strip()
    session_id = DATA.save_session(name=clean_name)
    DATA.record_audit_event(
        "save_session", "session", session_id, f'Saved session "{clean_name}".', {"name": clean_name}
    )
    return {"id": session_id, "name": clean_name}


@app.get("/api/sessions")
def list_sessions():
    return DATA.list_sessions()


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    info = DATA.get_session_info(session_id)
    if info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {
        "id": info["id"],
        "name": info["name"],
        "created_at": info["created_at"],
        "updated_at": info["updated_at"],
    }


@app.post("/api/sessions/{session_id}/load", dependencies=[Depends(require_admin_token)])
def load_session(session_id: str):
    ok = DATA.load_session(session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    DATA.record_audit_event("load_session", "session", session_id, f"Loaded session {session_id}.", {})
    return {"status": f"Session {session_id} loaded"}


@app.delete("/api/sessions/{session_id}", dependencies=[Depends(require_admin_token)])
def delete_session(session_id: str):
    ok = DATA.delete_session(session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    DATA.record_audit_event("delete_session", "session", session_id, f"Deleted session {session_id}.", {})
    return {"status": f"Session {session_id} deleted"}


# ---------- Audit endpoint ----------


@app.get("/api/audit-events", response_model=list[AuditEvent])
def list_audit_events(limit: int = Query(100, ge=1, le=500)):
    return DATA.list_audit_events(limit=limit)


# ---------- Executive summary endpoint ----------


@app.get("/api/executive-summary")
def executive_summary(format: str = Query("markdown", pattern="^(markdown|html)$")):
    prioritized = prioritized_exposures()
    act_items = [p for p in prioritized if p.decision == "Act"]
    attend_items = [p for p in prioritized if p.decision == "Attend"]
    scoped_services = [s for s in BUSINESS_SERVICES if s.in_scope]
    validated_paths = [p for p in ATTACK_PATHS if p.status == "Validated"]

    summary = _build_summary_text(
        organization="Northstar Financial Services",
        scoped_count=len(scoped_services),
        crown_jewel_count=len([a for a in ASSETS if a.crown_jewel]),
        exposure_count=len(EXPOSURES),
        act_count=len(act_items),
        attend_count=len(attend_items),
        validated_path_count=len(validated_paths),
        maturity_current=round(sum(d.score for d in MATURITY) / len(MATURITY), 1),
        maturity_target=round(sum(d.target for d in MATURITY) / len(MATURITY), 1),
        act_items=[(p.title, p.ctem_score, p.next_action) for p in act_items],
        attend_items=[(p.title, p.ctem_score, p.next_action) for p in attend_items],
    )

    if format == "html":
        html = summary.replace("\n", "<br>\n").replace("## ", "<h2>").replace("### ", "<h3>")
        html = f"<html><body style='font-family:system-ui,sans-serif;max-width:800px;margin:40px auto'>{html}</body></html>"
        return HTMLResponse(content=html)

    return StreamingResponse(
        iter([summary]),
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="ctem-executive-summary.md"'},
    )


def _build_summary_text(
    organization: str,
    scoped_count: int,
    crown_jewel_count: int,
    exposure_count: int,
    act_count: int,
    attend_count: int,
    validated_path_count: int,
    maturity_current: float,
    maturity_target: float,
    act_items: list[tuple[str, int, str]],
    attend_items: list[tuple[str, int, str]],
) -> str:
    lines = [
        f"# CTEM Executive Summary — {organization}",
        "",
        f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Program Overview",
        "",
        f"| Metric | Value |",
        "| --- | --- |",
        f"| Scoped services | {scoped_count} |",
        f"| Crown-jewel assets | {crown_jewel_count} |",
        f"| Total exposures | {exposure_count} |",
        f"| Act decisions | {act_count} |",
        f"| Attend decisions | {attend_count} |",
        f"| Validated attack paths | {validated_path_count} |",
        f"| Maturity (current/target) | {maturity_current}/{maturity_target} |",
        "",
        "## Act Decisions — Immediate Mobilization",
        "",
    ]
    if act_items:
        for title, score, action in act_items:
            lines.append(f"- **{title}** (CTEM {score}): {action}")
    else:
        lines.append("*No Act decisions in the current view.*")
    lines.append("")

    if attend_items:
        lines.append("## Attend Decisions — Leadership Coordination")
        lines.append("")
        for title, score, action in attend_items:
            lines.append(f"- **{title}** (CTEM {score}): {action}")
        lines.append("")

    lines.extend([
        "## Exposure Reduction Goal",
        "",
        "35% validated critical-path reduction in 90 days.",
        "",
        "---",
        "",
        "*Generated by CTEM Leader Lab*",
        "",
    ])
    return "\n".join(lines)
