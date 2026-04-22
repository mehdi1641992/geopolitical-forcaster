"""
scheduler.py - Daily data fetch + forecast generation
"""
import sys, os, time, json
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import init_db, save_news, save_market_data, save_price_history, save_forecast
from fetchers.news import fetch_all_regions, build_news_digest
from fetchers.stocks import (
    fetch_current_prices, fetch_all_history, fetch_commodity_prices,
    build_market_summary, build_trend_summary,
)
from fetchers.worldometer import fetch_all_worldometer, build_worldometer_digest
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
    print("\n[1/7] Initializing database...")
    init_db()

    # 2. Fetch news
    print("\n[2/7] Fetching news headlines (NewsAPI)...")
    region_articles = fetch_all_regions()
    for region, articles in region_articles.items():
        save_news(articles, region=region)
    news_digest = build_news_digest(region_articles)
    total_articles = sum(len(v) for v in region_articles.values())
    print(f"  📰 Total: {total_articles} articles across {len(region_articles)} regions")

    # 3. Scrape Worldometer
    print("\n[3/7] Scraping Worldometer live stats...")
    worldometer_data = fetch_all_worldometer()
    save_forecast("worldometer", worldometer_data)
    worldometer_digest = build_worldometer_digest(worldometer_data)

    # 4. Fetch commodity prices (Alpha Vantage)
    print("\n[4/7] Fetching commodity prices (Alpha Vantage)...")
    real_prices = fetch_commodity_prices()
    save_forecast("real_prices", {"data": real_prices})
    print(f"  💰 Oil: ${real_prices['barrel_price']}/bbl | Gold: ${real_prices['gold_ounce']}/oz")

    # 5. Fetch historical price data (limited to save API calls)
    print("\n[5/7] Fetching historical price data...")
    history = fetch_all_history()
    for symbol, rows in history.items():
        if rows:
            save_price_history(symbol, rows)
    trend_summary = build_trend_summary(history)

    # 6. Generate 5 regional forecasts via AI
    print("\n[6/7] Generating AI forecasts...")

    forecasts = [
        ("global",      "🌍 Global",      lambda: generate_global_forecast(news_digest, worldometer_digest)),
        ("europe",      "🇪🇺 Europe/West", lambda: generate_europe_forecast(news_digest)),
        ("middle_east", "🐪 Middle East",  lambda: generate_middle_east_forecast(news_digest)),
        ("south_asia",  "🌏 South Asia",   lambda: generate_south_asia_forecast(news_digest)),
        ("bangladesh",  "🇧🇩 Bangladesh",  lambda: generate_bd_specific_forecast(news_digest, worldometer_digest)),
    ]

    for ftype, label, fn in forecasts:
        print(f"  {label} forecast...")
        try:
            result = fn()
            save_forecast(ftype, result)
            print(f"    ✅ Saved (confidence: {result.get('confidence','?')}, risk: {result.get('risk_level','?')})")
        except Exception as e:
            print(f"    ⚠️ Failed: {e}")
        time.sleep(3)

    # 7. Done
    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"\n[7/7] ✅ All done in {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_daily_job()
