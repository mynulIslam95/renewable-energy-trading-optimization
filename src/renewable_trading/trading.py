"""Historical settlement accounting with explicit non-execution caveat."""
from __future__ import annotations
from datetime import datetime


def settle_day_ahead(rows, *, fee_eur_per_mwh=0.0):
    """Compute ex-post contracted-volume settlement using observed imbalance prices.

    Inputs must include observed day-ahead and imbalance prices and a forecast
    issued no later than the declared decision time. Not an order-fill simulator.
    """
    if fee_eur_per_mwh < 0:
        raise ValueError('negative transaction fee')
    trades = []
    for row in rows:
        required = ('timestamp_utc','decision_at_utc','published_at_utc','forecast_mw',
                    'actual_mw','day_ahead_eur_mwh','imbalance_eur_mwh')
        if any(row.get(k) is None for k in required):
            raise ValueError('missing observed price, generation or timing information')
        decision = datetime.fromisoformat(row['decision_at_utc'].replace('Z','+00:00'))
        published = datetime.fromisoformat(row['published_at_utc'].replace('Z','+00:00'))
        delivery = datetime.fromisoformat(row['timestamp_utc'].replace('Z','+00:00'))
        if any(t.tzinfo is None for t in (decision,published,delivery)):
            raise ValueError('timezone-aware timestamps required')
        if published > decision or decision >= delivery:
            raise ValueError('point-in-time decision violation')
        hours = float(row.get('interval_hours', .25))
        if hours <= 0:
            raise ValueError('invalid interval')
        contracted = float(row['forecast_mw'])*hours
        actual = float(row['actual_mw'])*hours
        deviation = actual-contracted
        fee = abs(contracted)*fee_eur_per_mwh
        cashflow = contracted*float(row['day_ahead_eur_mwh']) + deviation*float(row['imbalance_eur_mwh']) - fee
        trades.append({'timestamp_utc':row['timestamp_utc'], 'contracted_mwh':contracted,
                       'deviation_mwh':deviation,'fees_eur':fee,'cashflow_eur':cashflow})
    if not trades:
        raise ValueError('empty settlement dataset')
    return {'total_cashflow_eur':sum(t['cashflow_eur'] for t in trades),
            'total_fees_eur':sum(t['fees_eur'] for t in trades),
            'absolute_imbalance_mwh':sum(abs(t['deviation_mwh']) for t in trades),
            'trades':trades, 'scope':'ex-post settlement accounting; not verified executable P&L'}
