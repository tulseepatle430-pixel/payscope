"""Ingestion: read raw job postings and profile them."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "job_id", "job_title", "company", "location", "experience_years",
    "education", "skills_text", "salary_text", "employment_type",
    "industry", "job_description",
]


def load_from_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"No raw dataset found at {path}. Run scripts/generate_sample_jobs.py "
            "or place a sourced CSV there matching REQUIRED_COLUMNS."
        )
    df = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Raw dataset is missing required columns: {sorted(missing)}")
    return df


def profile(df: pd.DataFrame) -> dict:
    return {
        "n_records": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_job_ids": int(df["job_id"].duplicated().sum()),
    }
