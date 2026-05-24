from sqlalchemy.orm import Session

from app.db.models import RemediationActionModel
from app.db.repositories.base import BaseRepository


class RemediationRepository(BaseRepository[RemediationActionModel]):
    def __init__(self, db: Session):
        super().__init__(db, RemediationActionModel)
