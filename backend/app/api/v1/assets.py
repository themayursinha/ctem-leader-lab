from fastapi import APIRouter, Depends, File, UploadFile

from app.core.csv import FIELD_TYPE_MAP, LIST_FIELDS, OPTIONAL_CSV_FIELDS, coerce_value, csv_response, model_to_csv_rows, parse_upload
from app.core.security import require_admin_token
from app.dependencies import get_data_service
from app.models.domain import Asset
from app.services.data_service import DataService

router = APIRouter(tags=["Assets"])

ASSET_FIELDS = [
    "id", "name", "type", "service_id", "owner", "environment",
    "criticality", "crown_jewel", "internet_exposed",
    "reachable_from_internet", "tags",
]


@router.get("/api/assets", response_model=list[Asset])
def get_assets(data: DataService = Depends(get_data_service)):
    return data.get_assets()


@router.get("/api/assets/export")
def export_assets_csv(data: DataService = Depends(get_data_service)):
    assets = data.get_assets()
    rows = model_to_csv_rows(assets, ASSET_FIELDS)
    return csv_response(rows, ASSET_FIELDS, "assets.csv")


@router.post("/api/assets/import", dependencies=[Depends(require_admin_token)])
async def import_assets_csv(file: UploadFile = File(...), data: DataService = Depends(get_data_service)):
    rows = parse_upload(file)
    valid, errors = _validate_rows(rows, Asset, ASSET_FIELDS)
    if errors:
        return {"imported": 0, "errors": errors}
    data.replace_assets(valid)
    data.record_audit_event(
        "import_assets", "assets", None, f"Imported {len(valid)} asset rows.", {"row_count": len(valid)}
    )
    return {"imported": len(valid), "errors": []}


def _validate_rows(rows: list[dict], model_class: type, fields: list[str]) -> tuple[list, list[dict]]:
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
                coerced[field] = coerce_value(raw, ftype)
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
