"""
fetchers/worldometer.py - Scrape live global stats from Worldometer
Scrapes: world population, COVID stats, energy, food, environment counters
"""
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

WORLDOMETER_URLS = {
    "world": "https://www.worldometers.info/",
    "oil": "https://www.worldometers.info/oil/",
    "population": "https://www.worldometers.info/world-population/",
    "food": "https://www.worldometers.info/food/",
    "water": "https://www.worldometers.info/water/",
    "energy": "https://www.worldometers.info/energy/",
    "co2": "https://www.worldometers.info/co2-emissions/",
    "bangladesh": "https://www.worldometers.info/world-population/bangladesh-population/",
}


def scrape_page(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  ⚠️  Worldometer scrape error ({url}): {e}")
        return None


def scrape_world_stats() -> dict:
    """Scrape main Worldometer page for real-time counters."""
    soup = scrape_page(WORLDOMETER_URLS["world"])
    if not soup:
        return {}

    stats = {}
    # Find all counter items on the main page
    for item in soup.select(".counter-item"):
        label_el = item.select_one(".counter-item-label")
        val_el = item.select_one(".counter-number") or item.select_one(".rts-counter")
        if label_el and val_el:
            label = label_el.get_text(strip=True)
            val = val_el.get_text(strip=True).replace(",", "")
            try:
                stats[label] = int(float(val))
            except:
                stats[label] = val

    return stats


def scrape_oil_stats() -> dict:
    """Scrape oil production/consumption data."""
    soup = scrape_page(WORLDOMETER_URLS["oil"])
    if not soup:
        return {}

    data = {}
    # Look for key statistics in tables
    tables = soup.find_all("table")
    for table in tables[:3]:
        rows = table.find_all("tr")
        for row in rows[:5]:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key and val and len(key) < 60:
                    data[key] = val

    # Also grab any highlighted numbers
    for span in soup.select(".counter-number, .rts-counter"):
        parent = span.find_parent(class_=re.compile(r"counter"))
        if parent:
            label = parent.find(class_=re.compile(r"label"))
            if label:
                data[label.get_text(strip=True)] = span.get_text(strip=True)

    return data


def scrape_population_stats() -> dict:
    """Scrape world population data."""
    soup = scrape_page(WORLDOMETER_URLS["population"])
    if not soup:
        return {}

    data = {}
    # Main population counter
    for el in soup.select(".maincounter-number span"):
        val = el.get_text(strip=True).replace(",", "")
        try:
            data["world_population"] = int(val)
            break
        except:
            pass

    return data


def scrape_bangladesh_stats() -> dict:
    """Scrape Bangladesh population stats."""
    soup = scrape_page(WORLDOMETER_URLS["bangladesh"])
    if not soup:
        return {}

    data = {}
    for el in soup.select(".maincounter-number span"):
        val = el.get_text(strip=True).replace(",", "")
        try:
            data["bangladesh_population"] = int(val)
            break
        except:
            pass

    # Find key stats in tables
    for table in soup.find_all("table")[:2]:
        for row in table.find_all("tr")[1:6]:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[-1].get_text(strip=True)
                if key and val and len(key) < 50:
                    data[f"bd_{key[:30]}"] = val

    return data


def fetch_all_worldometer() -> dict:
    """Fetch all Worldometer data — returns structured dict."""
    print("  🌍 Scraping Worldometer...")
    result = {
        "world": scrape_world_stats(),
        "oil": scrape_oil_stats(),
        "population": scrape_population_stats(),
        "bangladesh": scrape_bangladesh_stats(),
        "scraped_at": __import__("datetime").datetime.utcnow().isoformat(),
    }

    total = sum(len(v) for v in result.values() if isinstance(v, dict))
    print(f"  ✅ Worldometer: {total} data points collected")
    return result


def build_worldometer_digest(data: dict) -> str:
    """Convert worldometer data into LLM-readable text."""
    lines = ["=== LIVE GLOBAL STATS (Worldometer) ===\n"]

    if data.get("world"):
        lines.append("--- WORLD COUNTERS ---")
        for k, v in list(data["world"].items())[:15]:
            lines.append(f"  {k}: {v:,}" if isinstance(v, int) else f"  {k}: {v}")

    if data.get("population", {}).get("world_population"):
        pop = data["population"]["world_population"]
        lines.append(f"\n--- POPULATION ---")
        lines.append(f"  World Population: {pop:,}")

    if data.get("bangladesh"):
        lines.append("\n--- BANGLADESH STATS ---")
        for k, v in list(data["bangladesh"].items())[:8]:
            lines.append(f"  {k}: {v}")

    if data.get("oil"):
        lines.append("\n--- OIL DATA ---")
        for k, v in list(data["oil"].items())[:6]:
            lines.append(f"  {k}: {v}")

    return "\n".join(lines)


if __name__ == "__main__":
    import json
    data = fetch_all_worldometer()
    print(json.dumps(data, indent=2, default=str))
