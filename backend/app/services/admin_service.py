from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.core.security import hash_password


class AdminService:
    """Service for admin management operations"""

    @staticmethod
    def get_all_admins(db: Session, skip: int = 0, limit: int = 100):
        """Get all admin users"""
        return db.query(User).filter(User.role == "admin").offset(skip).limit(limit).all()

    @staticmethod
    def get_admin_by_id(db: Session, admin_id: str):
        """Get admin by ID"""
        return db.query(User).filter(User.id == admin_id, User.role == "admin").first()

    @staticmethod
    def get_admin_by_email(db: Session, email: str):
        """Get admin by email"""
        return db.query(User).filter(User.email == email, User.role == "admin").first()

    @staticmethod
    def create_admin(db: Session, name: str, email: str, password: str):
        """Create a new admin user"""
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None
        
        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def update_admin(db: Session, admin_id: str, name: str = None, email: str = None, is_active: bool = None):
        """Update admin details"""
        admin = AdminService.get_admin_by_id(db, admin_id)
        if not admin:
            return None
        
        if name:
            admin.name = name
        if email:
            admin.email = email
        if is_active is not None:
            admin.is_active = is_active
        
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def delete_admin(db: Session, admin_id: str):
        """Delete an admin user"""
        admin = AdminService.get_admin_by_id(db, admin_id)
        if not admin:
            return False
        
        db.delete(admin)
        db.commit()
        return True

    @staticmethod
    def count_admins(db: Session):
        """Count total number of admins"""
        return db.query(func.count(User.id)).filter(User.role == "admin").scalar()
