"""
scheduler.py - Daily data fetch + forecast generation
Run this daily via PythonAnywhere Scheduled Tasks at midnight UTC.

PythonAnywhere setup:
  Dashboard → Tasks → Add new scheduled task
  Command: python3 /home/YOURUSERNAME/geopolitical-forecaster/scheduler.py
  Time: 00:30 UTC daily
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from database import init_db, save_news, save_market_data, save_price_history
from fetchers.news import fetch_all_regions, build_news_digest
from fetchers.stocks import (
    fetch_current_prices, fetch_all_history,
    build_market_summary, build_trend_summary
)
from analyzer import (
    generate_geopolitical_forecast,
    generate_market_forecast,
    generate_bd_specific_forecast,
)
from database import save_forecast


def run_daily_job():
    start = datetime.utcnow()
    print(f"\n{'='*60}")
    print(f"🌍 DAILY FORECAST JOB STARTED — {start.isoformat()}")
    print(f"{'='*60}")

    # 1. Init DB
    print("\n[1/6] Initializing database...")
    init_db()

    # 2. Fetch news
    print("\n[2/6] Fetching news headlines...")
    region_articles = fetch_all_regions()
    for region, articles in region_articles.items():
        save_news(articles, region=region)
    news_digest = build_news_digest(region_articles)
    print(f"  📰 Total articles: {sum(len(v) for v in region_articles.values())}")

    # 3. Fetch current market data
    print("\n[3/6] Fetching current market prices...")
    market_records = fetch_current_prices()
    save_market_data(market_records)
    market_summary = build_market_summary(market_records)

    # 4. Fetch & store historical data
    print("\n[4/6] Fetching historical price data...")
    history = fetch_all_history()
    for symbol, rows in history.items():
        save_price_history(symbol, rows)
    trend_summary = build_trend_summary(history)

    # 5. Generate forecasts via OpenRouter
    print("\n[5/6] Generating AI forecasts via OpenRouter...")

    print("  🔮 Geopolitical forecast...")
    geo_forecast = generate_geopolitical_forecast(news_digest, trend_summary)
    save_forecast("geopolitical", geo_forecast)

    print("  📈 Market forecast...")
    mkt_forecast = generate_market_forecast(news_digest, market_summary, trend_summary)
    save_forecast("market", mkt_forecast)

    print("  🇧🇩 Bangladesh/South Asia forecast...")
    bd_forecast = generate_bd_specific_forecast(news_digest, market_summary)
    save_forecast("bangladesh", bd_forecast)

    # 6. Done
    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"\n[6/6] ✅ All done in {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_daily_job()
