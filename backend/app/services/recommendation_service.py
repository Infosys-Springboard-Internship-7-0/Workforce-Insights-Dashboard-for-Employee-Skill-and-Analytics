from __future__ import annotations

import json
import re
from typing import Any

import numpy as np
import pandas as pd
from groq import Groq
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.dataset import Dataset, DatasetRow
from app.models.recommendation import Recommendation

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)


def available_datasets(db: Session) -> list[dict[str, Any]]:
    datasets = db.scalars(
        select(Dataset).order_by(Dataset.updated_at.desc())
    ).all()

    return [
        {
            "name": dataset.name,
            "rows": int(dataset.row_count or 0),
            "columns": len(dataset.columns or []),
            "column_names": dataset.columns or [],
        }
        for dataset in datasets
    ]


def _clean_scalar(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def analyze_dataframe(df: pd.DataFrame, filename: str) -> dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number])
    categorical = df.select_dtypes(exclude=[np.number])

    missing_by_column = df.isna().sum()
    missing = {
        str(k): int(v)
        for k, v in missing_by_column[missing_by_column > 0].items()
    }

    numeric_stats: dict[str, dict[str, Any]] = {}
    for column in numeric.columns:
        series = pd.to_numeric(numeric[column], errors="coerce").dropna()
        if series.empty:
            continue
        numeric_stats[str(column)] = {
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "std": round(float(series.std(ddof=0)), 4),
        }

    categorical_stats: dict[str, dict[str, Any]] = {}
    for column in categorical.columns:
        counts = df[column].fillna("<missing>").astype(str).value_counts().head(10)
        categorical_stats[str(column)] = {
            "unique_values": int(df[column].nunique(dropna=True)),
            "top_values": {str(k): int(v) for k, v in counts.items()},
        }

    outliers: dict[str, int] = {}
    for column in numeric.columns:
        series = pd.to_numeric(numeric[column], errors="coerce").dropna()
        if len(series) < 4:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        count = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        if count:
            outliers[str(column)] = count

    correlations: dict[str, float] = {}
    if len(numeric.columns) >= 2:
        corr = numeric.corr(numeric_only=True)
        for i, col_a in enumerate(corr.columns):
            for col_b in corr.columns[i + 1 :]:
                value = corr.loc[col_a, col_b]
                if pd.notna(value) and abs(float(value)) >= 0.5:
                    correlations[f"{col_a} vs {col_b}"] = round(float(value), 4)

    insights: list[str] = []
    if missing:
        insights.append(f"Missing values were found in {len(missing)} column(s), totaling {sum(missing.values())} cells.")
    if int(df.duplicated().sum()) > 0:
        insights.append(f"{int(df.duplicated().sum())} duplicate row(s) were detected.")
    if outliers:
        insights.append(
            "Potential outliers were detected in: "
            + ", ".join(f"{k} ({v})" for k, v in outliers.items())
            + "."
        )
    if correlations:
        insights.append(
            "Strong numeric relationships were detected: "
            + ", ".join(f"{k} ({v:+.2f})" for k, v in correlations.items())
            + "."
        )
    if categorical_stats:
        largest = max(
            categorical_stats.items(),
            key=lambda item: item[1]["unique_values"],
            default=None,
        )
        if largest:
            insights.append(
                f"Column '{largest[0]}' contains {largest[1]['unique_values']} distinct categorical value(s)."
            )
    if not insights:
        insights.append("No obvious data-quality issues or strong statistical signals were detected by the baseline analysis.")

    return {
        "dataset": filename,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "missing_values": int(df.isna().sum().sum()),
        "missing_by_column": missing,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_statistics": numeric_stats,
        "categorical_statistics": categorical_stats,
        "outliers": outliers,
        "strong_correlations": correlations,
        "insights": insights,
    }


def analyze_dataset(db: Session, dataset_name: str) -> dict[str, Any]:
    dataset = db.scalar(
        select(Dataset).where(Dataset.name == dataset_name)
    )

    if not dataset:
        raise ValueError("Dataset not found.")

    rows = db.scalars(
        select(DatasetRow)
        .where(DatasetRow.dataset_id == dataset.id)
        .order_by(DatasetRow.row_index)
    ).all()

    if rows:
        records = [row.data for row in rows]
        df = pd.DataFrame(records, columns=dataset.columns or None)
    else:
        df = pd.DataFrame(columns=dataset.columns or [])

    return analyze_dataframe(df, dataset.name)


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Groq did not return valid JSON.")
    return json.loads(cleaned[start : end + 1])


