from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.auth import decode_access_token
from app.db.database import get_db
from app.db.models import OrganizationModel, UserModel
from app.services.data_service import DataService


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> UserModel | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    return user


def require_current_user(user: UserModel | None = Depends(get_current_user)) -> UserModel:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def get_current_organization_id(
    user: UserModel | None = Depends(get_current_user),
) -> str | None:
    if user is not None:
        return user.organization_id
    return None


def get_data_service(
    db: Session = Depends(get_db),
    org_id: str | None = Depends(get_current_organization_id),
) -> DataService:
    return DataService(db, org_id=org_id)
