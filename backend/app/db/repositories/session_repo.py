from sqlalchemy.orm import Session

from app.db.models import SessionModel
from app.db.repositories.base import BaseRepository


class SessionRepository(BaseRepository[SessionModel]):
    def __init__(self, db: Session):
        super().__init__(db, SessionModel)

    def list_all(self) -> list[dict]:
        rows = self._db.query(
            SessionModel.id,
            SessionModel.name,
            SessionModel.created_at,
            SessionModel.updated_at,
        ).order_by(SessionModel.updated_at.desc()).all()
        return [dict(r._mapping) for r in rows]

    def get_full(self, session_id: str) -> SessionModel | None:
        return self._db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def delete(self, session_id: str) -> bool:
        obj = self._db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if obj is None:
            return False
        self._db.delete(obj)
        self._db.commit()
        return True
