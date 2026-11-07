"""Command line interface for normalized, provenance-tracked market CSV imports."""
import argparse
import json
from .market_data import import_market_csv

def main():
    p=argparse.ArgumentParser(description='Import sourced market CSV without silent imputation')
    p.add_argument('source');p.add_argument('output')
    p.add_argument('--timestamp-column',required=True)
    p.add_argument('--value-column',required=True)
    p.add_argument('--metric',required=True)
    p.add_argument('--unit',required=True)
    p.add_argument('--source-url',required=True)
    p.add_argument('--retrieved-at',required=True,help='ISO-8601 timestamp with UTC offset')
    p.add_argument('--published-column')
    a=p.parse_args()
    print(json.dumps(import_market_csv(a.source,a.output,timestamp_column=a.timestamp_column,
        value_column=a.value_column,metric=a.metric,unit=a.unit,source_url=a.source_url,
        retrieved_at=a.retrieved_at,published_column=a.published_column),indent=2))

if __name__=='__main__':main()
