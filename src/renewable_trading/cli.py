"""Command-line interface for first milestone: validated ingestion and baseline metrics."""
import argparse
import json
from .data import load_market_csv
from .metrics import mae, rmse, bias


def main(argv=None):
    parser = argparse.ArgumentParser(description="Renewable energy trading research CLI")
    parser.add_argument("csv", help="CSV with quarter-hourly UTC market observations")
    args = parser.parse_args(argv)
    rows = load_market_csv(args.csv)
    actual = [r["actual_mw"] for r in rows]
    forecast = [r["forecast_mw"] for r in rows]
    print(json.dumps({"observations": len(rows), "mae_mw": mae(actual, forecast),
                      "rmse_mw": rmse(actual, forecast), "bias_mw": bias(actual, forecast)}, indent=2))


if __name__ == "__main__":
    main()
