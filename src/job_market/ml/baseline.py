"""Trivial baseline: always predict the training mean.

Every real model must beat this to be worth using — it's the floor, not a
model in the interesting sense.
"""
from __future__ import annotations

import numpy as np


class MeanBaselineRegressor:
    def __init__(self) -> None:
        self.mean_: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MeanBaselineRegressor":
        self.mean_ = float(np.mean(y))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(X.shape[0], self.mean_)
