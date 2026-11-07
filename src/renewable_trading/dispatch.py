"""Rolling-horizon battery scheduling with separate predicted and realized prices."""
from __future__ import annotations
from .research import battery_dispatch


def rolling_battery_dispatch(predicted_prices, realized_prices, *, horizon=96,
                             capacity_mwh=4., power_mw=2., efficiency=.9,
                             interval_hours=.25, fee_eur_per_mwh=0., soc_steps=40):
    """Re-optimize each interval, executing only the first forecast-based action.

    To ensure feasible plans with nonzero SOC, uses a DP over a rolling horizon
    with a terminal state matching current SOC. Forecasts must be supplied from
    an external point-in-time forecasting process; they are not verified here.
    """
    if len(predicted_prices)!=len(realized_prices) or not predicted_prices:
        raise ValueError('matching nonempty predicted and realized prices required')
    if horizon < 1 or fee_eur_per_mwh < 0:
        raise ValueError('invalid horizon or fee')
    from math import sqrt, isfinite
    step=capacity_mwh/soc_steps
    leg=sqrt(efficiency)
    max_grid=power_mw*interval_hours
    state=0
    cash=0.
    schedule=[]
    for t in range(len(realized_prices)):
        lookahead=predicted_prices[t:min(t+horizon,len(predicted_prices))]
        values=[float('-inf')]*(soc_steps+1)
        values[state]=0.
        paths=[]
        for price in lookahead:
            nxt=[float('-inf')]*(soc_steps+1)
            parents=[None]*(soc_steps+1)
            for s,base in enumerate(values):
                if not isfinite(base): continue
                for target in range(soc_steps+1):
                    change=(target-s)*step
                    grid=change/leg if change>0 else change*leg
                    if abs(grid)>max_grid+1e-9: continue
                    score=base-grid*price-abs(grid)*fee_eur_per_mwh
                    if score>nxt[target]:
                        nxt[target]=score; parents[target]=(s,grid)
            values=nxt;paths.append(parents)
        terminal=max(range(soc_steps+1),key=lambda s:values[s])
        for k in range(len(paths)-1,0,-1):
            terminal=paths[k][terminal][0]
        previous, grid=paths[0][terminal]
        assert previous==state
        state=terminal
        realized_cash=-grid*realized_prices[t]-abs(grid)*fee_eur_per_mwh
        cash+=realized_cash
        schedule.append({'step':t,'forecast_price_eur_mwh':predicted_prices[t],
                         'realized_price_eur_mwh':realized_prices[t],
                         'grid_energy_mwh':grid,'soc_end_mwh':state*step,
                         'cashflow_eur':realized_cash})
    return {'realized_gross_net_fees_eur':cash,'terminal_soc_mwh':state*step,
            'schedule':schedule,'scope':'forecast-driven dispatch; assumes supplied forecasts are point-in-time valid'}
