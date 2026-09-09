"""Extract a ranked feature-importance table from a trained model."""
from __future__ import annotations

import numpy as np


def tree_based_importance(model, feature_names: list[str], top_n: int = 15) -> list[dict]:
    """For DecisionTree/RandomForest/GradientBoosting: impurity-reduction based importance."""
    importances = model.feature_importances_
    order = np.argsort(importances)[::-1][:top_n]
    return [{"feature": feature_names[i], "importance": round(float(importances[i]), 4)} for i in order]


def linear_coefficient_importance(model, feature_names: list[str], top_n: int = 15) -> list[dict]:
    """For RidgeRegression on standardized features: |coefficient| ranks influence."""
    coefs = model.coef_
    order = np.argsort(np.abs(coefs))[::-1][:top_n]
    return [
        {"feature": feature_names[i], "coefficient": round(float(coefs[i]), 2)}
        for i in order
    ]
