"""Build the ML feature matrix: one-hot categoricals (capped cardinality),
binary skill indicators (top-K most common skills), and numeric experience.

The builder is fit on training data only (which categories/skills count as
columns) and then applied identically to any other data — including a single
user-entered row at prediction time — so train/serve feature spaces always
match.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

CATEGORICAL_COLUMNS = ["job_title", "location", "education", "employment_type", "industry"]


@dataclass
class FeatureBuilder:
    top_categories: dict[str, list[str]] = field(default_factory=dict)
    top_skills: list[str] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    max_categories_per_column: int = 15
    max_skills: int = 30

    def fit(self, df: pd.DataFrame) -> "FeatureBuilder":
        for col in CATEGORICAL_COLUMNS:
            self.top_categories[col] = (
                df[col].value_counts().head(self.max_categories_per_column).index.tolist()
            )

        skill_counts = df.explode("skills")["skills"].value_counts()
        self.top_skills = skill_counts.head(self.max_skills).index.tolist()

        self.feature_names = ["experience_years"]
        for col in CATEGORICAL_COLUMNS:
            self.feature_names += [f"{col}={v}" for v in self.top_categories[col]]
        self.feature_names += [f"skill={s}" for s in self.top_skills]
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        n = len(df)
        columns = [df["experience_years"].to_numpy(dtype=float).reshape(n, 1)]

        for col in CATEGORICAL_COLUMNS:
            for category in self.top_categories[col]:
                columns.append((df[col] == category).to_numpy(dtype=float).reshape(n, 1))

        skill_sets = df["skills"].apply(set)
        for skill in self.top_skills:
            columns.append(skill_sets.apply(lambda s: skill in s).to_numpy(dtype=float).reshape(n, 1))

        return np.hstack(columns)

    def transform_single(
        self,
        experience_years: float,
        job_title: str,
        location: str,
        education: str,
        employment_type: str,
        industry: str,
        skills: list[str],
    ) -> np.ndarray:
        row = pd.DataFrame(
            [
                {
                    "experience_years": experience_years,
                    "job_title": job_title,
                    "location": location,
                    "education": education,
                    "employment_type": employment_type,
                    "industry": industry,
                    "skills": skills,
                }
            ]
        )
        return self.transform(row)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: Path) -> "FeatureBuilder":
        with open(path, "rb") as f:
            return pickle.load(f)
