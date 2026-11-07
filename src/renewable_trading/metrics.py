"""Forecast metrics with explicit input validation."""
from math import sqrt


def _pairs(actual, predicted):
    a, p = list(actual), list(predicted)
    if not a or len(a) != len(p):
        raise ValueError("actual and predicted must have the same nonzero length")
    if any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in a + p):
        raise TypeError("inputs must be numeric")
    return a, p


def mae(actual, predicted):
    a, p = _pairs(actual, predicted)
    return sum(abs(x - y) for x, y in zip(a, p)) / len(a)


def rmse(actual, predicted):
    a, p = _pairs(actual, predicted)
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, p)) / len(a))


def bias(actual, predicted):
    """Mean predicted minus actual; positive means overforecasting."""
    a, p = _pairs(actual, predicted)
    return sum(y - x for x, y in zip(a, p)) / len(a)


def mape(actual, predicted):
    """Percentage error, undefined for zero actual values."""
    a, p = _pairs(actual, predicted)
    if any(x == 0 for x in a):
        raise ValueError("MAPE is undefined when actual contains zero")
    return 100 * sum(abs((x - y) / x) for x, y in zip(a, p)) / len(a)
