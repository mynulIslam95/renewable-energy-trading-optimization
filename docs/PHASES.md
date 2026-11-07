# Implementation and validation status

## Phase 1: Data ingestion
Implemented strict CSV ingestion, UTC conversion, provenance metadata, duplicate rejection and time-key joins. User-supplied SMARD/ENTSO-E exports can be normalized. **No real market dataset was downloaded or independently verified.** SMARD and ENTSO-E export formats differ; map columns explicitly rather than guessing.

## Phase 2: Forecasting and settlement
Implemented ridge regression, expanding-window evaluation, point-in-time publication checks and settlement accounting using supplied observed imbalance prices. These components are independently tested. **No real-data model fitting or market backtest has been executed.** Forecast issue times must be obtained from the source.

## Phase 3: Rolling battery dispatch
Implemented forecast-based rolling-horizon battery scheduling with power, energy, efficiency and transaction-fee constraints. **Realistic price forecast inputs and external execution validation are still required.**

## Phase 4: Dashboard and CI
Implemented Streamlit research dashboard and GitHub Actions Python test matrix. Local tests passed; CI status must be confirmed on GitHub after upload. Dashboard is not a live market monitor.

## Reproducibility acceptance checklist
- [x] Unit tests for new research components
- [x] Explicit source provenance and UTC normalization
- [x] Point-in-time forecast validation function
- [x] Expanding-window regression baseline
- [x] Settlement accounting with externally supplied observed prices
- [x] Forecast-driven rolling dispatch
- [x] Streamlit experiment dashboard
- [x] GitHub Actions CI configuration
- [ ] Verified historical SMARD/ENTSO-E dataset
- [ ] Verified historical forecast publication timestamps
- [ ] Licensed/verified observed imbalance settlement prices
- [ ] Real-market walk-forward evaluation and sensitivity analysis
- [ ] Executable trading simulation with transaction costs and liquidity
- [ ] CI run confirmed on GitHub
