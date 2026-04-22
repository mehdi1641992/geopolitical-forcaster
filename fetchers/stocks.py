"""
fetchers/stocks.py - Market data via Alpha Vantage (free: 25 calls/day)
"""
import requests, os, time

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY")
AV_BASE = "https://www.alphavantage.co/query"

WATCHLIST = {
    "US Stocks":        [("SPY","S&P 500 ETF"), ("QQQ","NASDAQ ETF"), ("DIA","Dow Jones ETF")],
    "Crypto":           [("BTC","Bitcoin"), ("ETH","Ethereum")],
    "Commodities":      [("GLD","Gold ETF"), ("USO","Oil ETF"), ("SLV","Silver ETF")],
    "Asian & Emerging": [("INDA","India ETF"), ("EWJ","Japan ETF"), ("EEM","Emerging Markets ETF")],
    "Global":           [("TLT","US 20Y Treasury ETF")],
}
CRYPTO = {"BTC", "ETH"}


def fetch_quote(symbol):
    try:
        r = requests.get(AV_BASE, params={
            "function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_VANTAGE_KEY,
        }, timeout=15)
        r.raise_for_status()
        q = r.json().get("Global Quote", {})
        if not q or not q.get("05. price"):
            print(f"  ⚠️  No data for {symbol}")
            return None
        return {
            "price":      float(q["05. price"]),
            "change_pct": float(q["10. change percent"].replace("%", "")),
            "volume":     float(q.get("06. volume", 0)),
        }
    except Exception as e:
        print(f"  ⚠️  Quote error {symbol}: {e}")
        return None


def fetch_crypto_quote(symbol):
    try:
        r = requests.get(AV_BASE, params={
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol, "to_currency": "USD",
            "apikey": ALPHA_VANTAGE_KEY,
        }, timeout=15)
        info = r.json().get("Realtime Currency Exchange Rate", {})
        if not info:
            return None
        return {"price": float(info["5. Exchange Rate"]), "change_pct": 0.0, "volume": 0.0}
    except Exception as e:
        print(f"  ⚠️  Crypto error {symbol}: {e}")
        return None


def fetch_daily_history(symbol, days=100):
    try:
        r = requests.get(AV_BASE, params={
            "function": "TIME_SERIES_DAILY", "symbol": symbol,
            "outputsize": "compact", "apikey": ALPHA_VANTAGE_KEY,
        }, timeout=15)
        series = r.json().get("Time Series (Daily)", {})
        if not series:
            print(f"  ⚠️  No history for {symbol}")
            return []
        rows = [(d, float(v["4. close"]), float(v["5. volume"]))
                for d, v in sorted(series.items())[-days:]]
        print(f"  📊 {symbol}: {len(rows)} records")
        return rows
    except Exception as e:
        print(f"  ⚠️  History error {symbol}: {e}")
        return []


def fetch_commodity_prices():
    """Fetch WTI oil and gold via Alpha Vantage commodity endpoints."""
    data = {}
    try:
        r = requests.get(f"{AV_BASE}?function=WTI&interval=daily&apikey={ALPHA_VANTAGE_KEY}", timeout=10)
        oil_val = r.json().get("data", [{}])[0].get("value", "80.00")
        data["barrel_price"] = round(float(oil_val), 2)
        data["gallon_price"] = round((float(oil_val) / 42) * 1.8, 2)
    except Exception as e:
        print(f"  ⚠️ Oil price error: {e}")
        data["barrel_price"] = 80.00
        data["gallon_price"] = 3.45

    try:
        r = requests.get(f"{AV_BASE}?function=GOLD&interval=daily&apikey={ALPHA_VANTAGE_KEY}", timeout=10)
        gold_val = r.json().get("data", [{}])[0].get("value", "2300.00")
        data["gold_ounce"] = round(float(gold_val), 2)
    except Exception as e:
        print(f"  ⚠️ Gold price error: {e}")
        data["gold_ounce"] = 2300.00

    return data


def fetch_current_prices():
    records = []
    count = 0
    for category, symbols in WATCHLIST.items():
        for symbol, name in symbols:
            if count >= 20:   # Stay within daily API limit
                break
            q = fetch_crypto_quote(symbol) if symbol in CRYPTO else fetch_quote(symbol)
            if not q:
                continue
            records.append({
                "symbol": symbol, "name": name,
                "price": q["price"], "change_pct": q["change_pct"],
                "volume": q["volume"], "category": category,
            })
            arrow = "▲" if q["change_pct"] >= 0 else "▼"
            print(f"  {arrow} {name:30s} ${q['price']:>12,.2f}  ({q['change_pct']:+.2f}%)")
            count += 1
            time.sleep(12)  # Alpha Vantage free: ~5 calls/min
    return records


def fetch_all_history():
    results = {}
    # Only fetch history for key symbols to save API calls
    for symbol in ["SPY", "GLD", "USO"]:
        results[symbol] = fetch_daily_history(symbol)
        time.sleep(12)
    return results


def build_market_summary(records) -> str:
    if not records:
        return "=== MARKET DATA UNAVAILABLE ==="
    lines = ["=== CURRENT MARKET PRICES ===\n"]
    by_cat = {}
    for r in records:
        by_cat.setdefault(r["category"], []).append(r)
    for cat, items in by_cat.items():
        lines.append(f"\n--- {cat.upper()} ---")
        for r in items:
            arrow = "▲" if r["change_pct"] >= 0 else "▼"
            lines.append(f"  {arrow} {r['name']:28s} ${r['price']:>10,.2f} ({r['change_pct']:+.2f}%)")
    return "\n".join(lines)


def build_trend_summary(history) -> str:
    if not any(history.values()):
        return "=== TREND DATA UNAVAILABLE ==="
    lines = ["=== HISTORICAL TREND ANALYSIS ===\n"]
    for symbol, rows in history.items():
        if not rows:
            continue
        prices = [r[1] for r in sorted(rows)]
        latest = prices[-1]
        p30 = prices[-30] if len(prices) >= 30 else prices[0]
        p90 = prices[-90] if len(prices) >= 90 else prices[0]
        pct = lambda a, b: ((b - a) / a) * 100 if a else 0
        lines.append(
            f"{symbol:8s}  Now: ${latest:>10,.2f} | 30d: {pct(p30, latest):+.1f}% | 90d: {pct(p90, latest):+.1f}%"
        )
    return "\n".join(lines)
