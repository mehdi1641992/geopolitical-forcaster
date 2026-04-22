"""
scheduler.py - Daily data fetch + forecast generation
"""
import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from database import init_db, save_news, save_forecast
from fetchers.news import fetch_all_regions, build_news_digest
from analyzer import (
    generate_global_forecast, generate_europe_forecast, 
    generate_middle_east_forecast, generate_south_asia_forecast, 
    generate_bd_specific_forecast
)

def run_daily_job():
    start = datetime.utcnow()
    init_db()

    print("\n[1/3] Fetching news headlines...")
    region_articles = fetch_all_regions()
    for region, articles in region_articles.items():
        save_news(articles, region=region)
    news_digest = build_news_digest(region_articles)

    print("\n[2/3] Generating Actionable AI Forecasts (15s cooldowns)...")
    
    print("  🌍 Global Action Plan...")
    save_forecast("global", generate_global_forecast(news_digest))
    time.sleep(15)

    print("  🇪🇺 Europe Action Plan...")
    save_forecast("europe", generate_europe_forecast(news_digest))
    time.sleep(15)

    print("  🐪 Middle East Action Plan...")
    save_forecast("middle_east", generate_middle_east_forecast(news_digest))
    time.sleep(15)

    print("  🌏 South Asia Action Plan...")
    save_forecast("south_asia", generate_south_asia_forecast(news_digest))
    time.sleep(15)

    print("  🇧🇩 Bangladesh Action Plan...")
    save_forecast("bangladesh", generate_bd_specific_forecast(news_digest))

    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"\n[3/3] ✅ All done in {elapsed:.1f}s")

if __name__ == "__main__":
    run_daily_job()