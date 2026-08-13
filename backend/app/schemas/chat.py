"""RAG chatbot request/response schemas."""

from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    mode: str = Field(default="assistant", description="'assistant' (general Q&A) or 'admin_decision' (recommendation-focused)")


class SourceChunk(BaseModel):
    document: str
    category: str | None = None
    chunk_preview: str


class ChatQueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = Field(default_factory=list)
    grounded: bool


class SuggestedQuestionsResponse(BaseModel):
    questions: list[str]
