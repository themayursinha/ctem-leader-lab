from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.auth import decode_access_token
from app.db.database import get_db
from app.db.models import UserModel
from app.services.data_service import DataService


def get_data_service(db: Session = Depends(get_db)) -> DataService:
    return DataService(db)


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> UserModel:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
