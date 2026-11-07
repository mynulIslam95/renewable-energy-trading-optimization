import pytest
from renewable_trading.data import load_market_csv


def test_sample_csv():
    records = load_market_csv("data/synthetic_market_sample.csv")
    assert len(records) == 8
    assert records[0]["actual_mw"] == 100


def test_duplicate_timestamps(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text("timestamp_utc,actual_mw,forecast_mw,day_ahead_eur_mwh\n2026-01-01T00:00:00Z,1,1,50\n2026-01-01T00:00:00Z,2,2,51\n")
    with pytest.raises(ValueError, match="strictly increasing"):
        load_market_csv(path)
