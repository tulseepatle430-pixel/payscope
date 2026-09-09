import numpy as np

from job_market.ml.decision_tree import DecisionTreeRegressor
from job_market.ml.gradient_boosting import GradientBoostingRegressor
from job_market.ml.linear_regression import RidgeRegression
from job_market.ml.metrics import r2_score
from job_market.ml.random_forest import RandomForestRegressor


def _linear_data(n=200, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 10, size=(n, 2))
    y = 3 * X[:, 0] - 2 * X[:, 1] + 5 + rng.normal(0, 0.1, size=n)
    return X, y


def test_ridge_regression_fits_linear_signal():
    X, y = _linear_data()
    model = RidgeRegression(alpha=0.01).fit(X, y)
    preds = model.predict(X)
    assert r2_score(y, preds) > 0.95


def test_decision_tree_fits_training_data_reasonably():
    X, y = _linear_data()
    model = DecisionTreeRegressor(max_depth=5).fit(X, y)
    preds = model.predict(X)
    assert r2_score(y, preds) > 0.8


def test_random_forest_beats_single_tree_on_noisy_data():
    rng = np.random.default_rng(1)
    X, y = _linear_data(n=300, seed=1)
    y_noisy = y + rng.normal(0, 2.0, size=len(y))

    X_train, X_test = X[:200], X[200:]
    y_train, y_test = y_noisy[:200], y_noisy[200:]

    tree = DecisionTreeRegressor(max_depth=8, min_samples_split=2).fit(X_train, y_train)
    forest = RandomForestRegressor(n_estimators=30, max_depth=8).fit(X_train, y_train)

    tree_r2 = r2_score(y_test, tree.predict(X_test))
    forest_r2 = r2_score(y_test, forest.predict(X_test))
    assert forest_r2 > tree_r2


def test_gradient_boosting_improves_over_baseline():
    X, y = _linear_data()
    baseline_pred = np.full_like(y, y.mean())
    model = GradientBoostingRegressor(n_estimators=50, learning_rate=0.1, max_depth=3).fit(X, y)
    preds = model.predict(X)
    assert r2_score(y, preds) > r2_score(y, baseline_pred)


def test_tree_feature_importances_sum_to_one():
    X, y = _linear_data()
    model = DecisionTreeRegressor(max_depth=5).fit(X, y)
    assert abs(model.feature_importances_.sum() - 1.0) < 1e-9
