from datetime import datetime, timedelta, timezone
import csv
import pytest
from renewable_trading.market_data import import_market_csv, utc_time, join_market_series
from renewable_trading.forecasting import fit_ridge,predict_ridge,walk_forward_evaluation,point_in_time_features
from renewable_trading.trading import settle_day_ahead
from renewable_trading.dispatch import rolling_battery_dispatch


def test_import_and_lineage(tmp_path):
    source=tmp_path/'raw.csv'; output=tmp_path/'normalized.csv'
    source.write_text('time,price\n2025-01-01T01:00:00+01:00,42.5\n2025-01-01T00:15:00Z,43\n')
    metadata=import_market_csv(str(source),str(output),timestamp_column='time',value_column='price',
        metric='day_ahead_price',unit='EUR/MWh',source_url='https://www.smard.de/',retrieved_at='2025-01-02T00:00:00Z')
    assert metadata['observations']==2
    with output.open() as f: rows=list(csv.DictReader(f))
    assert rows[0]['timestamp_utc']=='2025-01-01T00:00:00+00:00'
    assert output.with_suffix('.metadata.json').exists()


def test_import_rejects_duplicate_utc(tmp_path):
    source=tmp_path/'raw.csv';source.write_text('t,v\n2025-01-01T00:00:00Z,2\n2025-01-01T01:00:00+01:00,3\n')
    with pytest.raises(ValueError,match='duplicate'):
        import_market_csv(str(source),str(tmp_path/'out.csv'),timestamp_column='t',value_column='v',
            metric='price',unit='EUR/MWh',source_url='https://example.com',retrieved_at='2025-01-02T00:00:00Z')


def test_point_in_time_rejects_future():
    rows=[{'timestamp_utc':'2025-01-02T00:00:00Z','decision_at_utc':'2025-01-01T12:00:00Z',
           'published_at_utc':'2025-01-01T13:00:00Z','forecast_mw':3}]
    with pytest.raises(ValueError,match='future forecast'):
        point_in_time_features(rows)


def test_ridge_and_walkforward():
    rows=[{'timestamp_utc':f'2025-01-{i+1:02d}T00:00:00Z','x':float(i),'actual_mw':float(2*i+3)} for i in range(15)]
    model=fit_ridge(rows[:10],['x'],penalty=.001)
    assert abs(predict_ridge(model,[{'x':11}])[0]-25)<.1
    result=walk_forward_evaluation(rows,['x'],initial_train=8,test_window=2,penalty=.001)
    assert result['n']==7
    assert result['mae_mw']<.1


def test_settlement_accounting():
    r={'timestamp_utc':'2025-01-02T00:00:00Z','decision_at_utc':'2025-01-01T12:00:00Z',
       'published_at_utc':'2025-01-01T10:00:00Z','forecast_mw':10,'actual_mw':8,
       'day_ahead_eur_mwh':100,'imbalance_eur_mwh':80}
    out=settle_day_ahead([r],fee_eur_per_mwh=1)
    assert out['total_cashflow_eur']==207.5
    with pytest.raises(ValueError):settle_day_ahead([{**r,'published_at_utc':'2025-01-01T13:00:00Z'}])


def test_rolling_dispatch_is_feasible():
    r=rolling_battery_dispatch([10,10,100,100],[10,10,100,100],horizon=4,
        capacity_mwh=1,power_mw=1,interval_hours=1,soc_steps=4)
    assert all(0<=x['soc_end_mwh']<=1 for x in r['schedule'])
    assert r['realized_gross_net_fees_eur']>=0
