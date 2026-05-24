from fastapi import APIRouter, Depends, File, UploadFile

from app.core.csv import FIELD_TYPE_MAP, LIST_FIELDS, OPTIONAL_CSV_FIELDS, coerce_value, csv_response, model_to_csv_rows, parse_upload
from app.core.security import require_admin_token
from app.dependencies import get_data_service
from app.models.domain import RemediationAction
from app.services.data_service import DataService
from app.api.v1.assets import _validate_rows

router = APIRouter(tags=["Remediation"])

REMEDIATION_FIELDS = [
    "id", "exposure_id", "title", "owner", "team", "status", "priority",
    "sla", "due_in_days", "playbook", "dependency", "retest_status",
    "risk_acceptance_required",
]


@router.get("/api/remediation-actions", response_model=list[RemediationAction])
def get_remediation_actions(data: DataService = Depends(get_data_service)):
    return data.get_remediation_actions()


@router.get("/api/remediation-actions/export")
def export_remediation_csv(data: DataService = Depends(get_data_service)):
    actions = data.get_remediation_actions()
    rows = model_to_csv_rows(actions, REMEDIATION_FIELDS)
    return csv_response(rows, REMEDIATION_FIELDS, "remediation-actions.csv")


@router.post("/api/remediation-actions/import", dependencies=[Depends(require_admin_token)])
async def import_remediation_csv(file: UploadFile = File(...), data: DataService = Depends(get_data_service)):
    rows = parse_upload(file)
    valid, errors = _validate_rows(rows, RemediationAction, REMEDIATION_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    data.replace_remediation_actions(valid)
    data.record_audit_event(
        "import_remediation_actions", "remediation_actions", None,
        f"Imported {len(valid)} remediation action rows.", {"row_count": len(valid)}
    )
    return {"imported": len(valid), "errors": []}
