"""CLI for reproducible, clearly labeled hypothetical experiments."""
import argparse
import csv
import json
from pathlib import Path
from .data import load_market_csv
from .research import (chronological_splits,forecast_metrics,lagged_baseline,fit_meta_weight,
                       apply_meta,backtest_day_ahead,revenue_summary,risk_summary,battery_dispatch)
from .storage import persist

def run(csv_path, output, synthetic=False, db=None):
    rows=load_market_csv(csv_path)
    if len(rows)<500: raise ValueError('research experiment requires >=500 observations')
    train,validation,test=chronological_splits(rows)
    lag=96
    # Train meta-weight only on past observations from the training interval.
    baseline_train=lagged_baseline(train,lag)
    weight=fit_meta_weight(baseline_train)
    # Validation/test lag features can use preceding historical observations.
    baseline_all=lagged_baseline(rows,lag)
    test_rows=[r for r in baseline_all if r['timestamp_utc']>=test[0]['timestamp_utc']]
    meta=apply_meta(test_rows,weight)
    strategies={}
    for key in ('forecast_mw','baseline_mw','meta_mw'):
        trades=backtest_day_ahead(meta,key)
        strategies[key]={'forecast':forecast_metrics(meta,key), 'revenue':revenue_summary(trades),
                         'risk':risk_summary(trades)}
    # Battery study uses just 1 day to bound DP runtime, with perfect foresight clearly disclosed.
    battery=battery_dispatch([r['day_ahead_eur_mwh'] for r in test[:96]],soc_steps=20)
    report={'dataset':str(csv_path),'data_classification':'SYNTHETIC' if synthetic else 'USER-SUPPLIED (NOT INDEPENDENTLY VERIFIED)',
            'observations':len(rows),'train':len(train),'validation':len(validation),'test':len(test),
            'meta_weight_fitted_on_train':weight,'strategies':strategies,
            'battery_24h_offline_upper_bound_eur':battery['gross_arbitrage_eur'],
            'limitations':['Input forecast publication times are not verified.',
                           'Synthetic imbalance prices are not observed settlement prices.',
                           'Backtest does not represent executable day-ahead/intraday strategies.',
                           'Battery uses perfect foresight and excludes degradation and fees.',
                           'No transaction costs, liquidity or operational constraints beyond the modeled battery limits.']}
    out=Path(output); out.mkdir(parents=True,exist_ok=True)
    (out/'report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    with (out/'battery_schedule.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=battery['schedule'][0].keys()); writer.writeheader(); writer.writerows(battery['schedule'])
    if db: persist(db,rows,'synthetic' if synthetic else 'user_supplied_unverified')
    return report

def main():
    p=argparse.ArgumentParser(description='Research experiment, NOT live trading')
    p.add_argument('csv'); p.add_argument('--out',default='results/demo'); p.add_argument('--synthetic',action='store_true'); p.add_argument('--db')
    args=p.parse_args(); r=run(args.csv,args.out,args.synthetic,args.db)
    print(json.dumps({'observations':r['observations'],'test':r['test'],'output':args.out,'classification':r['data_classification']},indent=2))
if __name__=='__main__': main()
