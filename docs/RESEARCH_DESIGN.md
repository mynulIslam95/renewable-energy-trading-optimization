# Research design and limitations

## Objective
Compare renewable generation forecast baselines and simulated financial exposure from forecast deviations. Assess an offline battery arbitrage upper bound. This is **not** a live trading system.

## Data requirements for genuine market research

* UTC interval start and resolution, delivery area, unit, source URL and retrieval date.
* Actual renewable generation MW, *published-before-decision* generation forecasts MW, day-ahead price EUR/MWh.
* Actual imbalance settlement prices and intraday transaction prices require separate, provenance-verified sources.
* Preserve original timestamps, publication/issue time, product resolution, DST handling and revisions. Never silently interpolate.
* Historical forecasts cannot be reconstructed by adding noise to realized generation.

## Model governance

Chronological 60/20/20 train/validation/test split. Meta-forecast weight fitted only on training observations. Lag-96 naive forecast uses a past actual value. However, for day-ahead trading this 24-hour lag may not be available at auction cutoff: it is an **illustrative retrospective benchmark**, not an executable day-ahead signal. Before claiming trading validity, replace it with an as-of-aware benchmark based on the market gate closure and forecast issue times.

The day-ahead revenue model uses observed day-ahead prices, hypothetical forecast-based contract volumes and a *fabricated* settlement-price spread. It must not be represented as historical trading P&L. The battery optimizer sees all prices in advance and therefore provides an optimistic upper bound, not a realistic executable dispatch policy. Neither trading transaction costs nor market impact are modeled.

## Acceptance criteria for future production-grade research

1. Ingest provenance-verified historical prices and actuals.
2. Add forecast issue timestamps and verify as-of correctness.
3. Obtain licensed or openly released actual imbalance and intraday prices.
4. Use gate-closure-aware signal generation, walk-forward retraining and truly out-of-sample evaluation.
5. Optimize multiple assets with constraints, degradation, fees and forecast uncertainty.
6. Run sensitivity tests and bootstrap uncertainty estimates, report negative results.
7. Do not claim historical profitability until all of the above are complete.
