"""CLI entrypoint: python scripts/run_pipeline.py"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from job_market.pipeline import run_pipeline

if __name__ == "__main__":
    clean_df, training = run_pipeline()
    print(f"\nPipeline complete: {len(clean_df):,} cleaned rows")
    for name, info in training["results"].items():
        print(f"{name:20s} {info['metrics']}")
