"""Central configuration, loaded from environment variables / .env."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_JOBS_CSV = DATA_RAW_DIR / "job_postings.csv"
CLEAN_JOBS_PARQUET = DATA_PROCESSED_DIR / "jobs_clean.parquet"
FEATURES_NPZ = DATA_PROCESSED_DIR / "features.npz"

SKILLS_TAXONOMY_PATH = PROJECT_ROOT / "src" / "job_market" / "nlp" / "skills_taxonomy.json"

INR_PER_LAKH = 100_000
USD_TO_INR = 83.0  # fixed approximate rate used only to unify currencies for modeling

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_DB = os.getenv("POSTGRES_DB", "job_market")
POSTGRES_USER = os.getenv("POSTGRES_USER", "job_market")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")


def sqlalchemy_url() -> str:
    return (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
