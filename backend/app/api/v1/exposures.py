from fastapi import APIRouter, Depends, File, UploadFile

from app.core.csv import csv_response, model_to_csv_rows, parse_upload
from app.core.security import require_admin_token
from app.dependencies import get_data_service
from app.models.domain import Exposure, PrioritizedExposure
from app.services.data_service import DataService
from app.api.v1.assets import _validate_rows

router = APIRouter(tags=["Exposures"])

EXPOSURE_FIELDS = [
    "id", "title", "description", "exposure_type", "asset_id", "severity",
    "cvss", "epss_probability", "kev_signal", "ransomware_observed",
    "identity_risk", "control_gap", "attack_path_proximity",
    "remediation_effort", "evidence_confidence", "evidence", "suggested_action",
    "source", "source_reference", "first_seen", "last_seen", "validated_at",
    "evidence_owner", "evidence_expires_at",
]


@router.get("/api/exposures", response_model=list[Exposure])
def get_exposures(data: DataService = Depends(get_data_service)):
    return data.get_exposures()


@router.get("/api/prioritized-exposures", response_model=list[PrioritizedExposure])
def get_prioritized_exposures(data: DataService = Depends(get_data_service)):
    return data.get_prioritized_exposures()


@router.get("/api/prioritization", response_model=list[PrioritizedExposure])
def get_legacy_prioritization_alias(data: DataService = Depends(get_data_service)):
    return data.get_prioritized_exposures()


@router.get("/api/exposures/export")
def export_exposures_csv(data: DataService = Depends(get_data_service)):
    exposures = data.get_exposures()
    rows = model_to_csv_rows(exposures, EXPOSURE_FIELDS)
    return csv_response(rows, EXPOSURE_FIELDS, "exposures.csv")


@router.post("/api/exposures/import", dependencies=[Depends(require_admin_token)])
async def import_exposures_csv(file: UploadFile = File(...), data: DataService = Depends(get_data_service)):
    rows = parse_upload(file)
    valid, errors = _validate_rows(rows, Exposure, EXPOSURE_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    data.replace_exposures(valid)
    data.record_audit_event(
        "import_exposures", "exposures", None, f"Imported {len(valid)} exposure rows.", {"row_count": len(valid)}
    )
    return {"imported": len(valid), "errors": []}
