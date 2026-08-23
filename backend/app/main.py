from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import enable_pgvector
from app.routers import auth, assistant, documents, team, powerbi, recommendations, datasets, analytics
from app.models import User, Document, DocumentChunk, TeamMember, PowerBIDashboard, Recommendation, ChatSession, ChatMessage, Dataset, DatasetRow

settings = get_settings()

app = FastAPI(
    title="AI-Powered Workforce Analytics & Talent Intelligence Dashboard API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    enable_pgvector()


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-workforce-assistant"}


app.include_router(auth.router)
app.include_router(assistant.router)
app.include_router(documents.router)
app.include_router(team.router)
app.include_router(powerbi.router)
app.include_router(recommendations.router)
app.include_router(datasets.router)
app.include_router(analytics.router)
