from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from app.core.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.core.security import require_admin_token
from app.db.models import OrganizationModel, UserModel
from app.dependencies import get_current_user, get_data_service, get_db
from app.services.data_service import DataService
from sqlalchemy.orm import Session

router = APIRouter(tags=["Auth"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    organization: str = "Default"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    organization_id: str
    role: str


@router.post("/api/auth/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == body.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    org = db.query(OrganizationModel).filter(OrganizationModel.name == body.organization).first()
    if not org:
        org = OrganizationModel(name=body.organization)
        db.add(org)
        db.flush()

    user = UserModel(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
        organization_id=org.id,
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, organization_id=org.id)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "email": user.email, "name": user.name, "organization_id": org.id, "role": user.role},
    )


@router.post("/api/auth/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=user.id, organization_id=user.organization_id)
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id, "email": user.email, "name": user.name,
            "organization_id": user.organization_id, "role": user.role,
        },
    )


@router.get("/api/auth/me", response_model=UserResponse)
def me(user: UserModel = Depends(get_current_user)):
    return UserResponse(
        id=user.id, email=user.email, name=user.name,
        organization_id=user.organization_id, role=user.role,
    )
