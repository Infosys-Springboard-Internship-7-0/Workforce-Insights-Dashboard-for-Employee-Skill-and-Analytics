"""FastAPI application entrypoint for the AI Workforce Assistant Platform."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_routes import router as admin_router
from app.api.auth_routes import router as auth_router
from app.api.chat_routes import router as chat_router
from app.api.dataviewer_routes import router as dataviewer_router
from app.api.document_routes import router as document_router
from app.api.health_routes import router as health_router
from app.api.powerbi_routes import router as powerbi_router
from app.api.team_routes import router as team_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.seed import seed_initial_admin

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info(f"Starting {settings.app_name}")
    seed_initial_admin()
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI Workforce Assistant Platform — RAG chatbot (ChromaDB + Groq), "
    "admin-managed documents/team/PowerBI dashboards, and a CSV data viewer.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(team_router)
app.include_router(powerbi_router)
app.include_router(document_router)
app.include_router(chat_router)
app.include_router(dataviewer_router)
