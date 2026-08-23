from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.team import TeamMember
from app.models.user import User
from app.schemas.team import TeamCreate
from app.services.team_service import TeamService

router = APIRouter(tags=["team"])


@router.get("/api/team")
def public_team(db: Session = Depends(get_db)):
    """Get all team members (public endpoint)"""
    return TeamService.get_all_team_members(db)


@router.get("/api/admin/team")
def admin_list_team(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Get all team members (admin endpoint)"""
    return TeamService.get_all_team_members(db, skip, limit)


@router.get("/api/admin/team/{member_id}")
def admin_get_team_member(
    member_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Get a specific team member"""
    member = TeamService.get_team_member_by_id(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    return member


@router.post("/api/admin/team")
def create_team_member(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Create a new team member"""
    member = TeamService.create_team_member(
        db,
        name=payload.name,
        role=payload.role,
        contribution=payload.contribution,
        skills=payload.skills,
        linkedin=payload.linkedin,
        github=payload.github,
    )
    return member


@router.put("/api/admin/team/{member_id}")
def update_team_member(
    member_id: str,
    payload: TeamCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Update a team member"""
    member = TeamService.update_team_member(
        db,
        member_id,
        name=payload.name,
        role=payload.role,
        contribution=payload.contribution,
        skills=payload.skills,
        linkedin=payload.linkedin,
        github=payload.github,
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    return member


@router.delete("/api/admin/team/{member_id}")
def delete_team_member(
    member_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a team member"""
    success = TeamService.delete_team_member(db, member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team member not found")
    return {"message": "Team member deleted", "id": member_id}


@router.delete("/api/admin/team/{member_id}")
def delete_team_member(
    member_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    member = db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    db.delete(member)
    db.commit()
    return {"message": "Team member deleted"}
