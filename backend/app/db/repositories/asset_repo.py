from sqlalchemy.orm import Session

from app.db.models import AssetModel
from app.db.repositories.base import BaseRepository


class AssetRepository(BaseRepository[AssetModel]):
    def __init__(self, db: Session):
        super().__init__(db, AssetModel)
