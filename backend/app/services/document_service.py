from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.document import Document, DocumentChunk
import os


class DocumentService:
    """Service for document management operations"""

    @staticmethod
    def get_all_documents(db: Session, skip: int = 0, limit: int = 100):
        """Get all documents"""
        return db.query(Document).offset(skip).limit(limit).all()

    @staticmethod
    def get_document_by_id(db: Session, document_id: str):
        """Get document by ID"""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_documents_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
        """Get documents uploaded by a specific user"""
        return db.query(Document).filter(Document.uploaded_by == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_documents_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
        """Get documents by processing status"""
        return db.query(Document).filter(Document.status == status).offset(skip).limit(limit).all()

    @staticmethod
    def create_document(
        db: Session,
        filename: str,
        file_type: str,
        uploaded_by: str,
        description: str = "",
        file_path: str = ""
    ):
        """Create a new document record"""
        document = Document(
            filename=filename,
            description=description,
            file_type=file_type,
            uploaded_by=uploaded_by,
            status="processing",
            processing_status="Initializing...",
            file_path=file_path,
            chunk_count=0
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def update_document_status(
        db: Session,
        document_id: str,
        status: str,
        processing_status: str = "",
        chunk_count: int = None
    ):
        """Update document processing status"""
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return None
        
        document.status = status
        if processing_status:
            document.processing_status = processing_status
        if chunk_count is not None:
            document.chunk_count = chunk_count
        
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def update_document_metadata(
        db: Session,
        document_id: str,
        description: str = None,
        filename: str = None
    ):
        """Update document metadata"""
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return None
        
        if description is not None:
            document.description = description
        if filename is not None:
            document.filename = filename
        
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: str):
        """Delete a document and its chunks"""
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return False
        
        # Delete associated file if it exists
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except:
                pass
        
        db.delete(document)
        db.commit()
        return True

    @staticmethod
    def count_documents(db: Session):
        """Count total number of documents"""
        return db.query(func.count(Document.id)).scalar()

    @staticmethod
    def count_documents_by_status(db: Session, status: str):
        """Count documents by status"""
        return db.query(func.count(Document.id)).filter(Document.status == status).scalar()

    @staticmethod
    def add_chunk(
        db: Session,
        document_id: str,
        chunk_index: int,
        content: str,
        embedding,
        page_number: int = None
    ):
        """Add a chunk to a document"""
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
            page_number=page_number
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def delete_document_chunks(db: Session, document_id: str):
        """Delete all chunks for a document"""
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        db.commit()
