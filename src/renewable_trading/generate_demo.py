"""Generate reproducible SYNTHETIC data. Not a substitute for historical market observations."""
import argparse
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate(path, start_year=2023, end_year=2025, seed=42):
    if end_year < start_year:
        raise ValueError('end_year must not precede start_year')
    rng = random.Random(seed)
    start = datetime(start_year, 1, 1, tzinfo=timezone.utc)
    end = datetime(end_year + 1, 1, 1, tzinfo=timezone.utc)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp_utc','actual_mw','forecast_mw','day_ahead_eur_mwh'])
        t = start
        while t < end:
            day = t.timetuple().tm_yday
            hour = t.hour + t.minute / 60
            seasonal = math.sin(2 * math.pi * day / 365.25)
            diurnal = math.sin(2 * math.pi * (hour - 6) / 24)
            solar = max(0, diurnal) * (140 + 55 * seasonal)
            wind = max(5, 105 + 42 * math.sin(2 * math.pi * day / 8.7) + 28 * rng.gauss(0, 1))
            actual = max(0, solar + wind)
            forecast = max(0, actual + rng.gauss(0, 22) + 3 * seasonal)
            price = 78 + 15 * math.cos(2 * math.pi * (hour - 19) / 24) - 0.16 * actual + rng.gauss(0, 13)
            writer.writerow([t.isoformat().replace('+00:00','Z'), f'{actual:.3f}', f'{forecast:.3f}', f'{price:.3f}'])
            t += timedelta(minutes=15)
            count += 1
    return count


def main():
    p = argparse.ArgumentParser()
    p.add_argument('output')
    p.add_argument('--start-year', type=int, default=2023)
    p.add_argument('--end-year', type=int, default=2025)
    args = p.parse_args()
    print(f'Generated {generate(args.output, args.start_year, args.end_year):,} SYNTHETIC observations')

if __name__ == '__main__':
    main()
