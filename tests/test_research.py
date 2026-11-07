import math
import pytest
from renewable_trading.research import *

def sample(n=500):
    return [{'actual_mw':100+i%7,'forecast_mw':103+i%7,'day_ahead_eur_mwh':50+i%10,'timestamp_utc':i} for i in range(n)]

def test_chronological_splits():
    a,b,c=chronological_splits(sample()); assert (len(a),len(b),len(c))==(300,100,100)

def test_lag_uses_only_past():
    a=lagged_baseline(sample(),96); assert a[0]['baseline_mw']==100

def test_meta_weight_bounds():
    a=lagged_baseline(sample()); assert 0<=fit_meta_weight(a)<=1

def test_metrics():
    assert forecast_metrics(sample())['mae_mw']==3

def test_imbalance_penalty():
    t=backtest_day_ahead(sample(3)); assert revenue_summary(t)['simulated_forecast_error_cost_eur']>=0

def test_battery_flat_prices_no_profit():
    x=battery_dispatch([50]*8,soc_steps=8); assert abs(x['gross_arbitrage_eur'])<1e-7

def test_battery_spread():
    x=battery_dispatch([0,0,100,100],capacity_mwh=1,power_mw=4,soc_steps=4)
    assert x['gross_arbitrage_eur']>0
    assert abs(x['schedule'][-1]['soc_end_mwh'])<1e-8

def test_battery_limits():
    x=battery_dispatch([0,100],capacity_mwh=1,power_mw=1,soc_steps=4)
    assert all(abs(y['grid_energy_mwh'])<=.25+1e-8 for y in x['schedule'])

def test_risk():
    assert 'p95_interval_loss_eur' in risk_summary(backtest_day_ahead(sample(50)))
