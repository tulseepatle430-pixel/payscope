"""Gradient boosting regressor: additive shallow trees fit to residuals.

Standard least-squares gradient boosting: start from the mean, then
repeatedly fit a shallow regression tree to the current residuals and add
`learning_rate * tree.predict(X)` to the running prediction.
"""
from __future__ import annotations

import numpy as np

from .decision_tree import DecisionTreeRegressor


class GradientBoostingRegressor:
    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 3,
        min_samples_split: int = 10,
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees: list[DecisionTreeRegressor] = []
        self.init_value_: float = 0.0
        self.feature_importances_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GradientBoostingRegressor":
        self.init_value_ = float(np.mean(y))
        prediction = np.full(len(y), self.init_value_)
        self.trees = []
        importance_sum = np.zeros(X.shape[1])

        for i in range(self.n_estimators):
            residuals = y - prediction
            tree = DecisionTreeRegressor(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(X, residuals, seed=i)
            prediction += self.learning_rate * tree.predict(X)
            self.trees.append(tree)
            importance_sum += tree.feature_importances_

        self.feature_importances_ = importance_sum / self.n_estimators
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        prediction = np.full(X.shape[0], self.init_value_)
        for tree in self.trees:
            prediction += self.learning_rate * tree.predict(X)
        return prediction
