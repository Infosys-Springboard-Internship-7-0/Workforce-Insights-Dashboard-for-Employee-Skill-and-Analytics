from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.team import TeamMember


class TeamService:
    """Service for team member management"""

    @staticmethod
    def get_all_team_members(db: Session, skip: int = 0, limit: int = 100):
        """Get all team members"""
        return db.query(TeamMember).offset(skip).limit(limit).all()

    @staticmethod
    def get_team_member_by_id(db: Session, member_id: str):
        """Get team member by ID"""
        return db.query(TeamMember).filter(TeamMember.id == member_id).first()

    @staticmethod
    def create_team_member(
        db: Session,
        name: str,
        role: str,
        contribution: str,
        skills: str = "",
        linkedin: str = "",
        github: str = ""
    ):
        """Create a new team member"""
        member = TeamMember(
            name=name,
            role=role,
            contribution=contribution,
            skills=skills,
            linkedin=linkedin,
            github=github
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def update_team_member(
        db: Session,
        member_id: str,
        name: str = None,
        role: str = None,
        contribution: str = None,
        skills: str = None,
        linkedin: str = None,
        github: str = None
    ):
        """Update team member details"""
        member = TeamService.get_team_member_by_id(db, member_id)
        if not member:
            return None
        
        if name is not None:
            member.name = name
        if role is not None:
            member.role = role
        if contribution is not None:
            member.contribution = contribution
        if skills is not None:
            member.skills = skills
        if linkedin is not None:
            member.linkedin = linkedin
        if github is not None:
            member.github = github
        
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def delete_team_member(db: Session, member_id: str):
        """Delete a team member"""
        member = TeamService.get_team_member_by_id(db, member_id)
        if not member:
            return False
        
        db.delete(member)
        db.commit()
        return True

    @staticmethod
    def count_team_members(db: Session):
        """Count total team members"""
        return db.query(func.count(TeamMember.id)).scalar()
