# Renewable Energy Trading & Portfolio Optimization

**Quantitative research in renewable generation forecasting, electricity-market exposure and storage dispatch**

A Python research platform for studying how renewable generation forecasts influence electricity-market outcomes. The project combines time-series evaluation, forecast blending, simulated day-ahead settlement sensitivity, battery dispatch optimization and reproducible experiment reporting.

The current benchmark uses a deterministic **synthetic** dataset. Its purpose is to test the analytical workflow and compare methods under controlled assumptions. Results are not observations of actual German trading performance.

## Research questions

1. How much does forecast blending improve accuracy over a single forecast and a lag-based baseline?
2. How do forecast errors translate into modeled imbalance exposure and revenue sensitivity?
3. What is the theoretical value of flexible battery dispatch under a known 24-hour price trajectory?
4. How can these experiments be made reproducible and auditable?

## Architecture

```text
Quarter-hour observations (CSV)
             |
             v
     Validation and ingestion --------> SQLite archive
             |
             v
   Chronological data partition
             |
             v
  Baseline / single / blended forecasts
             |
             v
  Accuracy, exposure and risk analysis
             |
             +----> Battery dispatch optimization
             |
             v
      JSON and CSV research outputs
```

The implementation uses Python's standard library for its research pipeline and SQLite for local persistence. Tests run with `pytest`.

## Methods

**Forecast evaluation.** Compare the supplied forecast, a 96-interval lag baseline and a weighted blend. Report mean absolute error (MAE), root mean squared error (RMSE) and mean bias error in MW.

**Chronological evaluation.** Partition observations into training, validation and test periods in time order. Fit the blending weight using the training period, then evaluate the approaches on the held-out test period.

**Market exposure study.** Translate forecast deviations into hypothetical settlement exposure using the model's price assumptions. Compare simulated revenue, absolute imbalance volume and interval-loss statistics. This is a sensitivity analysis, not a market-executable trading backtest.

**Storage dispatch.** Solve a discretized battery charge/discharge scheduling problem over a 24-hour price horizon. The reported value is an offline, perfect-foresight upper bound, before degradation and transaction costs.

For assumptions and methodological boundaries, see [`docs/RESEARCH_DESIGN.md`](docs/RESEARCH_DESIGN.md).

## Reproduce the experiment

Requires Python 3.10 or newer. Run from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

Generate the reproducible demonstration dataset:

```bash
python -m renewable_trading.generate_demo data/synthetic_market_2023_2025.csv
```

Run the complete experiment:

```bash
python -m renewable_trading.experiment \
  data/synthetic_market_2023_2025.csv \
  --synthetic \
  --out results/demo \
  --db results/demo.sqlite
```

The experiment writes `results/demo/report.json`, `results/demo/battery_schedule.csv` and a SQLite archive at `results/demo.sqlite`.

## Benchmark results

The following results come from the deterministic synthetic 2023–2025 dataset: **105,216 quarter-hour observations**, including **21,044 held-out test observations**. Values are rounded from one local experiment run.

| Forecast approach | MAE (MW) | RMSE (MW) | Modeled forecast-error cost (EUR) |
| --- | ---: | ---: | ---: |
| Lag baseline | 35.85 | 44.68 | 1,568,089 |
| Supplied forecast | 17.57 | 22.02 | 765,811 |
| Blended forecast | **15.76** | **19.77** | **686,267** |

In this synthetic experiment, blending reduced MAE by approximately **10.3%** relative to the supplied forecast. The battery study produced a **EUR 398.99** perfect-foresight gross arbitrage upper bound for one simulated 24-hour window. Neither figure should be interpreted as verified historical or achievable trading profit.

## Repository structure

```text
src/renewable_trading/
  data.py            # Input parsing and timestamp validation
  generate_demo.py   # Seeded synthetic data generation
  research.py        # Forecasting, exposure, risk and dispatch models
  experiment.py      # Reproducible experiment orchestration
  storage.py         # SQLite persistence
  metrics.py         # Forecast evaluation helpers
  cli.py             # Command-line entry point

tests/               # Automated checks
docs/RESEARCH_DESIGN.md
pyproject.toml
```

## Research boundaries and next steps

This repository currently demonstrates a **controlled research workflow**, not a live trading system. The dataset is synthetic. Forecast issuance times and market gate closures have not been independently verified. The settlement-price model is hypothetical, and the battery optimizer has perfect price foresight. Realistic execution costs, market liquidity, battery degradation and actual intraday order execution are outside the current experiment.

The next research phase is to ingest sourced German market observations, enforce point-in-time forecast availability, implement rolling-horizon dispatch and evaluate trading rules with realistic settlement and execution assumptions. Any future empirical claims should be supported by traceable datasets, explicit market conventions and reproducible out-of-sample results.

## Scope

This is an independent software engineering and quantitative research portfolio project. It is not affiliated with an electricity exchange or energy trading company, and it does not place orders or provide investment advice.

## Extended research modules

The repository includes additional modules for a reproducible four-stage research workflow:

1. **Market data foundation:** `market_data.py` and `market_cli.py` normalize user-exported SMARD/ENTSO-E CSV files to UTC, reject duplicate timestamps and preserve a source URL, retrieval time, unit and publication metadata. No live data is bundled or independently verified.
2. **Point-in-time forecasting:** `forecasting.py` checks forecast publication against decision timestamps and implements ridge regression with expanding-window evaluation. This is a transparent baseline, not a trained production forecast.
3. **Historical settlement and rolling dispatch:** `trading.py` accepts observed imbalance and day-ahead prices with time-aware forecast records; `dispatch.py` executes only the first action of each forecast-based battery schedule. The settlement model is not an order-execution simulator.
4. **Dashboard and CI:** `dashboard.py` visualizes generated experiment reports and `.github/workflows/tests.yml` tests Python 3.10, 3.12 and 3.13.

### Import an exported market CSV

Download the relevant historical CSV directly from [SMARD](https://www.smard.de/en) or [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/). Inspect the export's actual column names, resolution, timezone and licensing before importing. Do not treat a CSV lacking an explicit timezone as verified.

```bash
python -m renewable_trading.market_cli \
  examples/sourced_market_sample.csv results/import/day_ahead.csv \
  --timestamp-column timestamp_utc \
  --value-column day_ahead_eur_mwh \
  --metric day_ahead_price --unit EUR/MWh \
  --source-url https://www.smard.de/en \
  --retrieved-at 2025-01-02T00:00:00Z
```

The example CSV contains illustrative values, not authenticated SMARD records. The importer writes a normalized CSV and a JSON provenance manifest. It does **not** automatically verify a source's authenticity or infer forecast issue times.

### Interactive dashboard

```bash
python -m pip install -e '.[dashboard]'
streamlit run src/renewable_trading/dashboard.py
```

Run the experiment first to create `results/demo/report.json`.

### Research integrity

These modules provide working building blocks, not an end-to-end validated historical strategy. A real-data experiment requires separately sourced and joined actual generation, point-in-time forecasts, day-ahead prices and observed imbalance prices. No historical P&L or market profitability is claimed without those inputs.
