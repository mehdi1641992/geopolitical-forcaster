"""
fetchers/stocks.py - Fetch market data using yfinance (100% free, no API key)
Covers: S&P 500, Crypto, Commodities, Asian/BD proxy markets
"""
import yfinance as yf
from datetime import datetime, timedelta

# ── Watchlist ──────────────────────────────────────────────────────────────────
WATCHLIST = {
    "US Stocks": [
        ("^GSPC",  "S&P 500"),
        ("^DJI",   "Dow Jones"),
        ("^IXIC",  "NASDAQ"),
        ("^VIX",   "VIX (Fear Index)"),
    ],
    "Crypto": [
        ("BTC-USD", "Bitcoin"),
        ("ETH-USD", "Ethereum"),
    ],
    "Commodities": [
        ("GC=F",   "Gold"),
        ("CL=F",   "Crude Oil (WTI)"),
        ("SI=F",   "Silver"),
        ("NG=F",   "Natural Gas"),
    ],
    "Asian & BD Proxy": [
        ("^NSEI",  "NIFTY 50 (India)"),
        ("^BSESN", "BSE Sensex (India)"),
        ("^N225",  "Nikkei 225 (Japan)"),
        ("^HSI",   "Hang Seng (HK)"),
        ("EWZ",    "iShares Emerging Markets"),
        # Bangladesh's DSE is not on Yahoo Finance; use India as closest proxy
        # DSE30 data available via BD-specific scraping (optional extension)
    ],
    "Global ETFs": [
        ("EEM",    "Emerging Markets ETF"),
        ("USO",    "Oil ETF"),
        ("GLD",    "Gold ETF"),
        ("^TNX",   "US 10Y Treasury Yield"),
    ],
}


def fetch_current_prices() -> list:
    """
    Fetch latest price + 1-day change for all watchlist symbols.
    Returns list of dicts ready for DB storage.
    """
    records = []
    for category, symbols in WATCHLIST.items():
        for symbol, name in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if hist.empty or len(hist) < 1:
                    print(f"  ⚠️  No data for {symbol}")
                    continue

                price = float(hist["Close"].iloc[-1])
                volume = float(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0.0

                if len(hist) >= 2:
                    prev = float(hist["Close"].iloc[-2])
                    change_pct = ((price - prev) / prev) * 100 if prev else 0.0
                else:
                    change_pct = 0.0

                records.append({
                    "symbol": symbol,
                    "name": name,
                    "price": round(price, 4),
                    "change_pct": round(change_pct, 3),
                    "volume": round(volume, 0),
                    "category": category,
                })
                print(f"  ✅ {name:30s} ${price:,.2f}  ({change_pct:+.2f}%)")
            except Exception as e:
                print(f"  ⚠️  Error fetching {symbol}: {e}")
    return records


def fetch_history(symbol: str, days: int = 180) -> list:
    """
    Fetch historical daily close prices for a symbol.
    Returns list of (date_str, close_price, volume).
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")
        rows = []
        for date, row in hist.iterrows():
            date_str = date.strftime("%Y-%m-%d")
            rows.append((date_str, float(row["Close"]), float(row.get("Volume", 0))))
        print(f"  📊 {symbol}: {len(rows)} historical records fetched")
        return rows
    except Exception as e:
        print(f"  ⚠️  History error for {symbol}: {e}")
        return []


def fetch_all_history() -> dict:
    """Fetch 6-month history for key symbols."""
    key_symbols = [
        "^GSPC", "BTC-USD", "GC=F", "CL=F", "^NSEI", "ETH-USD", "^TNX"
    ]
    results = {}
    for symbol in key_symbols:
        results[symbol] = fetch_history(symbol, days=180)
    return results


def build_market_summary(records: list) -> str:
    """Build a readable market summary string for the LLM."""
    lines = ["=== CURRENT MARKET SNAPSHOT ===\n"]
    current_cat = None
    for r in records:
        if r["category"] != current_cat:
            current_cat = r["category"]
            lines.append(f"\n{current_cat}:")
        arrow = "▲" if r["change_pct"] >= 0 else "▼"
        lines.append(
            f"  {arrow} {r['name']:30s} {r['price']:>12,.4f}  ({r['change_pct']:+.2f}%)"
        )
    return "\n".join(lines)


def build_trend_summary(price_history: dict) -> str:
    """Summarize 30/90/180 day trends for the LLM."""
    lines = ["=== HISTORICAL TREND ANALYSIS ===\n"]
    for symbol, rows in price_history.items():
        if not rows:
            continue
        rows_sorted = sorted(rows, key=lambda x: x[0])
        prices = [r[1] for r in rows_sorted]
        if len(prices) < 2:
            continue

        latest = prices[-1]
        p30  = prices[-30]  if len(prices) >= 30  else prices[0]
        p90  = prices[-90]  if len(prices) >= 90  else prices[0]
        p180 = prices[0]

        def pct(a, b): return ((b - a) / a) * 100 if a else 0

        lines.append(
            f"{symbol:12s}  Current: {latest:>12,.2f} | "
            f"30d: {pct(p30, latest):+.1f}% | "
            f"90d: {pct(p90, latest):+.1f}% | "
            f"180d: {pct(p180, latest):+.1f}%"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    records = fetch_current_prices()
    print("\n" + build_market_summary(records))
