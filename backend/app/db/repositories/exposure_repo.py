from sqlalchemy.orm import Session

from app.db.models import ExposureModel
from app.db.repositories.base import BaseRepository


class ExposureRepository(BaseRepository[ExposureModel]):
    def __init__(self, db: Session):
        super().__init__(db, ExposureModel)
