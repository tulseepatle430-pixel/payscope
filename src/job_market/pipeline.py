"""End-to-end pipeline: ingest -> clean -> feature engineer -> train models -> persist."""
from __future__ import annotations

import logging
import pickle

from config.settings import CLEAN_JOBS_PARQUET, DATA_PROCESSED_DIR, MODELS_DIR, RAW_JOBS_CSV
from .cleaning.clean import clean_jobs, validation_report
from .features.engineer import FeatureBuilder
from .ingestion.load_data import load_from_csv, profile
from .ml.train import best_model_name, train_and_compare

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(raw_path=RAW_JOBS_CSV):
    logger.info("Step 1: Ingesting raw job postings from %s", raw_path)
    raw_df = load_from_csv(raw_path)
    logger.info("Raw profile: %s", profile(raw_df))

    logger.info("Step 2: Cleaning (salary parsing, categorical normalization, skill extraction)")
    clean_df = clean_jobs(raw_df)
    logger.info("Validation report: %s", validation_report(raw_df, clean_df))

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_parquet(CLEAN_JOBS_PARQUET, index=False)
    logger.info("Wrote cleaned dataset to %s", CLEAN_JOBS_PARQUET)

    logger.info("Step 3: Feature engineering")
    builder = FeatureBuilder().fit(clean_df)
    X = builder.transform(clean_df)
    y = clean_df["salary_midpoint"].to_numpy(dtype=float)
    logger.info("Feature matrix shape: %s", X.shape)

    logger.info("Step 4: Training and comparing models")
    training = train_and_compare(X, y, builder.feature_names)
    for name, info in training["results"].items():
        logger.info("%-20s %s", name, info["metrics"])

    best = best_model_name(training["results"])
    logger.info("Best model: %s", best)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    builder.save(MODELS_DIR / "feature_builder.pkl")
    with open(MODELS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(training["scaler"], f)
    with open(MODELS_DIR / "training_results.pkl", "wb") as f:
        pickle.dump(training["results"], f)
    with open(MODELS_DIR / "best_model_name.txt", "w") as f:
        f.write(best)

    logger.info("Saved feature builder, scaler, and trained models to %s", MODELS_DIR)
    return clean_df, training


if __name__ == "__main__":
    run_pipeline()