def generate_recommendations(analysis: dict[str, Any]) -> list[dict[str, str]]:
    prompt = f"""You are the AI Workforce Decision Assistant.

Use ONLY the verified Python analysis below. Never invent or recalculate facts.
Generate 3 to 5 practical recommendations for an administrator.
A recommendation must be actionable and tied to an observed fact or insight.
Do not make high-stakes HR, legal, financial, medical, or safety decisions automatically.
Use priority values: low, medium, high, critical.

Return ONLY valid JSON in this exact shape:
{{
  "recommendations": [
    {{
      "title": "short title",
      "recommendation": "specific action",
      "reasoning": "why this action is supported by the verified analysis",
      "priority": "medium",
      "expected_impact": "expected operational impact"
    }}
  ]
}}

Verified analysis:
{json.dumps(analysis, indent=2, default=_clean_scalar)}
"""

    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "You produce grounded enterprise decision-support recommendations from verified data analysis.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.15,
        max_tokens=1800,
        response_format={"type": "json_object"},
    )

    payload = _extract_json(completion.choices[0].message.content or "{}")
    raw_items = payload.get("recommendations", [])
    if not isinstance(raw_items, list):
        raise ValueError("Invalid recommendations payload.")

    valid: list[dict[str, str]] = []
    allowed_priorities = {"low", "medium", "high", "critical"}
    for item in raw_items[:5]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        recommendation = str(item.get("recommendation", "")).strip()
        reasoning = str(item.get("reasoning", "")).strip()
        priority = str(item.get("priority", "medium")).strip().lower()
        impact = str(item.get("expected_impact", "")).strip()
        if title and recommendation and reasoning:
            valid.append(
                {
                    "title": title,
                    "recommendation": recommendation,
                    "reasoning": reasoning,
                    "priority": priority if priority in allowed_priorities else "medium",
                    "expected_impact": impact,
                }
            )

    if not valid:
        raise ValueError("Groq returned no usable recommendations.")
    return valid


def fallback_recommendations(analysis: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if analysis["missing_values"]:
        items.append(
            {
                "title": "Review missing data",
                "recommendation": "Review and resolve missing values before relying on the dataset for operational decisions.",
                "reasoning": f"The analysis found {analysis['missing_values']} missing cell(s).",
                "priority": "high",
                "expected_impact": "Improve data quality and reporting reliability.",
            }
        )
    if analysis["duplicate_rows"]:
        items.append(
            {
                "title": "Clean duplicate records",
                "recommendation": "Review duplicate rows and remove confirmed duplicates from the source dataset.",
                "reasoning": f"The analysis detected {analysis['duplicate_rows']} duplicate row(s).",
                "priority": "medium",
                "expected_impact": "Reduce double counting and improve downstream analytics.",
            }
        )
    if analysis["outliers"]:
        items.append(
            {
                "title": "Review potential outliers",
                "recommendation": "Investigate flagged numeric outliers before using the affected metrics for decisions.",
                "reasoning": "The IQR-based baseline analysis identified potential outliers.",
                "priority": "medium",
                "expected_impact": "Reduce the risk of decisions being driven by anomalous records.",
            }
        )
    if not items:
        items.append(
            {
                "title": "Validate business context",
                "recommendation": "Review the dataset findings with the responsible business owner before taking action.",
                "reasoning": "The baseline analysis did not identify a clear data-quality issue requiring automatic action.",
                "priority": "low",
                "expected_impact": "Keep recommendations aligned with business context and ownership.",
            }
        )
    return items[:5]


def save_recommendations(db, analysis: dict[str, Any], items: list[dict[str, str]], user_id: str) -> list[Recommendation]:
    records: list[Recommendation] = []
    for item in items:
        record = Recommendation(
            title=item["title"],
            recommendation=item["recommendation"],
            reasoning=item["reasoning"],
            priority=item["priority"],
            status="new",
            expected_impact=item.get("expected_impact", ""),
            dataset_name=analysis["dataset"],
            analysis_summary=json.dumps(analysis, default=_clean_scalar),
            created_by=user_id,
        )
        db.add(record)
        records.append(record)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def serialize_recommendation(record: Recommendation) -> dict[str, Any]:
    return {
        "id": record.id,
        "title": record.title,
        "recommendation": record.recommendation,
        "reasoning": record.reasoning,
        "priority": record.priority,
        "status": record.status,
        "dismissed": record.dismissed,
        "dismissed_at": record.dismissed_at,
        "expected_impact": record.expected_impact,
        "dataset_name": record.dataset_name,
        "created_at": record.created_at,
    }
