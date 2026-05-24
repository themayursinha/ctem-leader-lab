from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import require_admin_token
from app.dependencies import get_data_service
from app.services.data_service import DataService

router = APIRouter(tags=["Admin"])


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.post("/api/reset", dependencies=[Depends(require_admin_token)])
def reset_data(confirm: bool = Query(False, alias="X-Confirm-Reset"),
               data: DataService = Depends(get_data_service)):
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset requires X-Confirm-Reset=true query parameter.",
        )
    data.reset()
    data.record_audit_event("reset_data", "workspace", None, "Reset workspace to seed data.", {})
    return {"status": "reset to seed data"}
