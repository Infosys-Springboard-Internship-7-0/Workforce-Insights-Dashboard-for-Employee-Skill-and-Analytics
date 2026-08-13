"""Auth routes: admin login and profile self-service. Only admins can authenticate."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_admin, hash_password, verify_password
from app.models.admin import Admin
from app.schemas.admin import AdminOut, ProfileUpdateRequest
from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    admin = db.execute(select(Admin).where(Admin.email == request.email)).scalar_one_or_none()
    if admin is None or not verify_password(request.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This admin account has been disabled.")

    token = create_access_token(admin.id, admin.email)
    return LoginResponse(access_token=token, admin=AdminOut.model_validate(admin))


@router.get("/me", response_model=AdminOut)
async def get_me(current_admin: Admin = Depends(get_current_admin)) -> AdminOut:
    return AdminOut.model_validate(current_admin)


@router.put("/me", response_model=AdminOut)
async def update_profile(
    request: ProfileUpdateRequest, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> AdminOut:
    if request.email and request.email != current_admin.email:
        existing = db.execute(select(Admin).where(Admin.email == request.email)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="That email is already in use.")
        current_admin.email = request.email
    if request.name:
        current_admin.name = request.name
    db.commit()
    db.refresh(current_admin)
    return AdminOut.model_validate(current_admin)


@router.post("/me/change-password")
async def change_password(
    request: ChangePasswordRequest, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> dict:
    if not verify_password(request.current_password, current_admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect.")
    current_admin.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"detail": "Password updated successfully."}
