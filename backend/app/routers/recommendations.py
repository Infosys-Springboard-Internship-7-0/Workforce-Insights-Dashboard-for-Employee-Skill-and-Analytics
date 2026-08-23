import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.groq_service import generate_answer
from app.services.recommendation_service import (
    analyze_dataset,
    available_datasets,
    fallback_recommendations,
    generate_recommendations,
    save_recommendations,
    serialize_recommendation,
)

router = APIRouter(prefix="/api/admin/recommendations", tags=["recommendations"])


class AnalyzeRequest(BaseModel):
    dataset_name: str = Field(min_length=1, max_length=255)


class UpdateRecommendationRequest(BaseModel):
    status: str = Field(pattern="^(new|in_progress|approved|completed|dismissed|in_review)$")


class AskRecommendationRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class DecisionAssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    dataset_name: str = Field(min_length=1, max_length=255)


@router.get("/datasets")
def datasets(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return available_datasets(db)


@router.post("/decision-assistant")
def decision_assistant(
    payload: DecisionAssistantRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        analysis = analyze_dataset(db, payload.dataset_name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    prompt_context = (
        f"Selected dataset: {payload.dataset_name}\n"
        "Verified Python analysis of the selected dataset:\n"
        f"{json.dumps(analysis, indent=2, default=str)}"
    )
    try:
        answer = generate_answer(payload.question, prompt_context)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Decision assistant unavailable: {exc}")
    return {
        "question": payload.question,
        "dataset": payload.dataset_name,
        "answer": answer,
        "analysis": analysis,
    }


@router.post("/analyze")
def analyze(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    try:
        analysis = analyze_dataset(db, payload.dataset_name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        items = generate_recommendations(analysis)
        ai_generated = True
    except Exception as exc:
        # The data analysis remains useful even if the LLM is temporarily unavailable.
        items = fallback_recommendations(analysis)
        ai_generated = False
        llm_error = str(exc)
    else:
        llm_error = None

    records = save_recommendations(db, analysis, items, user.id)

    response: dict[str, Any] = {
        "message": "Dataset analyzed and recommendations generated.",
        "dataset": analysis,
        "ai_generated": ai_generated,
        "recommendations": [serialize_recommendation(x) for x in records],
    }
    if llm_error:
        response["llm_warning"] = f"Groq was unavailable, so baseline data-quality recommendations were used: {llm_error}"
    return response


@router.get("")
def recommendations(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    records = db.execute(
        select(Recommendation).order_by(Recommendation.created_at.desc())
    ).scalars().all()
    return [serialize_recommendation(x) for x in records]


@router.get("/{recommendation_id}")
def get_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    record = db.get(Recommendation, recommendation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return serialize_recommendation(record)


@router.patch("/{recommendation_id}")
def update_recommendation(
    recommendation_id: str,
    payload: UpdateRecommendationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    record = db.get(Recommendation, recommendation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if payload.status == "dismissed":
        from datetime import datetime, timezone
        record.dismissed = True
        record.dismissed_at = datetime.now(timezone.utc)

    record.status = payload.status
    db.commit()
    db.refresh(record)
    return serialize_recommendation(record)


@router.delete("/{recommendation_id}")
def delete_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    record = db.get(Recommendation, recommendation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    db.delete(record)
    db.commit()
    return {"message": "Recommendation deleted", "id": recommendation_id}


@router.post("/{recommendation_id}/ask")
def ask_about_recommendation(
    recommendation_id: str,
    payload: AskRecommendationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    record = db.get(Recommendation, recommendation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    try:
        analysis = json.loads(record.analysis_summary or "{}")
    except json.JSONDecodeError:
        analysis = {}

    context = f"""
Recommendation:
Title: {record.title}
Action: {record.recommendation}
Reasoning: {record.reasoning}
Priority: {record.priority}
Expected impact: {record.expected_impact}
Dataset: {record.dataset_name}

Verified dataset analysis:
{json.dumps(analysis, indent=2, default=str)}
"""

    answer = generate_answer(payload.question, context)
    return {"question": payload.question, "answer": answer}
