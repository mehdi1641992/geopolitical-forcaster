"""
scheduler.py - Daily data fetch + forecast generation (Gemini version)
"""
import sys
import os
import time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import init_db, save_news, save_market_data, save_price_history, save_forecast
from fetchers.news import fetch_all_regions, build_news_digest
from fetchers.stocks import fetch_current_prices, fetch_all_history, build_market_summary, build_trend_summary
from analyzer import (
    generate_global_forecast,
    generate_europe_forecast,
    generate_middle_east_forecast,
    generate_south_asia_forecast,
    generate_bd_specific_forecast,
)


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
    if market_records:
        save_market_data(market_records)
    market_summary = build_market_summary(market_records)

    # 4. Fetch & store historical data
    print("\n[4/6] Fetching historical price data...")
    history = fetch_all_history()
    for symbol, rows in history.items():
        if rows:
            save_price_history(symbol, rows)
    trend_summary = build_trend_summary(history)

    # 5. Generate 5 regional forecasts via Gemini
    print("\n[5/6] Generating AI forecasts via Google Gemini...")

    print("  🌍 Global forecast...")
    global_forecast = generate_global_forecast(news_digest)
    save_forecast("global", global_forecast)
    time.sleep(3)

    print("  🇪🇺 Europe/West forecast...")
    europe_forecast = generate_europe_forecast(news_digest)
    save_forecast("europe", europe_forecast)
    time.sleep(3)

    print("  🐪 Middle East forecast...")
    me_forecast = generate_middle_east_forecast(news_digest)
    save_forecast("middle_east", me_forecast)
    time.sleep(3)

    print("  🌏 South Asia forecast...")
    sa_forecast = generate_south_asia_forecast(news_digest)
    save_forecast("south_asia", sa_forecast)
    time.sleep(3)

    print("  🇧🇩 Bangladesh forecast...")
    bd_forecast = generate_bd_specific_forecast(news_digest)
    save_forecast("bangladesh", bd_forecast)

    # 6. Done
    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"\n[6/6] ✅ All done in {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_daily_job()
