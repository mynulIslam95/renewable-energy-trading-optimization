# German Renewable Energy Trading & Portfolio Optimization Research Lab

**ENCAVIS-targeted portfolio project | Research prototype, not live trading**

Python research code for renewable generation forecasts, chronological model evaluation, simulated imbalance exposure, constrained battery dispatch and reproducible reporting. **Bundled 2023–2025 data are entirely synthetic (105,216 rows)**. The experiment does **not** demonstrate historical trading profits or access to licensed EPEX data.

## Run

Requires Python 3.10+. All research components use the standard library; `pytest` is optional for tests.

```bash
export PYTHONPATH=src  # Windows PowerShell: $env:PYTHONPATH="src"
python -m renewable_trading.experiment data/synthetic_market_2023_2025.csv --synthetic --out results/demo --db results/demo.sqlite
python -m pytest -q
```

## Modules

- `data.py`: UTC quarter-hour CSV validation
- `generate_demo.py`: deterministic **synthetic** dataset generator
- `research.py`: chronological splits, lagged benchmark, train-only two-forecast blend, forecast metrics, hypothetical settlement sensitivity, risk statistics, battery dynamic programming
- `storage.py`: SQLite observations with source label
- `experiment.py`: experiment orchestration, JSON report and battery schedule CSV
- `docs/RESEARCH_DESIGN.md`: methodological limitations, data provenance requirements and next acceptance criteria

## Output

`results/demo/report.json` includes test-period MAE/RMSE/bias, simulated revenue and risk by forecasting approach. `battery_schedule.csv` contains a perfect-foresight 24-hour battery schedule. **These numbers are synthetic and are not CV-ready trading performance claims.**

## Coverage and exclusions

| Feature | Status |
|---|---|
| 105,216 synthetic quarter-hour observations | Included |
| Forecast accuracy and meta-forecasting | Implemented (retrospective research) |
| Chronological holdout | Implemented |
| Forecast deviation revenue sensitivity | Implemented (hypothetical settlement price) |
| Battery charge/discharge optimization | Implemented (offline perfect foresight) |
| SQLite persistence, reports, unit tests | Implemented |
| Verified SMARD/ENTSO-E data | Not included |
| As-of/gate-closure verified forecasts | Not included |
| Actual intraday execution and ancillary services | Not included |
| Commercially validated historical P&L | Not established |

## CV positioning

Describe this accurately as a **renewable trading research prototype** until actual market data, forecast issuance timestamps and executable backtesting are added. The user’s existing bachelor thesis on day-ahead renewable generation forecasting is independently relevant to the role.
