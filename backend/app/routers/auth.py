from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_current_user, require_admin, hash_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut, CreateAdmin
from app.services.auth_service import AuthService
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/auth", tags=["auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    new_password: str


class UpdateAdminRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    
    token = AuthService.create_access_token({"sub": user.id})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not AuthService.change_password(db, user.id, payload.old_password, payload.new_password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    return {"message": "Password changed successfully"}


@router.post("/admins", response_model=UserOut)
def create_admin(
    payload: CreateAdmin,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    admin = AdminService.create_admin(db, payload.name, payload.email, payload.password)
    if not admin:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    return admin


@router.get("/admins", response_model=list[UserOut])
def list_admins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return AdminService.get_all_admins(db, skip, limit)


@router.get("/admins/{admin_id}", response_model=UserOut)
def get_admin(
    admin_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    admin = AdminService.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@router.put("/admins/{admin_id}", response_model=UserOut)
def update_admin(
    admin_id: str,
    payload: UpdateAdminRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
):
    admin = AdminService.update_admin(
        db,
        admin_id,
        payload.name,
        payload.email,
        payload.is_active,
    )
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@router.post("/admins/{admin_id}/reset-password")
def reset_admin_password(
    admin_id: str,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
):
    success = AuthService.reset_password(db, admin_id, payload.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {"message": "Password reset successfully"}


@router.delete("/admins/{admin_id}")
def delete_admin(
    admin_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
):
    if current.id == admin_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account",
        )

    success = AdminService.delete_admin(db, admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"message": "Admin deleted successfully", "id": admin_id}
