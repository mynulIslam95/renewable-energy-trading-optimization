"""Auditable research methods. All trading results are hypothetical."""
from __future__ import annotations
import math
from statistics import mean


def chronological_splits(rows, train_fraction=.6, validation_fraction=.2):
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1 or train_fraction+validation_fraction >= 1:
        raise ValueError('invalid chronological split')
    a=int(len(rows)*train_fraction); b=int(len(rows)*(train_fraction+validation_fraction))
    if a<1 or b<=a or b>=len(rows): raise ValueError('insufficient observations')
    return rows[:a], rows[a:b], rows[b:]


def forecast_metrics(rows, key='forecast_mw'):
    errors=[r[key]-r['actual_mw'] for r in rows]
    if not errors: raise ValueError('empty sample')
    return {'n':len(errors),'mae_mw':mean(map(abs,errors)), 'rmse_mw':math.sqrt(mean(e*e for e in errors)), 'bias_mw':mean(errors)}


def lagged_baseline(rows, lag=96):
    """Past-observation benchmark; no contemporaneous actual value is used."""
    if lag<1: raise ValueError('lag must be positive')
    out=[]
    for i in range(lag,len(rows)):
        r=dict(rows[i]); r['baseline_mw']=rows[i-lag]['actual_mw']; out.append(r)
    return out


def fit_meta_weight(train, first='forecast_mw', second='baseline_mw'):
    """Fit constrained 2-forecast blend on training data ONLY."""
    numerator=sum((r[first]-r[second])*(r['actual_mw']-r[second]) for r in train)
    denominator=sum((r[first]-r[second])**2 for r in train)
    return max(0.,min(1.,numerator/denominator)) if denominator else .5


def apply_meta(rows, weight, first='forecast_mw', second='baseline_mw'):
    return [dict(r,meta_mw=weight*r[first]+(1-weight)*r[second]) for r in rows]


def backtest_day_ahead(rows, forecast_key='forecast_mw', interval_hours=.25, imbalance_discount=.15):
    """Simplified contracted generation model, NOT executable intraday trading.

    Sells forecast MWh at observed day-ahead price. Deviations settle at a
    synthetic discounted price. This is a sensitivity analysis, not historical P&L.
    """
    if interval_hours<=0 or not 0<=imbalance_discount<=1: raise ValueError('invalid parameters')
    trades=[]
    for r in rows:
        p=r['day_ahead_eur_mwh']; q=r[forecast_key]*interval_hours; actual=r['actual_mw']*interval_hours
        imbalance_price=p*(1+imbalance_discount) if actual<q else p*(1-imbalance_discount)
        revenue=q*p+(actual-q)*imbalance_price
        perfect=actual*p
        trades.append({'timestamp_utc':r['timestamp_utc'], 'contract_mwh':q, 'actual_mwh':actual,
                       'imbalance_mwh':actual-q,'day_ahead_price':p,'assumed_imbalance_price':imbalance_price,
                       'simulated_revenue_eur':revenue,'perfect_information_revenue_eur':perfect})
    return trades


def revenue_summary(trades):
    if not trades: raise ValueError('empty trades')
    revenue=sum(x['simulated_revenue_eur'] for x in trades)
    oracle=sum(x['perfect_information_revenue_eur'] for x in trades)
    return {'n':len(trades),'simulated_revenue_eur':revenue,'oracle_revenue_eur':oracle,
            'simulated_forecast_error_cost_eur':oracle-revenue,
            'absolute_imbalance_mwh':sum(abs(x['imbalance_mwh']) for x in trades)}


def risk_summary(trades):
    """Descriptive loss statistics, not financial VaR or market-risk calibration."""
    losses=sorted(x['perfect_information_revenue_eur']-x['simulated_revenue_eur'] for x in trades)
    if not losses: raise ValueError('empty trades')
    threshold=losses[min(len(losses)-1,math.ceil(.95*len(losses))-1)]
    tail=[x for x in losses if x>=threshold]
    return {'p95_interval_loss_eur':threshold,'mean_tail_interval_loss_eur':mean(tail),
            'worst_interval_loss_eur':losses[-1]}


def battery_dispatch(prices, capacity_mwh=4., power_mw=2., efficiency=.9, interval_hours=.25, soc_steps=40):
    """Offline dynamic-programming upper bound with terminal SOC=0.

    Assumes perfect future price knowledge and zero degradation. NOT a deployable
    trading strategy. Discretized SOC; per-leg sqrt(roundtrip efficiency).
    """
    if capacity_mwh<=0 or power_mw<=0 or not 0<efficiency<=1 or interval_hours<=0 or soc_steps<2:
        raise ValueError('invalid battery configuration')
    step=capacity_mwh/soc_steps; leg=math.sqrt(efficiency); max_grid=power_mw*interval_hours
    values=[float('-inf')]*(soc_steps+1); values[0]=0.; history=[]
    for price in prices:
        nxt=[float('-inf')]*(soc_steps+1); parent=[None]*(soc_steps+1)
        for state,base in enumerate(values):
            if not math.isfinite(base): continue
            for target in range(soc_steps+1):
                change=(target-state)*step
                grid_energy=change/leg if change>0 else change*leg
                if abs(grid_energy)>max_grid+1e-9: continue
                score=base-grid_energy*price
                if score>nxt[target]: nxt[target]=score; parent[target]=(state,grid_energy)
        values=nxt; history.append(parent)
    if not math.isfinite(values[0]): raise ValueError('no feasible schedule')
    state=0; schedule=[]
    for t in range(len(prices)-1,-1,-1):
        prev,energy=history[t][state]; schedule.append({'step':t,'price_eur_mwh':prices[t],
            'grid_energy_mwh':energy,'soc_end_mwh':state*step,'cashflow_eur':-energy*prices[t]}); state=prev
    schedule.reverse()
    return {'gross_arbitrage_eur':values[0], 'schedule':schedule,
            'note':'Perfect-foresight offline upper bound; excludes degradation, tariffs and fees.'}
