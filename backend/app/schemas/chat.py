from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None
    dataset_name: str | None = None
    document_filename: str | None = None


class Source(BaseModel):
    filename: str
    page: int | None = None
    chunk_index: int


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[Source]
