"""Leakage-controlled, dependency-free time-series regression baselines."""
from __future__ import annotations
from datetime import datetime, timedelta
from math import sqrt
from statistics import mean


def point_in_time_features(observations: list[dict], *, decision_time_key='decision_at_utc',
                           publication_key='published_at_utc', feature_keys=('forecast_mw',)) -> list[dict]:
    """Refuse forecasts that were not available when the decision was made."""
    output = []
    for row in observations:
        decision = datetime.fromisoformat(row[decision_time_key].replace('Z', '+00:00'))
        published = datetime.fromisoformat(row[publication_key].replace('Z', '+00:00'))
        if decision.tzinfo is None or published.tzinfo is None:
            raise ValueError('aware decision/publication timestamps required')
        if published > decision:
            raise ValueError(f'future forecast used at {row.get("timestamp_utc")}')
        for key in feature_keys:
            if row.get(key) is None:
                raise ValueError(f'missing feature {key}')
        output.append(dict(row))
    return output


def fit_ridge(train: list[dict], features: list[str], target='actual_mw', penalty=1.0):
    """Fit a small linear model via Gaussian elimination, with intercept unpenalized."""
    if not train or not features or penalty < 0:
        raise ValueError('training rows, features and nonnegative penalty required')
    size = len(features) + 1
    matrix = [[0.0]*size for _ in range(size)]
    vector = [0.0]*size
    for row in train:
        x = [1.0] + [float(row[f]) for f in features]
        y = float(row[target])
        for i in range(size):
            vector[i] += x[i]*y
            for j in range(size):
                matrix[i][j] += x[i]*x[j]
    for i in range(1, size):
        matrix[i][i] += penalty
    for k in range(size):
        pivot = max(range(k, size), key=lambda j: abs(matrix[j][k]))
        if abs(matrix[pivot][k]) < 1e-12:
            raise ValueError('singular model; increase regularization')
        matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
        vector[k], vector[pivot] = vector[pivot], vector[k]
        scale = matrix[k][k]
        matrix[k] = [x/scale for x in matrix[k]]
        vector[k] /= scale
        for j in range(size):
            if j == k:
                continue
            factor = matrix[j][k]
            matrix[j] = [a-factor*b for a,b in zip(matrix[j],matrix[k])]
            vector[j] -= factor*vector[k]
    return {'features': features, 'coefficients': vector, 'penalty': penalty}


def predict_ridge(model, rows):
    return [model['coefficients'][0] + sum(w*float(r[f]) for f,w in zip(model['features'],model['coefficients'][1:])) for r in rows]


def walk_forward_evaluation(rows, features, *, initial_train, test_window, step=None, penalty=1.0):
    """Expanding-window training, evaluating each later non-overlapping test block."""
    if initial_train < 2 or test_window < 1 or len(rows) <= initial_train:
        raise ValueError('invalid walk-forward parameters')
    if step is None:
        step = test_window
    if step < test_window:
        raise ValueError('step must be >= test_window to prevent duplicate predictions')
    ordered = sorted(rows, key=lambda r: r['timestamp_utc'])
    predictions = []
    for end in range(initial_train, len(ordered), step):
        model = fit_ridge(ordered[:end], features, penalty=penalty)
        block = ordered[end:min(end+test_window, len(ordered))]
        values = predict_ridge(model, block)
        predictions.extend({'timestamp_utc': r['timestamp_utc'], 'actual_mw': float(r['actual_mw']),
                            'predicted_mw': p, 'trained_through_utc': ordered[end-1]['timestamp_utc']}
                           for r,p in zip(block,values))
    errors = [r['predicted_mw']-r['actual_mw'] for r in predictions]
    return {'n':len(predictions), 'mae_mw':mean(map(abs, errors)),
            'rmse_mw':sqrt(mean(e*e for e in errors)), 'predictions':predictions}
