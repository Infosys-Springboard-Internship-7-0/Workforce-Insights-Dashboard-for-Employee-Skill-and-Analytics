"""
Admin management routes: add/update/delete admin accounts.

Only super admins can add or remove other admins (an admin cannot demote/
delete themselves, and the last remaining active admin cannot be deleted,
to avoid ever locking everyone out of the platform).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin, hash_password
from app.models.admin import Admin
from app.schemas.admin import AdminCreateRequest, AdminOut, AdminUpdateRequest

router = APIRouter(prefix="/api/admins", tags=["admin-management"])


def _require_super_admin(current_admin: Admin) -> None:
    if not current_admin.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can manage admin accounts.")


@router.get("", response_model=list[AdminOut])
async def list_admins(current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)) -> list[AdminOut]:
    admins = db.execute(select(Admin).order_by(Admin.id)).scalars().all()
    return [AdminOut.model_validate(a) for a in admins]


@router.post("", response_model=AdminOut, status_code=status.HTTP_201_CREATED)
async def create_admin(
    request: AdminCreateRequest, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> AdminOut:
    _require_super_admin(current_admin)

    existing = db.execute(select(Admin).where(Admin.email == request.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An admin with that email already exists.")

    new_admin = Admin(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password),
        is_super_admin=request.is_super_admin,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return AdminOut.model_validate(new_admin)


@router.put("/{admin_id}", response_model=AdminOut)
async def update_admin(
    admin_id: int,
    request: AdminUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminOut:
    _require_super_admin(current_admin)

    target = db.get(Admin, admin_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")

    if target.id == current_admin.id and request.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own account.")

    if request.name is not None:
        target.name = request.name
    if request.is_active is not None:
        target.is_active = request.is_active
    if request.is_super_admin is not None:
        target.is_super_admin = request.is_super_admin

    db.commit()
    db.refresh(target)
    return AdminOut.model_validate(target)


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(admin_id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)) -> None:
    _require_super_admin(current_admin)

    if admin_id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account.")

    target = db.get(Admin, admin_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")

    active_count = db.execute(select(Admin).where(Admin.is_active.is_(True))).scalars().all()
    if len(active_count) <= 1 and target.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the last active admin account.")

    db.delete(target)
    db.commit()
