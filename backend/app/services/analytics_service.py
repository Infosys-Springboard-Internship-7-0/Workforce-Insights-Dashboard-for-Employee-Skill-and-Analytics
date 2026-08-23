from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.document import Document
from app.models.dataset import Dataset
from app.models.user import User
from app.models.recommendation import Recommendation
from app.models.team import TeamMember
from app.models.chat import ChatSession, ChatMessage


class AnalyticsService:
    """Service for analytics and dashboard statistics"""

    @staticmethod
    def get_dashboard_stats(db: Session):
        """Get comprehensive dashboard statistics"""
        return {
            "documents": {
                "total": AnalyticsService.count_documents(db),
                "processing": AnalyticsService.count_documents_by_status(db, "processing"),
                "indexed": AnalyticsService.count_documents_by_status(db, "indexed"),
                "failed": AnalyticsService.count_documents_by_status(db, "failed"),
                "total_chunks": AnalyticsService.count_total_chunks(db),
            },
            "datasets": {
                "total": AnalyticsService.count_datasets(db),
                "total_rows": AnalyticsService.count_total_dataset_rows(db),
            },
            "admins": {
                "total": AnalyticsService.count_admins(db),
            },
            "team": {
                "members": AnalyticsService.count_team_members(db),
            },
            "recommendations": {
                "total": AnalyticsService.count_recommendations(db),
                "new": AnalyticsService.count_recommendations_by_status(db, "new"),
                "in_progress": AnalyticsService.count_recommendations_by_status(db, "in_progress"),
                "completed": AnalyticsService.count_recommendations_by_status(db, "completed"),
                "dismissed": AnalyticsService.count_dismissed_recommendations(db),
            },
            "chat": {
                "total_sessions": AnalyticsService.count_chat_sessions(db),
                "total_messages": AnalyticsService.count_chat_messages(db),
            },
        }

    @staticmethod
    def count_documents(db: Session):
        """Count total documents"""
        return db.query(func.count(Document.id)).scalar() or 0

    @staticmethod
    def count_documents_by_status(db: Session, status: str):
        """Count documents by status"""
        return db.query(func.count(Document.id)).filter(Document.status == status).scalar() or 0

    @staticmethod
    def count_total_chunks(db: Session):
        """Count indexed chunks across all documents"""
        return db.query(func.coalesce(func.sum(Document.chunk_count), 0)).scalar() or 0

    @staticmethod
    def count_datasets(db: Session):
        """Count total datasets"""
        return db.query(func.count(Dataset.id)).scalar() or 0

    @staticmethod
    def count_total_dataset_rows(db: Session):
        """Count total rows across all datasets"""
        return db.query(func.sum(Dataset.row_count)).scalar() or 0

    @staticmethod
    def count_admins(db: Session):
        """Count total admins"""
        return db.query(func.count(User.id)).filter(User.role == "admin").scalar() or 0

    @staticmethod
    def count_team_members(db: Session):
        """Count team members"""
        return db.query(func.count(TeamMember.id)).scalar() or 0

    @staticmethod
    def count_recommendations(db: Session):
        """Count total recommendations"""
        return db.query(func.count(Recommendation.id)).scalar() or 0

    @staticmethod
    def count_recommendations_by_status(db: Session, status: str):
        """Count recommendations by status"""
        return db.query(func.count(Recommendation.id)).filter(Recommendation.status == status).scalar() or 0

    @staticmethod
    def count_dismissed_recommendations(db: Session):
        """Count dismissed recommendations"""
        return db.query(func.count(Recommendation.id)).filter(Recommendation.dismissed == True).scalar() or 0

    @staticmethod
    def count_chat_sessions(db: Session):
        """Count chat sessions"""
        return db.query(func.count(ChatSession.id)).scalar() or 0

    @staticmethod
    def count_chat_messages(db: Session):
        """Count total chat messages"""
        return db.query(func.count(ChatMessage.id)).scalar() or 0

    @staticmethod
    def get_documents_overview(db: Session):
        """Get overview of document processing"""
        documents = db.query(Document).all()
        return {
            "total": len(documents),
            "by_status": {
                "processing": sum(1 for d in documents if d.status == "processing"),
                "indexed": sum(1 for d in documents if d.status == "indexed"),
                "failed": sum(1 for d in documents if d.status == "failed"),
            },
            "total_chunks": sum(d.chunk_count for d in documents),
            "recent_uploads": [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "status": d.status,
                    "created_at": d.created_at.isoformat()
                }
                for d in sorted(documents, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }

    @staticmethod
    def get_recommendations_overview(db: Session):
        """Get overview of recommendations"""
        recommendations = db.query(Recommendation).all()
        return {
            "total": len(recommendations),
            "by_status": {
                "new": sum(1 for r in recommendations if r.status == "new"),
                "in_progress": sum(1 for r in recommendations if r.status == "in_progress"),
                "completed": sum(1 for r in recommendations if r.status == "completed"),
                "dismissed": sum(1 for r in recommendations if r.dismissed),
            },
            "by_priority": {
                "low": sum(1 for r in recommendations if r.priority == "low"),
                "medium": sum(1 for r in recommendations if r.priority == "medium"),
                "high": sum(1 for r in recommendations if r.priority == "high"),
            },
            "recent": [
                {
                    "id": r.id,
                    "title": r.title,
                    "priority": r.priority,
                    "status": r.status,
                    "created_at": r.created_at.isoformat()
                }
                for r in sorted(recommendations, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }
