"""Power BI embed link routes. Listing active links is public; mutations are admin-only."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.powerbi_link import PowerBILink
from app.schemas.powerbi import PowerBILinkCreate, PowerBILinkOut, PowerBILinkUpdate

router = APIRouter(prefix="/api/powerbi", tags=["powerbi"])


@router.get("", response_model=list[PowerBILinkOut])
async def list_powerbi_links(active_only: bool = True, db: Session = Depends(get_db)) -> list[PowerBILinkOut]:
    query = select(PowerBILink).order_by(PowerBILink.display_order, PowerBILink.id)
    if active_only:
        query = query.where(PowerBILink.is_active.is_(True))
    links = db.execute(query).scalars().all()
    return [PowerBILinkOut.model_validate(link) for link in links]


@router.post("", response_model=PowerBILinkOut, status_code=status.HTTP_201_CREATED)
async def create_powerbi_link(
    request: PowerBILinkCreate, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> PowerBILinkOut:
    link = PowerBILink(**request.model_dump())
    db.add(link)
    db.commit()
    db.refresh(link)
    return PowerBILinkOut.model_validate(link)


@router.put("/{link_id}", response_model=PowerBILinkOut)
async def update_powerbi_link(
    link_id: int,
    request: PowerBILinkUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> PowerBILinkOut:
    link = db.get(PowerBILink, link_id)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Power BI link not found.")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(link, field, value)
    db.commit()
    db.refresh(link)
    return PowerBILinkOut.model_validate(link)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_powerbi_link(
    link_id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> None:
    link = db.get(PowerBILink, link_id)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Power BI link not found.")
    db.delete(link)
    db.commit()
