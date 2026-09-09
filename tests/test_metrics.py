import numpy as np

from job_market.ml.metrics import mae, r2_score, rmse


def test_perfect_prediction_zero_error():
    y = np.array([1.0, 2.0, 3.0])
    assert mae(y, y) == 0.0
    assert rmse(y, y) == 0.0
    assert r2_score(y, y) == 1.0


def test_mae_matches_hand_calculation():
    y_true = np.array([10.0, 20.0])
    y_pred = np.array([12.0, 16.0])
    assert mae(y_true, y_pred) == 3.0


def test_r2_worse_than_mean_is_negative():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([10.0, -10.0, 10.0, -10.0])
    assert r2_score(y_true, y_pred) < 0
