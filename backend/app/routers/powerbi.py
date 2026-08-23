from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.powerbi import PowerBIDashboard
from app.models.user import User
from app.schemas.powerbi import PowerBIUpdate

router = APIRouter(tags=["powerbi"])


@router.get("/api/powerbi")
def public_powerbi(db: Session = Depends(get_db)):
    return db.execute(
        select(PowerBIDashboard).where(PowerBIDashboard.is_active.is_(True))
    ).scalars().all()


@router.get("/api/admin/powerbi")
def admin_powerbi(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.execute(select(PowerBIDashboard)).scalars().all()


@router.post("/api/admin/powerbi")
def create_powerbi(
    payload: PowerBIUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = PowerBIDashboard(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/api/admin/powerbi/{dashboard_id}")
def update_powerbi(
    dashboard_id: str,
    payload: PowerBIUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = db.get(PowerBIDashboard, dashboard_id)
    if not item:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    for key, value in payload.model_dump().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item
