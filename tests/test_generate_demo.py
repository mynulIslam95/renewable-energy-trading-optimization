from renewable_trading.generate_demo import generate
from renewable_trading.data import load_market_csv

def test_generator_two_days_equivalent_year_2024(tmp_path):
    p = tmp_path / 'demo.csv'
    assert generate(p, 2024, 2024) == 366 * 96
    rows = load_market_csv(p)
    assert len(rows) == 366 * 96
    assert rows[0]['timestamp_utc'].year == 2024
