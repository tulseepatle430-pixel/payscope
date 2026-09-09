"""Generate a synthetic job-postings dataset with realistic messy salary strings.

Salary is generated from an underlying formula (experience, role, location,
skills) plus noise, then rendered into one of several inconsistent real-world
text formats — this is what makes salary_parser.py and the cleaning step
worth having, rather than reading a single clean numeric column.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from config.settings import DATA_RAW_DIR, RAW_JOBS_CSV

ROLES = {
    "Data Analyst": {"base_lpa": 6, "skills": ["Python", "SQL", "Excel", "Power BI", "Statistics"]},
    "Data Scientist": {"base_lpa": 10, "skills": ["Python", "Machine Learning", "Statistics", "SQL", "NLP"]},
    "ML Engineer": {"base_lpa": 12, "skills": ["Python", "Machine Learning", "Deep Learning", "Docker", "AWS"]},
    "Data Engineer": {"base_lpa": 11, "skills": ["Python", "SQL", "Spark", "Airflow", "AWS", "ETL"]},
    "BI Analyst": {"base_lpa": 7, "skills": ["SQL", "Power BI", "Tableau", "Excel", "Data Visualization"]},
    "Software Engineer": {"base_lpa": 9, "skills": ["Java", "JavaScript", "Git", "Docker", "SQL"]},
}

LOCATIONS = {
    "Bangalore": 1.25, "Mumbai": 1.15, "Hyderabad": 1.05,
    "Delhi": 1.10, "Pune": 1.0, "Chennai": 0.95,
}

EDUCATION = ["Bachelor's", "Master's", "PhD"]
EDUCATION_PREMIUM = {"Bachelor's": 1.0, "Master's": 1.12, "PhD": 1.25}

EMPLOYMENT_TYPES = ["Full-Time", "Contract", "Part-Time"]
INDUSTRIES = ["Technology", "Finance", "Healthcare", "E-Commerce", "Consulting"]

EXTRA_SKILLS = ["AWS", "Azure", "GCP", "Git", "Linux", "Kubernetes", "MySQL", "PostgreSQL"]

SALARY_FORMATS = ["inr_range_symbol", "inr_lpa_single", "inr_lakh_range", "usd_single", "not_disclosed"]


def _format_salary(low_lpa: float, high_lpa: float, rng: np.random.Generator) -> str:
    fmt = rng.choice(SALARY_FORMATS, p=[0.30, 0.25, 0.20, 0.15, 0.10])
    if fmt == "inr_range_symbol":
        return f"₹{low_lpa:.0f}-{high_lpa:.0f} LPA"
    if fmt == "inr_lpa_single":
        return f"{(low_lpa + high_lpa) / 2:.0f} LPA"
    if fmt == "inr_lakh_range":
        return f"{low_lpa:.0f}-{high_lpa:.0f} Lakhs"
    if fmt == "usd_single":
        usd = (low_lpa + high_lpa) / 2 * 100_000 / 83.0
        return f"${usd:,.0f}"
    return "Not Disclosed"


def generate(n_jobs: int = 3000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    role_names = list(ROLES.keys())
    location_names = list(LOCATIONS.keys())

    rows = []
    for i in range(n_jobs):
        role = rng.choice(role_names)
        role_info = ROLES[role]
        location = rng.choice(location_names)
        education = rng.choice(EDUCATION, p=[0.6, 0.32, 0.08])
        experience = round(float(rng.gamma(shape=2.0, scale=2.0)), 1)
        experience = min(experience, 20.0)

        core_skills = rng.choice(role_info["skills"], size=rng.integers(2, len(role_info["skills"]) + 1), replace=False)
        extra = rng.choice(EXTRA_SKILLS, size=rng.integers(0, 3), replace=False)
        skills = list(core_skills) + list(extra)

        salary_mid = (
            role_info["base_lpa"]
            * LOCATIONS[location]
            * EDUCATION_PREMIUM[education]
            * (1 + 0.07 * experience)
            * (1 + 0.02 * len(skills))
        )
        noise = rng.normal(0, salary_mid * 0.08)
        salary_mid = max(3.0, salary_mid + noise)
        spread = salary_mid * rng.uniform(0.1, 0.25)
        low_lpa, high_lpa = salary_mid - spread, salary_mid + spread

        skills_text = ", ".join(skills)
        job_description = (
            f"Looking for a {role} with {experience:.0f}+ years of experience. "
            f"Required skills: {skills_text}. Based in {location}."
        )

        rows.append(
            {
                "job_id": f"J{i:05d}",
                "job_title": role,
                "company": f"Company {rng.integers(1, 400)}",
                "location": location,
                "experience_years": experience,
                "education": education,
                "skills_text": skills_text,
                "salary_text": _format_salary(low_lpa, high_lpa, rng),
                "employment_type": rng.choice(EMPLOYMENT_TYPES, p=[0.8, 0.15, 0.05]),
                "industry": rng.choice(INDUSTRIES),
                "job_description": job_description,
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(RAW_JOBS_CSV, index=False)
    print(f"Wrote {len(df):,} rows to {RAW_JOBS_CSV}")
