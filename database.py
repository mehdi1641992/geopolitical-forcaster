"""
database.py - SQLite setup and queries for the forecasting app
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "forecaster.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    # Store daily news headlines
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT,
            title TEXT,
            source TEXT,
            url TEXT,
            description TEXT,
            region TEXT
        )
    """)

    # Store daily market snapshots
    c.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT,
            symbol TEXT,
            name TEXT,
            price REAL,
            change_pct REAL,
            volume REAL,
            category TEXT
        )
    """)

    # Store AI-generated forecasts
    c.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            forecast_type TEXT,
            title TEXT,
            summary TEXT,
            short_term TEXT,
            medium_term TEXT,
            long_term TEXT,
            confidence TEXT,
            risk_level TEXT,
            raw_json TEXT
        )
    """)

    # Store historical price data for trend analysis
    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            symbol TEXT,
            close_price REAL,
            volume REAL,
            UNIQUE(date, symbol)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized.")


def save_news(articles, region="global"):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    for a in articles:
        c.execute("""
            INSERT INTO news (fetched_at, title, source, url, description, region)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (now, a.get("title"), a.get("source", {}).get("name"),
              a.get("url"), a.get("description"), region))
    conn.commit()
    conn.close()


def save_market_data(records):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    for r in records:
        c.execute("""
            INSERT INTO market_data (fetched_at, symbol, name, price, change_pct, volume, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now, r["symbol"], r["name"], r["price"], r["change_pct"], r["volume"], r["category"]))
    conn.commit()
    conn.close()


def save_price_history(symbol, rows):
    """rows: list of (date_str, close_price, volume)"""
    conn = get_conn()
    c = conn.cursor()
    for date_str, close_price, volume in rows:
        c.execute("""
            INSERT OR IGNORE INTO price_history (date, symbol, close_price, volume)
            VALUES (?, ?, ?, ?)
        """, (date_str, symbol, close_price, volume))
    conn.commit()
    conn.close()


def save_forecast(forecast_type, data: dict):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("""
        INSERT INTO forecasts (created_at, forecast_type, title, summary, short_term, medium_term, long_term, confidence, risk_level, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now, forecast_type,
        data.get("title", ""),
        data.get("summary", ""),
        data.get("short_term", ""),
        data.get("medium_term", ""),
        data.get("long_term", ""),
        data.get("confidence", "medium"),
        data.get("risk_level", "medium"),
        json.dumps(data)
    ))
    conn.commit()
    conn.close()


def get_latest_forecasts(limit=10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM forecasts ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_latest_news(limit=20):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY fetched_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_latest_market_data():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM market_data
        WHERE fetched_at = (SELECT MAX(fetched_at) FROM market_data)
        ORDER BY category, symbol
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_price_history(symbol, days=90):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT date, close_price FROM price_history
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT ?
    """, (symbol, days))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
