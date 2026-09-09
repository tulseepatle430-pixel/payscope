"""FastAPI backend for Job Market Intelligence & Salary Prediction.

Serves market analytics under /api/* and a POST /api/predict endpoint backed
by the from-scratch models trained by scripts/run_pipeline.py. When the
frontend has been built (frontend/dist) it's served as static files at "/".
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.settings import CLEAN_JOBS_PARQUET, MODELS_DIR
from job_market.analysis.market_eda import (
    salary_by_experience_bucket,
    salary_by_location,
    salary_by_role,
    skill_demand,
)
from job_market.llm.groq_client import generate_career_insight, is_available as llm_is_available
from job_market.nlp.skill_extractor import all_skills

app = FastAPI(title="Job Market Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_df: pd.DataFrame | None = None
_models = None


def get_df() -> pd.DataFrame:
    global _df
    if _df is None:
        if not CLEAN_JOBS_PARQUET.exists():
            raise HTTPException(
                status_code=503,
                detail=f"No processed dataset at {CLEAN_JOBS_PARQUET}. "
                "Run `python scripts/run_pipeline.py` first.",
            )
        _df = pd.read_parquet(CLEAN_JOBS_PARQUET)
    return _df


def get_models():
    global _models
    if _models is None:
        try:
            with open(MODELS_DIR / "feature_builder.pkl", "rb") as f:
                builder = pickle.load(f)
            with open(MODELS_DIR / "scaler.pkl", "rb") as f:
                scaler = pickle.load(f)
            with open(MODELS_DIR / "training_results.pkl", "rb") as f:
                results = pickle.load(f)
            best_name = (MODELS_DIR / "best_model_name.txt").read_text().strip()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="No trained models found. Run `python scripts/run_pipeline.py` first.",
            )
        _models = {"builder": builder, "scaler": scaler, "results": results, "best_name": best_name}
    return _models


def _clean_records(df: pd.DataFrame) -> list[dict]:
    records = df.to_dict(orient="records")
    for record in records:
        for key, value in record.items():
            if isinstance(value, float) and pd.isna(value):
                record[key] = None
    return records


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/overview")
def overview():
    df = get_df()
    return {
        "total_jobs": int(len(df)),
        "median_salary": float(df["salary_midpoint"].median()),
        "top_location": df["location"].mode()[0],
        "top_role": df["job_title"].mode()[0],
        "salary_histogram": df["salary_midpoint"].tolist(),
    }


@app.get("/api/skill-demand")
def skill_demand_endpoint():
    df = get_df()
    return _clean_records(skill_demand(df))


@app.get("/api/salary/by-role")
def by_role():
    return _clean_records(salary_by_role(get_df()))


@app.get("/api/salary/by-location")
def by_location():
    return _clean_records(salary_by_location(get_df()))


@app.get("/api/salary/by-experience")
def by_experience():
    df = salary_by_experience_bucket(get_df())
    df["experience_bucket"] = df["experience_bucket"].astype(str)
    return _clean_records(df)


@app.get("/api/options")
def options():
    df = get_df()
    return {
        "job_titles": sorted(df["job_title"].unique().tolist()),
        "locations": sorted(df["location"].unique().tolist()),
        "education": sorted(df["education"].unique().tolist()),
        "employment_types": sorted(df["employment_type"].unique().tolist()),
        "industries": sorted(df["industry"].unique().tolist()),
        "skills": all_skills(),
    }


@app.get("/api/model-comparison")
def model_comparison():
    models = get_models()
    return {
        "best_model": models["best_name"],
        "comparison": {name: info["metrics"] for name, info in models["results"].items()},
    }


class PredictRequest(BaseModel):
    job_title: str
    location: str
    education: str
    experience_years: float
    employment_type: str
    industry: str
    skills: list[str] = []


@app.post("/api/predict")
def predict(req: PredictRequest):
    models = get_models()
    builder = models["builder"]
    scaler = models["scaler"]
    best_name = models["best_name"]
    model_info = models["results"][best_name]

    X = builder.transform_single(
        req.experience_years, req.job_title, req.location, req.education,
        req.employment_type, req.industry, req.skills,
    )
    X_input = scaler.transform(X) if model_info["uses_scaled_features"] else X
    prediction = float(model_info["model"].predict(X_input)[0])

    insight = None
    if llm_is_available():
        top_skills = skill_demand(get_df())["skill"].head(10).tolist()
        insight = generate_career_insight(
            req.job_title, req.location, req.experience_years, req.education,
            req.skills, prediction, top_skills,
        )

    return {
        "model_used": best_name,
        "predicted_salary": prediction,
        "range_low": prediction * 0.9,
        "range_high": prediction * 1.1,
        "llm_available": llm_is_available(),
        "llm_insight": insight,
    }


FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
