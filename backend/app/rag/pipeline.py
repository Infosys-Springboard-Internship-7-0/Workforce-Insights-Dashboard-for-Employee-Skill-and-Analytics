"""
RAG query pipeline, matching the specified architecture exactly:

  User Question -> React -> FastAPI -> Generate Embedding -> Search ChromaDB
  -> Top 5 Chunks -> Prompt -> Groq API -> Answer -> React

Two modes:
  - "assistant": general-purpose Q&A for any authenticated/public user of
    the AI Workforce Assistant chatbot page.
  - "admin_decision": same retrieval, but a recommendation-focused system
    prompt for the admin decision-support chatbot.
"""

from dataclasses import dataclass, field

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.llm_client import LLMNotConfiguredError, chat_completion
from app.rag.vector_store import get_vector_store

logger = get_logger(__name__)

NOT_ENOUGH_INFO_MESSAGE = (
    "I could not find sufficient information in the uploaded documents to answer this "
    "question reliably. Try rephrasing, or ask an admin to upload a relevant document."
)

RELEVANCE_THRESHOLD = 0.30

ASSISTANT_SYSTEM_PROMPT = """You are the AI Workforce Assistant for this workforce analytics platform.

Use only the provided context (retrieved from admin-uploaded documents) to answer the
question. Never fabricate policies, figures, or facts not present in the context.

If the answer cannot be found in the context, say so plainly instead of guessing.

Cite the source document name when relevant. Keep answers clear and concise, and
distinguish factual statements (from the context) from any interpretation you add."""

ADMIN_DECISION_SYSTEM_PROMPT = """You are a decision-support assistant for platform administrators.

Use only the provided context (retrieved from uploaded documents/data) to answer.
Where relevant, surface concrete, actionable recommendations grounded in the context,
clearly labeled as "Recommendation:" and stating they require human review before
being acted on. Never fabricate data. If the context doesn't support a confident
recommendation, say so."""


@dataclass
class RagAnswer:
    answer: str
    sources: list[dict] = field(default_factory=list)
    grounded: bool = True


def _build_prompt(question: str, chunks: list[dict]) -> str:
    context_blocks = []
    for c in chunks:
        doc = c["metadata"].get("document", "unknown")
        context_blocks.append(f"[{doc}]\n{c['text']}")
    context = "\n\n---\n\n".join(context_blocks)
    return f"Context:\n{context}\n\nQuestion: {question}"


def answer_question(question: str, mode: str = "assistant") -> RagAnswer:
    settings = get_settings()
    store = get_vector_store()

    chunks = store.query(question, top_k=settings.top_k_chunks)

    if not chunks or max((c["relevance"] for c in chunks), default=0.0) < RELEVANCE_THRESHOLD:
        logger.info("Low-confidence or empty retrieval; returning refusal.")
        return RagAnswer(answer=NOT_ENOUGH_INFO_MESSAGE, sources=[], grounded=False)

    system_prompt = ADMIN_DECISION_SYSTEM_PROMPT if mode == "admin_decision" else ASSISTANT_SYSTEM_PROMPT
    prompt = _build_prompt(question, chunks)

    try:
        answer_text = chat_completion(system_prompt, prompt, temperature=0.2)
    except LLMNotConfiguredError as exc:
        raise RuntimeError(str(exc)) from exc

    sources = [
        {
            "document": c["metadata"].get("document", ""),
            "category": c["metadata"].get("category"),
            "chunk_preview": c["text"][:200],
        }
        for c in chunks
    ]
    return RagAnswer(answer=answer_text, sources=sources, grounded=True)
