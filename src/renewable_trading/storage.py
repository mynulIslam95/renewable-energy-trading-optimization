"""SQLite research store with provenance and strict timestamp keys."""
import sqlite3

def persist(path, rows, source_label):
    if not source_label: raise ValueError('source_label required')
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS observations (timestamp_utc TEXT PRIMARY KEY, actual_mw REAL NOT NULL, forecast_mw REAL NOT NULL, day_ahead_eur_mwh REAL NOT NULL, source TEXT NOT NULL)')
        db.executemany('INSERT OR REPLACE INTO observations VALUES (?,?,?,?,?)',
           [(r['timestamp_utc'].isoformat(),r['actual_mw'],r['forecast_mw'],r['day_ahead_eur_mwh'],source_label) for r in rows])
        return db.execute('SELECT COUNT(*) FROM observations').fetchone()[0]
