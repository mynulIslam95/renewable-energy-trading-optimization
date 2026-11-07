"""CSV ingestion for quarter-hourly German electricity market observations."""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED = ("timestamp_utc", "actual_mw", "forecast_mw", "day_ahead_eur_mwh")


def load_market_csv(path):
    """Return validated records; timestamps must be unique, sorted UTC 15-minute slots."""
    records = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError(f"CSV must include {', '.join(REQUIRED)}")
        previous = None
        for row in reader:
            timestamp = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00"))
            if timestamp.utcoffset() != timedelta(0):
                raise ValueError("timestamps must explicitly use UTC")
            if timestamp.minute % 15 or timestamp.second or timestamp.microsecond:
                raise ValueError("timestamps must align to 15-minute boundaries")
            if previous is not None and timestamp <= previous:
                raise ValueError("timestamps must be strictly increasing and unique")
            previous = timestamp
            record = {"timestamp_utc": timestamp.astimezone(timezone.utc)}
            for name in REQUIRED[1:]:
                record[name] = float(row[name])
            if record["actual_mw"] < 0 or record["forecast_mw"] < 0:
                raise ValueError("generation MW cannot be negative")
            records.append(record)
    if not records:
        raise ValueError("CSV contains no observations")
    return records
