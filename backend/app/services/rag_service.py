import json
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.chat import ChatMessage, ChatSession
from app.models.document import Document, DocumentChunk
from app.rag.chunker import chunk_text
from app.rag.embeddings import embed_texts
from app.rag.loader import extract_document
from app.rag.retriever import search_chunks
from app.services.groq_service import generate_answer
from app.services.recommendation_service import analyze_dataset

settings = get_settings()


def ingest_document(
    db: Session,
    file_bytes: bytes,
    filename: str,
    document,
):
    pages = extract_document(file_bytes, filename)

    all_chunks = []
    for text, page_number in pages:
        for chunk in chunk_text(text):
            all_chunks.append((chunk, page_number))

    if not all_chunks:
        raise ValueError("No extractable text found in document")

    vectors = embed_texts([x[0] for x in all_chunks])

    for index, ((content, page_number), vector) in enumerate(zip(all_chunks, vectors)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
                page_number=page_number,
                embedding=vector,
            )
        )

    document.chunk_count = len(all_chunks)
    document.status = "indexed"
    db.commit()


def answer_question(
    db: Session,
    user_id: str,
    question: str,
    dataset_name: str | None = None,
    document_filename: str | None = None,
):
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.flush()

    chunks = search_chunks(db, question, settings.top_k, document_filename)

    context_parts = []
    sources = []

    for chunk in chunks:
        doc = db.get(Document, chunk.document_id)
        filename = doc.filename if doc else "unknown"
        context_parts.append(
            f"[Source: {filename}, page={chunk.page_number}, chunk={chunk.chunk_index}]\n"
            f"{chunk.content}"
        )
        sources.append({
            "filename": filename,
            "page": chunk.page_number,
            "chunk_index": chunk.chunk_index,
        })

    context = "\n\n---\n\n".join(context_parts)
    if dataset_name:
        try:
            analysis = analyze_dataset(db, dataset_name)
        except ValueError:
            analysis = None
        if analysis:
            context += "\n\n---\n\n[Selected dataset analysis]\n" + json.dumps(analysis, default=str)
    answer = generate_answer(question, context or "No relevant project documents were found.")

    db.add(ChatMessage(
        session_id=session.id,
        role="user",
        content=question,
        sources="[]",
    ))
    db.add(ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
        sources=json.dumps(sources),
    ))
    db.commit()

    return answer, session.id, sources
