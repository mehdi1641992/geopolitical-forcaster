"""
scheduler.py - Daily data fetch + forecast generation (No Market Data)
"""
import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from database import init_db, save_news
from fetchers.news import fetch_all_regions, build_news_digest
from analyzer import generate_geopolitical_forecast, generate_bd_specific_forecast
from database import save_forecast

def run_daily_job():
    start = datetime.utcnow()
    print(f"\n{'='*60}")
    print(f"🌍 DAILY FORECAST JOB STARTED — {start.isoformat()}")
    
    print("\n[1/4] Initializing database...")
    init_db()

    print("\n[2/4] Fetching news headlines...")
    region_articles = fetch_all_regions()
    for region, articles in region_articles.items():
        save_news(articles, region=region)
    news_digest = build_news_digest(region_articles)

    print("\n[3/4] Generating AI Action Plans via Gemini...")
    
    print("  🔮 Global Geopolitical Forecast...")
    geo_forecast = generate_geopolitical_forecast(news_digest)
    save_forecast("geopolitical", geo_forecast)

    time.sleep(10) # Safety pause

    print("  🇧🇩 Bangladesh/South Asia Forecast...")
    bd_forecast = generate_bd_specific_forecast(news_digest)
    save_forecast("bangladesh", bd_forecast)

    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"\n[4/4] ✅ All done in {elapsed:.1f}s")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_daily_job()
