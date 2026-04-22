"""
fetchers/stocks.py - Fetch market data using Alpha Vantage (free, 25 calls/day)
Replaces yfinance which is blocked on PythonAnywhere free tier.

Free API key: https://www.alphavantage.co/support/#api-key
Free tier: 25 requests/day — we batch smartly to stay within limits.
"""
import requests
import os
from datetime import datetime, timedelta

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "832C3WKGH2HE71QB")
AV_BASE = "https://www.alphavantage.co/query"

WATCHLIST = {
    "US Stocks":        [("SPY","S&P 500 ETF"),("QQQ","NASDAQ ETF"),("DIA","Dow Jones ETF")],
    "Crypto":           [("BTC","Bitcoin"),("ETH","Ethereum")],
    "Commodities":      [("GLD","Gold ETF"),("USO","Oil ETF"),("SLV","Silver ETF")],
    "Asian & Emerging": [("INDA","India ETF"),("EWJ","Japan ETF"),("EEM","Emerging Markets ETF")],
    "Global":           [("TLT","US Treasury ETF")],
}
CRYPTO = {"BTC","ETH"}

def fetch_quote(symbol):
    try:
        r = requests.get(AV_BASE, params={"function":"GLOBAL_QUOTE","symbol":symbol,"apikey":ALPHA_VANTAGE_KEY}, timeout=15)
        q = r.json().get("Global Quote",{})
        if not q.get("05. price"): return None
        return {"price":float(q["05. price"]),"change_pct":float(q["10. change percent"].replace("%","")),"volume":float(q["06. volume"])}
    except Exception as e:
        print(f"  ⚠️  Quote error {symbol}: {e}"); return None

def fetch_crypto_quote(symbol):
    try:
        r = requests.get(AV_BASE, params={"function":"CURRENCY_EXCHANGE_RATE","from_currency":symbol,"to_currency":"USD","apikey":ALPHA_VANTAGE_KEY}, timeout=15)
        info = r.json().get("Realtime Currency Exchange Rate",{})
        if not info: return None
        return {"price":float(info["5. Exchange Rate"]),"change_pct":0.0,"volume":0.0}
    except Exception as e:
        print(f"  ⚠️  Crypto error {symbol}: {e}"); return None

def fetch_daily_history(symbol, days=100):
    try:
        r = requests.get(AV_BASE, params={"function":"TIME_SERIES_DAILY","symbol":symbol,"outputsize":"compact","apikey":ALPHA_VANTAGE_KEY}, timeout=15)
        series = r.json().get("Time Series (Daily)",{})
        rows = [(d,float(v["4. close"]),float(v["5. volume"])) for d,v in sorted(series.items())[-days:]]
        print(f"  📊 {symbol}: {len(rows)} records"); return rows
    except Exception as e:
        print(f"  ⚠️  History error {symbol}: {e}"); return []

def fetch_current_prices():
    records = []
    for category, symbols in WATCHLIST.items():
        for entry in symbols:
            symbol, name = entry[0], entry[1]
            q = fetch_crypto_quote(symbol) if symbol in CRYPTO else fetch_quote(symbol)
            if not q: continue
            records.append({"symbol":symbol,"name":name,"price":q["price"],"change_pct":q["change_pct"],"volume":q["volume"],"category":category})
            arrow = "▲" if q["change_pct"] >= 0 else "▼"
            print(f"  {arrow} {name:30s} ${q['price']:>12,.2f}  ({q['change_pct']:+.2f}%)")
    return records

def fetch_all_history():
    results = {}
    for symbol in ["SPY","GLD","USO","INDA","EEM"]:
        results[symbol] = fetch_daily_history(symbol)
    return results

def build_market_summary(records):
    if not records: return "=== MARKET DATA UNAVAILABLE ==="
    lines = ["=== CURRENT MARKET SNAPSHOT ===\n"]
    cat = None
    for r in records:
        if r["category"] != cat:
            cat = r["category"]; lines.append(f"\n{cat}:")
        arrow = "▲" if r["change_pct"] >= 0 else "▼"
        lines.append(f"  {arrow} {r['name']:30s} ${r['price']:>12,.4f}  ({r['change_pct']:+.2f}%)")
    return "\n".join(lines)

def build_trend_summary(history):
    if not history: return "=== TREND DATA UNAVAILABLE ==="
    lines = ["=== HISTORICAL TREND ANALYSIS ===\n"]
    for symbol, rows in history.items():
        if not rows: continue
        prices = [r[1] for r in sorted(rows)]
        latest = prices[-1]
        p30 = prices[-30] if len(prices)>=30 else prices[0]
        p90 = prices[-90] if len(prices)>=90 else prices[0]
        pct = lambda a,b: ((b-a)/a)*100 if a else 0
        lines.append(f"{symbol:8s}  Now: ${latest:>10,.2f} | 30d: {pct(p30,latest):+.1f}% | 90d: {pct(p90,latest):+.1f}%")
    return "\n".join(lines)
    return "\n".join(lines)


if __name__ == "__main__":
    records = fetch_current_prices()
    print("\n" + build_market_summary(records))
