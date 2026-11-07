"""Strict, provenance-aware importers for externally obtained market observations."""
from __future__ import annotations
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_time(value: str) -> datetime:
    if not value or not value.strip():
        raise ValueError('missing timestamp')
    parsed = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamps must include timezone offset')
    return parsed.astimezone(timezone.utc)


def import_market_csv(source: str, output: str, *, timestamp_column: str,
                      value_column: str, metric: str, unit: str,
                      source_url: str, retrieved_at: str,
                      published_column: str | None = None) -> dict:
    """Normalize exported CSV into UTC, preserving lineage and optional publication time.

    No forward-fill or interpolation: missing/invalid values are rejected. Data
    may be actual generation, prices or forecast values, but never silently mixed.
    """
    if not source_url.startswith(('https://', 'http://')):
        raise ValueError('source_url must be a URL')
    retrieved = utc_time(retrieved_at)
    if not metric.strip() or not unit.strip():
        raise ValueError('metric and unit required')
    rows = []
    with open(source, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        required = {timestamp_column, value_column} | ({published_column} if published_column else set())
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f'missing CSV columns: {sorted(required-set(reader.fieldnames or []))}')
        for line, record in enumerate(reader, 2):
            try:
                timestamp = utc_time(record[timestamp_column])
                value = float(record[value_column].strip().replace(',', '.'))
                import math
                if not math.isfinite(value):
                    raise ValueError('non-finite value')
                published = utc_time(record[published_column]) if published_column else None
                if published and published > retrieved:
                    raise ValueError('publication time after retrieval time')
                rows.append({'timestamp_utc': timestamp.isoformat(), 'metric': metric,
                             'value': value, 'unit': unit,
                             'published_at_utc': published.isoformat() if published else None})
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'Invalid input at CSV line {line}: {exc}') from exc
    if not rows:
        raise ValueError('empty input CSV')
    times = [r['timestamp_utc'] for r in rows]
    if len(times) != len(set(times)):
        raise ValueError('duplicate UTC delivery timestamps')
    rows.sort(key=lambda r: r['timestamp_utc'])
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {'source_file': str(source), 'source_url': source_url,
                'retrieved_at_utc': retrieved.isoformat(), 'metric': metric,
                'unit': unit, 'observations': len(rows),
                'first_timestamp_utc': rows[0]['timestamp_utc'],
                'last_timestamp_utc': rows[-1]['timestamp_utc'],
                'publication_times_provided': bool(published_column),
                'verification_status': 'USER_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED'}
    destination.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return metadata


def join_market_series(series: dict[str, list[dict]], required_metrics: list[str]) -> list[dict]:
    """Inner join strictly on UTC delivery timestamps; no invented data."""
    indexes = {name: {r['timestamp_utc']: r for r in rows} for name, rows in series.items()}
    if any(metric not in indexes for metric in required_metrics):
        raise ValueError('missing required metric')
    common = set.intersection(*(set(indexes[m]) for m in required_metrics))
    return [{'timestamp_utc': ts, **{m: indexes[m][ts]['value'] for m in required_metrics}}
            for ts in sorted(common)]
