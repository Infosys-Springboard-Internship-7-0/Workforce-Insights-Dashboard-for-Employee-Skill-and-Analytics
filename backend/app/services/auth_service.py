from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import get_settings
from app.core.security import verify_password, hash_password

settings = get_settings()


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return {"user_id": user_id}
        except JWTError:
            return None

    @staticmethod
    def get_current_user(db: Session, token: str):
        """Get current user from token"""
        token_data = AuthService.verify_token(token)
        if token_data is None:
            return None
        
        user_id = token_data.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        return user

    @staticmethod
    def is_admin(user: User):
        """Check if user is admin"""
        return user and user.role == "admin" and user.is_active

    @staticmethod
    def change_password(db: Session, user_id: str, old_password: str, new_password: str):
        """Change user password"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if not verify_password(old_password, user.password_hash):
            return False
        
        user.password_hash = hash_password(new_password)
        db.commit()
        return True

    @staticmethod
    def reset_password(db: Session, user_id: str, new_password: str):
        """Reset user password (admin only)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.password_hash = hash_password(new_password)
        db.commit()
        return True

    @staticmethod
    def check_admin_access(user: User, resource_admin_id: str = None):
        """Check if user has admin access to a resource"""
        if not AuthService.is_admin(user):
            return False
        
        # If resource_admin_id is specified, check if it matches the current user
        if resource_admin_id and resource_admin_id != user.id:
            return False
        
        return True
