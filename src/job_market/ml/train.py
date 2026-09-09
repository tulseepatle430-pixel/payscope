"""Train and compare all models on a single train/test split."""
from __future__ import annotations

import numpy as np

from .baseline import MeanBaselineRegressor
from .gradient_boosting import GradientBoostingRegressor
from .linear_regression import RidgeRegression
from .metrics import regression_report
from .random_forest import RandomForestRegressor
from .decision_tree import DecisionTreeRegressor
from .splitting import StandardScaler, train_test_split


def train_and_compare(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    baseline = MeanBaselineRegressor().fit(X_train, y_train)
    results["Baseline (mean)"] = {
        "model": baseline,
        "uses_scaled_features": False,
        "metrics": regression_report(y_test, baseline.predict(X_test)),
    }

    ridge = RidgeRegression(alpha=1.0).fit(X_train_scaled, y_train)
    results["Linear Regression"] = {
        "model": ridge,
        "uses_scaled_features": True,
        "metrics": regression_report(y_test, ridge.predict(X_test_scaled)),
    }

    tree = DecisionTreeRegressor(max_depth=6, min_samples_split=10).fit(X_train, y_train)
    results["Decision Tree"] = {
        "model": tree,
        "uses_scaled_features": False,
        "metrics": regression_report(y_test, tree.predict(X_test)),
    }

    forest = RandomForestRegressor(n_estimators=50, max_depth=6, max_features=0.6).fit(X_train, y_train)
    results["Random Forest"] = {
        "model": forest,
        "uses_scaled_features": False,
        "metrics": regression_report(y_test, forest.predict(X_test)),
    }

    gbrt = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3).fit(X_train, y_train)
    results["Gradient Boosting"] = {
        "model": gbrt,
        "uses_scaled_features": False,
        "metrics": regression_report(y_test, gbrt.predict(X_test)),
    }

    return {
        "results": results,
        "scaler": scaler,
        "feature_names": feature_names,
        "split": {"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test},
    }


def best_model_name(results: dict) -> str:
    """Pick the model with the highest test-set R2 (baseline excluded from consideration)."""
    candidates = {k: v for k, v in results.items() if k != "Baseline (mean)"}
    return max(candidates, key=lambda k: candidates[k]["metrics"]["R2"])
