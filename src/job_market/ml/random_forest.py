"""Random forest regressor: bagging of DecisionTreeRegressor with feature subsampling."""
from __future__ import annotations

import numpy as np

from .decision_tree import DecisionTreeRegressor


class RandomForestRegressor:
    def __init__(
        self,
        n_estimators: int = 50,
        max_depth: int = 6,
        min_samples_split: int = 10,
        max_features: float = 0.6,
        seed: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.seed = seed
        self.trees: list[DecisionTreeRegressor] = []
        self.feature_importances_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestRegressor":
        rng = np.random.default_rng(self.seed)
        n_samples, n_features = X.shape
        self.trees = []
        importance_sum = np.zeros(n_features)

        for i in range(self.n_estimators):
            bootstrap_idx = rng.integers(0, n_samples, size=n_samples)  # sample with replacement
            X_boot, y_boot = X[bootstrap_idx], y[bootstrap_idx]

            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                max_features=self.max_features,
            )
            tree.fit(X_boot, y_boot, seed=int(rng.integers(0, 1_000_000)))
            self.trees.append(tree)
            importance_sum += tree.feature_importances_

        self.feature_importances_ = importance_sum / self.n_estimators
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = np.column_stack([tree.predict(X) for tree in self.trees])
        return predictions.mean(axis=1)
