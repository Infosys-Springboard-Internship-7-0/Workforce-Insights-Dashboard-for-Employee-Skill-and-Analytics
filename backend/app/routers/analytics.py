from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Get comprehensive dashboard statistics"""
    return AnalyticsService.get_dashboard_stats(db)


@router.get("/documents")
def get_documents_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Get document processing overview"""
    return AnalyticsService.get_documents_overview(db)


@router.get("/recommendations")
def get_recommendations_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Get recommendations overview"""
    return AnalyticsService.get_recommendations_overview(db)
