# Renewable Energy Trading & Portfolio Optimization

**Python research platform for renewable power forecasting, market exposure analysis and battery dispatch optimization**

This repository explores the connection between renewable generation forecast quality and electricity portfolio decisions. It provides a reproducible workflow for evaluating quarter-hourly forecasts, blending forecast signals, estimating modeled imbalance exposure and studying battery dispatch under price assumptions.

The current benchmark uses **synthetic observations** generated for methodological testing. Reported revenue figures are simulation outputs, not realized trading returns.

## Research objectives

- Benchmark renewable generation forecasts using chronological evaluation.
- Evaluate whether weighted forecast blending improves error metrics.
- Quantify the sensitivity of modeled portfolio revenue to forecast deviations.
- Explore battery charge and discharge scheduling under a 24-hour price horizon.
- Preserve reproducible experiment outputs in JSON, CSV and SQLite.

## Workflow

```text
Quarter-hour market observations
               |
               v
     Data ingestion and checks
               |
               v
    Chronological evaluation
               |
        +------+------+
        |             |
        v             v
 Forecast metrics   Market exposure
        |             |
        +------+------+
               |
               v
      Storage optimization
               |
               v
       Reports and SQLite
```

## Getting started

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest
PYTHONPATH=src python -m pytest -q
```

Generate a synthetic demonstration dataset:

```bash
PYTHONPATH=src python -m renewable_trading.generate_demo
```

Run the experiment:

```bash
PYTHONPATH=src python -m renewable_trading.experiment \
  data/synthetic_market_2023_2025.csv \
  --synthetic \
  --out results/demo \
  --db results/demo.sqlite
```

The experiment writes machine-readable reports under `results/demo/` and stores research outputs in SQLite.

## Benchmark results

The demonstration dataset contains **105,216 synthetic quarter-hourly observations** spanning 2023–2025. A chronological holdout contains 21,044 test observations.

| Forecast | MAE (MW) | RMSE (MW) | Simulated revenue |
| --- | ---: | ---: | ---: |
| Lag baseline | 35.847 | 44.682 | €35.82 million |
| Forecast | 17.570 | 22.022 | €36.62 million |
| Blended forecast | **15.756** | **19.766** | **€36.70 million** |

On this synthetic benchmark, blending reduced MAE by approximately **10.3%** relative to the individual forecast. Modeled forecast-error costs decreased from approximately €765,811 to €686,267. The battery experiment yielded a €398.99 gross perfect-foresight upper bound for its simulated 24-hour scenario.

All monetary results depend on synthetic generation and price assumptions and should not be interpreted as market-validated profit estimates.

## Repository layout

```text
src/renewable_trading/
  cli.py
  data.py
  experiment.py
  generate_demo.py
  metrics.py
  research.py
  storage.py
tests/
docs/RESEARCH_DESIGN.md
pyproject.toml
```

## Research design

The methodology includes time-ordered data splits, forecast accuracy evaluation, simulated exposure calculations and an offline battery dispatch model. See [Research Design](docs/RESEARCH_DESIGN.md) for assumptions and experimental details.

## Scope and limitations

This is an offline quantitative research implementation, not a live trading system. The bundled observations and settlement prices are synthetic. The experiment does not establish verified point-in-time forecast availability, executable market fills or historical trading P&L. The battery study uses perfect foresight and does not establish deployable storage returns.

A historically grounded extension would incorporate sourced SMARD and ENTSO-E data, forecast issuance timestamps, gate-closure constraints, transaction costs and rolling-horizon dispatch.

## Reproducibility

The research workflow is intended to be run locally with Python. Automated tests cover key data, generation, metric and research functions. Experiment artifacts are generated locally rather than committed as benchmark evidence.
