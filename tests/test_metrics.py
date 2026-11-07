import pytest
from renewable_trading.metrics import mae, rmse, bias, mape


def test_metrics():
    assert mae([10, 20], [12, 18]) == 2
    assert rmse([10, 20], [12, 18]) == 2
    assert bias([10, 20], [12, 18]) == 0
    assert mape([10, 20], [12, 18]) == pytest.approx(15)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        mae([], [])
    with pytest.raises(ValueError):
        rmse([1], [1, 2])
    with pytest.raises(ValueError):
        mape([0], [1])
