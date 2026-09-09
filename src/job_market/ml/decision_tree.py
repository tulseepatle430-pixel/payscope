"""CART regression tree, built from scratch with numpy.

Splits are chosen to minimize the weighted variance (MSE) of the two child
nodes, searched efficiently per feature via sorting + cumulative sums rather
than re-scanning all points for every candidate threshold.
"""
from __future__ import annotations

import numpy as np


class _Node:
    __slots__ = ("feature_idx", "threshold", "value", "left", "right")

    def __init__(self, value: float | None = None):
        self.feature_idx: int | None = None
        self.threshold: float | None = None
        self.value = value
        self.left: "_Node | None" = None
        self.right: "_Node | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


def _best_split_for_feature(x: np.ndarray, y: np.ndarray) -> tuple[float, float] | None:
    """Return (threshold, weighted_mse) minimizing MSE for a single feature, or None.

    Fully vectorized over all candidate split points at once (rather than a
    Python-level loop) so tree building stays fast at dataset sizes of a few
    thousand rows.
    """
    order = np.argsort(x)
    x_sorted, y_sorted = x[order], y[order]
    n = len(y)
    if n < 2:
        return None

    cum_sum = np.cumsum(y_sorted)
    cum_sq = np.cumsum(y_sorted**2)
    total_sum, total_sq = cum_sum[-1], cum_sq[-1]

    left_n = np.arange(1, n, dtype=float)
    right_n = n - left_n
    left_sum, left_sq = cum_sum[:-1], cum_sq[:-1]
    right_sum, right_sq = total_sum - left_sum, total_sq - left_sq

    left_mse = left_sq / left_n - (left_sum / left_n) ** 2
    right_mse = right_sq / right_n - (right_sum / right_n) ** 2
    weighted = (left_n * left_mse + right_n * right_mse) / n

    valid = x_sorted[1:] != x_sorted[:-1]
    if not valid.any():
        return None
    weighted = np.where(valid, weighted, np.inf)

    best_i = int(np.argmin(weighted))  # index into the 0..n-2 range, split is between best_i and best_i+1
    if not np.isfinite(weighted[best_i]):
        return None

    threshold = (x_sorted[best_i] + x_sorted[best_i + 1]) / 2
    return threshold, float(weighted[best_i])


class DecisionTreeRegressor:
    def __init__(self, max_depth: int = 6, min_samples_split: int = 10, max_features: float | None = None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features  # fraction of features considered per split (for random forests)
        self.root: _Node | None = None
        self.n_features_: int = 0
        self.feature_importances_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray, seed: int = 0) -> "DecisionTreeRegressor":
        self.n_features_ = X.shape[1]
        self._importance_accum = np.zeros(self.n_features_)
        rng = np.random.default_rng(seed)
        self.root = self._build(X, y, depth=0, rng=rng)

        total = self._importance_accum.sum()
        self.feature_importances_ = (
            self._importance_accum / total if total > 0 else self._importance_accum
        )
        return self

    def _build(self, X: np.ndarray, y: np.ndarray, depth: int, rng: np.random.Generator) -> _Node:
        if depth >= self.max_depth or len(y) < self.min_samples_split or np.all(y == y[0]):
            return _Node(value=float(np.mean(y)))

        candidate_features = range(self.n_features_)
        if self.max_features is not None:
            k = max(1, int(self.n_features_ * self.max_features))
            candidate_features = rng.choice(self.n_features_, size=k, replace=False)

        parent_mse = float(np.var(y))
        best_feature, best_threshold, best_mse = None, None, np.inf

        for f in candidate_features:
            result = _best_split_for_feature(X[:, f], y)
            if result is None:
                continue
            threshold, mse = result
            if mse < best_mse:
                best_feature, best_threshold, best_mse = f, threshold, mse

        if best_feature is None:
            return _Node(value=float(np.mean(y)))

        mask = X[:, best_feature] <= best_threshold
        if mask.all() or (~mask).all():
            return _Node(value=float(np.mean(y)))

        self._importance_accum[best_feature] += len(y) * (parent_mse - best_mse)

        node = _Node()
        node.feature_idx, node.threshold = best_feature, best_threshold
        node.left = self._build(X[mask], y[mask], depth + 1, rng)
        node.right = self._build(X[~mask], y[~mask], depth + 1, rng)
        return node

    def _predict_one(self, x: np.ndarray) -> float:
        node = self.root
        while not node.is_leaf:
            node = node.left if x[node.feature_idx] <= node.threshold else node.right
        return node.value

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._predict_one(row) for row in X])
