"""Clean raw job postings: parse salary, normalize categoricals, extract skills."""
from __future__ import annotations

import pandas as pd

from ..nlp.skill_extractor import extract_skills
from .salary_parser import parse_salary


def clean_jobs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["job_title"] = df["job_title"].astype(str).str.strip()
    df["company"] = df["company"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip().str.title()
    df["education"] = df["education"].astype(str).str.strip().str.title()
    df["employment_type"] = df["employment_type"].astype(str).str.strip().str.title()
    df["industry"] = df["industry"].astype(str).str.strip().str.title()

    df["experience_years"] = pd.to_numeric(df["experience_years"], errors="coerce")

    parsed = df["salary_text"].apply(parse_salary)
    df["salary_min"] = [p.salary_min_inr for p in parsed]
    df["salary_max"] = [p.salary_max_inr for p in parsed]
    df["salary_midpoint"] = [p.salary_midpoint_inr for p in parsed]
    df["currency"] = [p.currency for p in parsed]

    df["skills"] = (df["skills_text"].fillna("") + " " + df["job_description"].fillna("")).apply(
        lambda text: sorted(extract_skills(text))
    )

    df = df.drop_duplicates(subset=["job_id"])
    df = df.dropna(subset=["job_title", "experience_years", "salary_midpoint"])
    df = df[df["salary_midpoint"] > 0]

    return df.reset_index(drop=True)


def validation_report(before: pd.DataFrame, after: pd.DataFrame) -> dict:
    return {
        "rows_before": len(before),
        "rows_after": len(after),
        "rows_dropped": len(before) - len(after),
        "pct_dropped": round(100 * (len(before) - len(after)) / max(len(before), 1), 2),
        "rows_missing_disclosed_salary": int(before["salary_text"].isna().sum()),
    }
