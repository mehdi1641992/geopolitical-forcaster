"""
fetchers/news.py - Fetch news headlines from NewsAPI (free tier: 100 req/day)
"""
import requests, os

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
EVERYTHING_URL = "https://newsapi.org/v2/everything"

REGION_QUERIES = {
    "geopolitics": {
        "q": "war OR conflict OR NATO OR 'Red Sea' OR sanctions OR diplomacy",
        "language": "en",
    },
    "us_europe": {
        "q": "US economy OR stock market OR Fed interest rates OR ECB OR Wall Street",
        "language": "en",
    },
    "commodities": {
        "q": "oil price OR crude oil OR gold price OR silver OR commodity market",
        "language": "en",
    },
    "south_asia": {
        "q": "India economy OR Bangladesh garments OR remittance OR Pakistan economy OR South Asia trade",
        "language": "en",
    },
    "middle_east": {
        "q": "Saudi Arabia OR Iran nuclear OR Israel OR OPEC OR Gulf economy",
        "language": "en",
    },
    "global_markets": {
        "q": "global recession OR inflation OR IMF OR World Bank OR central bank policy",
        "language": "en",
    },
    "crypto": {
        "q": "Bitcoin OR Ethereum OR crypto regulation OR DeFi",
        "language": "en",
    },
}


def fetch_headlines(query_params: dict, max_articles=8) -> list:
    params = {
        "apiKey": NEWS_API_KEY,
        "pageSize": max_articles,
        "sortBy": "publishedAt",
        **query_params,
    }
    try:
        resp = requests.get(EVERYTHING_URL, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        print(f"  📰 [{query_params.get('q','')[:40]}] → {len(articles)} articles")
        return articles
    except Exception as e:
        print(f"  ⚠️  NewsAPI error: {e}")
        return []


def fetch_all_regions() -> dict:
    results = {}
    for region, params in REGION_QUERIES.items():
        results[region] = fetch_headlines(params, max_articles=8)
    return results


def build_news_digest(region_articles: dict) -> str:
    lines = ["=== DAILY NEWS DIGEST ===\n"]
    for region, articles in region_articles.items():
        lines.append(f"\n--- {region.upper().replace('_', ' ')} ---")
        for a in articles:
            title = a.get("title", "")
            source = a.get("source", {}).get("name", "") if isinstance(a.get("source"), dict) else ""
            desc = (a.get("description") or "")[:120]
            if title:
                lines.append(f"• [{source}] {title}")
                if desc:
                    lines.append(f"  {desc}...")
    return "\n".join(lines)
