"""Team member routes. Listing is public (shown on the landing page); mutations are admin-only."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.team_member import TeamMember
from app.schemas.team import TeamMemberCreate, TeamMemberOut, TeamMemberUpdate

router = APIRouter(prefix="/api/team", tags=["team"])


@router.get("", response_model=list[TeamMemberOut])
async def list_team_members(db: Session = Depends(get_db)) -> list[TeamMemberOut]:
    members = db.execute(select(TeamMember).order_by(TeamMember.display_order, TeamMember.id)).scalars().all()
    return [TeamMemberOut.model_validate(m) for m in members]


@router.post("", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    request: TeamMemberCreate, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> TeamMemberOut:
    member = TeamMember(**request.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return TeamMemberOut.model_validate(member)


@router.put("/{member_id}", response_model=TeamMemberOut)
async def update_team_member(
    member_id: int,
    request: TeamMemberUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> TeamMemberOut:
    member = db.get(TeamMember, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found.")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return TeamMemberOut.model_validate(member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    member_id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
) -> None:
    member = db.get(TeamMember, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found.")
    db.delete(member)
    db.commit()
