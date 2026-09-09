"""Load cleaned jobs (+ many-to-many skills) into Postgres."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from .connection import get_engine

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "sql" / "schema.sql"

JOB_COLUMNS = [
    "job_id", "job_title", "company", "location", "experience_years", "education",
    "employment_type", "industry", "salary_min", "salary_max", "salary_midpoint", "currency",
]


def apply_schema() -> None:
    engine = get_engine()
    sql = SCHEMA_PATH.read_text()
    with engine.begin() as conn:
        for statement in filter(None, (s.strip() for s in sql.split(";"))):
            conn.exec_driver_sql(statement)


def load_jobs(df: pd.DataFrame) -> None:
    engine = get_engine()
    df[JOB_COLUMNS].to_sql("jobs", engine, if_exists="replace", index=False, chunksize=2000)

    unique_skills = sorted({skill for skills in df["skills"] for skill in skills})
    skills_df = pd.DataFrame({"skill_name": unique_skills})
    skills_df.to_sql("skills", engine, if_exists="replace", index=False, chunksize=2000)

    with engine.connect() as conn:
        skill_id_map = dict(conn.execute(text("SELECT skill_name, skill_id FROM skills")).fetchall())

    rows = [
        {"job_id": job_id, "skill_id": skill_id_map[skill]}
        for job_id, skills in zip(df["job_id"], df["skills"])
        for skill in skills
    ]
    job_skills_df = pd.DataFrame(rows)
    job_skills_df.to_sql("job_skills", engine, if_exists="replace", index=False, chunksize=5000)
