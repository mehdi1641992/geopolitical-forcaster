"""
fetchers/news.py - Fetch news headlines from NewsAPI (free tier)
"""
import requests
import os

# Pulled safely from .env via wsgi.py or scheduler.py
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
EVERYTHING_URL = "https://newsapi.org/v2/everything"

REGION_QUERIES = {
    "geopolitics": {
        "q": "war OR conflict OR NATO OR 'Red Sea' OR 'diplomacy shift'",
        "language": "en",
    }, # <-- Fixed missing comma
    "us_europe": {
        "q": "US economy OR stock market OR geopolitics OR NATO OR Fed interest rates",
        "language": "en",
    },
    "commodities": {
        "q": "oil price OR gas price OR 'gold reserves' OR 'silver price'",
        "language": "en",
    },
    "south_asia": {
        "q": "India OR Bangladesh economy OR 'remittance' OR 'garments export' OR Pakistan OR South Asia economy",
        "language": "en",
    },
    "middle_east": {
        "q": "Middle East OR Saudi Arabia OR Iran OR Israel OR oil",
        "language": "en",
    },
    "global_markets": {
        "q": "global economy OR recession OR inflation OR Federal Reserve OR IMF OR World Bank OR 'central bank'",
        "language": "en",
    },
    "crypto": {
        "q": "Bitcoin OR Ethereum OR cryptocurrency",
        "language": "en",
    },
}

def fetch_headlines(query_params: dict, max_articles=10) -> list:
    """Fetch headlines from NewsAPI /everything endpoint."""
    params = {
        "apiKey": NEWS_API_KEY,
        "pageSize": max_articles,
        "sortBy": "publishedAt",
        **query_params,
    }
    try:
        resp = requests.get(EVERYTHING_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        print(f"  📰 Fetched {len(articles)} articles for: {query_params.get('q', '')[:40]}...")
        return articles
    except Exception as e:
        print(f"  ⚠️ NewsAPI error: {e}")
        return []

def fetch_all_regions() -> dict:
    """Fetch news for all configured regions."""
    results = {}
    for region, params in REGION_QUERIES.items():
        articles = fetch_headlines(params, max_articles=8)
        results[region] = articles
    return results

def build_news_digest(region_articles: dict) -> str:
    """Combine all news into a readable text digest for the LLM."""
    lines = ["=== DAILY NEWS DIGEST ===\n"]
    for region, articles in region_articles.items():
        lines.append(f"\n--- {region.upper().replace('_', ' ')} ---")
        for a in articles:
            title = a.get("title", "")
            source = a.get("source", {}).get("name", "")
            desc = a.get("description", "") or ""
            if title:
                lines.append(f"• [{source}] {title}")
                if desc:
                    lines.append(f"  {desc[:120]}...")
    return "\n".join(lines)

if __name__ == "__main__":
    data = fetch_all_regions()
    digest = build_news_digest(data)
    print(digest)
