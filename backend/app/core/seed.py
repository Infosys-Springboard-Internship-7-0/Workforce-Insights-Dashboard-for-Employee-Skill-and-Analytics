"""First-run seeding: creates tables and the initial super-admin account if none exists."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.admin import Admin
from app.models.document import Document  # noqa: F401 - ensures table is registered
from app.models.powerbi_link import PowerBILink  # noqa: F401
from app.models.team_member import TeamMember  # noqa: F401

logger = get_logger(__name__)


def seed_initial_admin() -> None:
    Base.metadata.create_all(bind=engine)

    settings = get_settings()
    db: Session = SessionLocal()
    try:
        existing = db.execute(select(Admin)).first()
        if existing:
            return

        admin = Admin(
            name=settings.initial_admin_name,
            email=settings.initial_admin_email,
            hashed_password=hash_password(settings.initial_admin_password),
            is_super_admin=True,
        )
        db.add(admin)
        db.commit()
        logger.info(f"Seeded initial super-admin account: {settings.initial_admin_email}")
    finally:
        db.close()
