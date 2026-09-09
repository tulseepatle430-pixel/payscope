"""Market-level exploratory analysis: skill demand, salary by role/experience/location."""
from __future__ import annotations

import pandas as pd


def skill_demand(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.explode("skills")["skills"].value_counts()
    return counts.rename_axis("skill").reset_index(name="job_count")


def salary_by_role(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("job_title")["salary_midpoint"]
        .agg(median_salary="median", avg_salary="mean", n_jobs="count")
        .sort_values("median_salary", ascending=False)
        .reset_index()
    )


def salary_by_location(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("location")["salary_midpoint"]
        .agg(median_salary="median", n_jobs="count")
        .sort_values("median_salary", ascending=False)
        .reset_index()
    )


def salary_by_experience_bucket(df: pd.DataFrame) -> pd.DataFrame:
    bins = [-0.01, 1, 2, 5, 8, 100]
    labels = ["0-1", "1-2", "2-5", "5-8", "8+"]
    df = df.copy()
    df["experience_bucket"] = pd.cut(df["experience_years"], bins=bins, labels=labels)
    return (
        df.groupby("experience_bucket", observed=True)["salary_midpoint"]
        .agg(median_salary="median", n_jobs="count")
        .reset_index()
    )
