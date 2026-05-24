from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.data_service import DataService


def get_data_service(db: Session = Depends(get_db)) -> DataService:
    return DataService(db)
