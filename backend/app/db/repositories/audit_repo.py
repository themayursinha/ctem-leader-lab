import json

from sqlalchemy.orm import Session

from app.db.models import AuditEventModel
from app.db.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditEventModel]):
    def __init__(self, db: Session):
        super().__init__(db, AuditEventModel)

    def list_recent(self, limit: int = 100) -> list[dict]:
        rows = self._db.query(AuditEventModel).order_by(
            AuditEventModel.created_at.desc(), AuditEventModel.id.desc()
        ).limit(limit).all()
        events = []
        for row in rows:
            event = {
                "id": row.id,
                "created_at": row.created_at,
                "action": row.action,
                "resource_type": row.resource_type,
                "resource_id": row.resource_id,
                "summary": row.summary,
                "metadata": row.details if isinstance(row.details, dict) else json.loads(row.details),
            }
            events.append(event)
        return events
