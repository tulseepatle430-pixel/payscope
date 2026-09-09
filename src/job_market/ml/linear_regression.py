"""Ridge (L2-regularized) linear regression via the closed-form normal equation.

Implemented directly with numpy.linalg (no scikit-learn) — solves
w = (X^T X + alpha*I)^-1 X^T y on standardized features, with a bias column.
Small regularization (alpha) keeps the solve stable when one-hot-encoded
categorical features introduce collinearity.
"""
from __future__ import annotations

import numpy as np


class RidgeRegression:
    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha
        self.coef_: np.ndarray | None = None
        self.intercept_: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeRegression":
        n_samples, n_features = X.shape
        X_b = np.hstack([np.ones((n_samples, 1)), X])

        penalty = self.alpha * np.eye(n_features + 1)
        penalty[0, 0] = 0.0  # don't regularize the intercept

        weights = np.linalg.solve(X_b.T @ X_b + penalty, X_b.T @ y)
        self.intercept_ = float(weights[0])
        self.coef_ = weights[1:]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.intercept_ + X @ self.coef_
