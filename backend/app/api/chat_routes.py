"""
Chatbot routes.

- POST /api/chat/query is public (the AI Workforce Assistant page is meant
  for general users, not just admins) and always runs in "assistant" mode.
- POST /api/chat/admin-query is admin-only and defaults to "admin_decision"
  mode for recommendation-focused answers.
- GET  /api/chat/suggested-questions returns a curated starter-question list
  for the chat UI (different sets for the public assistant vs. the admin
  analytics/decision page).
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import get_logger
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.rag.pipeline import answer_question
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, SourceChunk, SuggestedQuestionsResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = get_logger(__name__)

ASSISTANT_SUGGESTED_QUESTIONS = [
    "What is the company's promotion policy?",
    "What leave and benefits are employees entitled to?",
    "What learning and development programs are available?",
    "What are the requirements for a Data Scientist role?",
    "Summarize the key points of our privacy policy.",
]

ADMIN_SUGGESTED_QUESTIONS = [
    "Which departments show the highest attrition risk based on uploaded data?",
    "What retention programs should we prioritize this quarter?",
    "Summarize key risks found across the uploaded reports.",
    "What policy gaps exist compared to industry best practice documents?",
    "What should leadership focus on based on the latest workforce data?",
]


def _run_query(request: ChatQueryRequest) -> ChatQueryResponse:
    try:
        result = answer_question(request.question, mode=request.mode)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Chat query failed: {exc}")
        raise HTTPException(status_code=500, detail="Chat query failed. Check server logs.") from exc

    sources = [SourceChunk(**s) for s in result.sources]
    return ChatQueryResponse(answer=result.answer, sources=sources, grounded=result.grounded)


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest) -> ChatQueryResponse:
    """Public AI Workforce Assistant endpoint — always runs in general 'assistant' mode."""
    request.mode = "assistant"
    return _run_query(request)


@router.post("/admin-query", response_model=ChatQueryResponse)
async def admin_chat_query(request: ChatQueryRequest, current_admin: Admin = Depends(get_current_admin)) -> ChatQueryResponse:
    """Admin decision-support endpoint — defaults to recommendation-focused 'admin_decision' mode."""
    if request.mode not in {"assistant", "admin_decision"}:
        request.mode = "admin_decision"
    return _run_query(request)


@router.get("/suggested-questions", response_model=SuggestedQuestionsResponse)
async def suggested_questions(audience: str = "assistant") -> SuggestedQuestionsResponse:
    questions = ADMIN_SUGGESTED_QUESTIONS if audience == "admin" else ASSISTANT_SUGGESTED_QUESTIONS
    return SuggestedQuestionsResponse(questions=questions)


RECOMMENDATIONS_QUERY = (
    "Based on all available uploaded documents and data, identify the top workforce risks, "
    "policy gaps, and opportunities. Provide 3-5 concrete, prioritized recommendations for "
    "leadership, each clearly labeled as a recommendation requiring human review."
)


@router.get("/recommendations", response_model=ChatQueryResponse)
async def get_recommendations(current_admin: Admin = Depends(get_current_admin)) -> ChatQueryResponse:
    """
    Admin-only: 'See recommendation to admin (after analyze data)'. Runs a
    fixed, broad analytical question through the same RAG pipeline in
    admin_decision mode, so recommendations are always grounded in whatever
    documents/data have actually been uploaded — never fabricated.
    """
    return _run_query(ChatQueryRequest(question=RECOMMENDATIONS_QUERY, mode="admin_decision"))
