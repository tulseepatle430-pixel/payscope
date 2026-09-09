"""CLI entrypoint: apply schema and load the cleaned dataset into Postgres."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from config.settings import CLEAN_JOBS_PARQUET
from job_market.db.loader import apply_schema, load_jobs

if __name__ == "__main__":
    if not CLEAN_JOBS_PARQUET.exists():
        raise SystemExit("Run scripts/run_pipeline.py first to produce the cleaned dataset.")

    df = pd.read_parquet(CLEAN_JOBS_PARQUET)
    apply_schema()
    load_jobs(df)
    print(f"Loaded {len(df):,} jobs into Postgres.")
