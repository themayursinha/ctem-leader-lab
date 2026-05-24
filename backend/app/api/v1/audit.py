from fastapi import APIRouter, Depends, Query

from app.dependencies import get_data_service
from app.models.domain import AuditEvent
from app.services.data_service import DataService

router = APIRouter(tags=["Audit"])


@router.get("/api/audit-events", response_model=list[AuditEvent])
def list_audit_events(limit: int = Query(100, ge=1, le=500),
                      data: DataService = Depends(get_data_service)):
    return data.list_audit_events(limit=limit)
