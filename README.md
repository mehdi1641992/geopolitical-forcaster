# 🌍 GeoMarket Intel — Daily Geopolitical & Market Forecaster

> A zero-cost AI-powered forecasting dashboard that monitors global news daily and generates geopolitical risk assessments and financial market outlooks — with a dedicated South Asia / Bangladesh lens.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Cost](https://img.shields.io/badge/Hosting%20Cost-%240%2Fmonth-brightgreen?style=flat-square)

---

## 📸 What It Does

Every day the app automatically:

1. **Fetches global news** across 5 regions (US/Europe, South Asia, Middle East, Global Markets, Crypto) via NewsAPI
2. **Pulls live market prices** for 20+ assets — S&P 500, Bitcoin, Ethereum, Gold, Oil, NIFTY 50, Hang Seng, and more — via yfinance (no API key needed)
3. **Stores 6 months of historical price data** in a local SQLite database for trend analysis
4. **Generates 3 AI forecasts** via OpenRouter (free LLM models):
   - 🌐 Geopolitical Risk Forecast
   - 📈 Market Outlook (with per-asset signals)
   - 🇧🇩 Bangladesh & South Asia Economic Outlook

All results are displayed on a live dark-themed dashboard at your PythonAnywhere URL.

---

## 🛠️ Tech Stack

| Layer | Tool | Cost |
|---|---|---|
| Hosting | PythonAnywhere (free tier) | $0 |
| AI / LLM | OpenRouter — Mistral, Gemma, Llama (free models) | $0 |
| News | NewsAPI.org (free tier, 100 req/day) | $0 |
| Market Data | yfinance (Yahoo Finance, unlimited) | $0 |
| Database | SQLite (built into Python) | $0 |
| Scheduler | GitHub Actions or cron-job.org | $0 |
| Backend | Flask | $0 |
| Frontend | Vanilla HTML/CSS/JS | $0 |
| **Total** | | **$0/month** |

---

## 📁 Project Structure

```
geopolitical-forecaster/
├── app.py                  # Flask web app + API routes
├── scheduler.py            # Daily job: fetch → analyze → store
├── analyzer.py             # OpenRouter LLM forecast generation
├── database.py             # SQLite setup and queries
├── wsgi.py                 # PythonAnywhere WSGI config
├── requirements.txt        # Python dependencies
├── fetchers/
│   ├── __init__.py
│   ├── news.py             # NewsAPI fetcher (5 regions)
│   └── stocks.py           # yfinance fetcher (20+ assets)
├── templates/
│   └── index.html          # Dashboard UI
└── .github/
    └── workflows/
        └── daily.yml       # GitHub Actions daily trigger
```

---

## 🚀 Deployment Guide

### Prerequisites — Get Your Free API Keys

#### NewsAPI
1. Register at [newsapi.org/register](https://newsapi.org/register)
2. Copy your API key from the dashboard
3. Free tier: 100 requests/day (app uses ~5/day)

#### OpenRouter
1. Sign up at [openrouter.ai](https://openrouter.ai)
2. Go to **Keys → Create API Key**
3. Free models available: Mistral 7B, Gemma 3 27B, Llama 3.1 8B
4. No credit card required for free models

---

### Step 1 — PythonAnywhere Setup

1. Register at [pythonanywhere.com](https://www.pythonanywhere.com/registration/register/beginner/) (free)
2. Your app will be hosted at `https://YOURUSERNAME.pythonanywhere.com`

### Step 2 — Upload Files

In PythonAnywhere **Dashboard → Files**, create this folder structure:
```
/home/YOURUSERNAME/geopolitical-forecaster/
/home/YOURUSERNAME/geopolitical-forecaster/fetchers/
/home/YOURUSERNAME/geopolitical-forecaster/templates/
```
Upload each file from this repo into its matching folder.

### Step 3 — Install Dependencies

Go to **Dashboard → Consoles → Bash** and run:
```bash
python3.10 -m pip install --user flask requests yfinance
```

### Step 4 — Add Your API Keys

Open `wsgi.py` and update these three lines:
```python
PROJECT_HOME = '/home/YOURUSERNAME/geopolitical-forecaster'
os.environ['NEWS_API_KEY']       = 'YOUR_NEWSAPI_KEY_HERE'
os.environ['OPENROUTER_API_KEY'] = 'YOUR_OPENROUTER_KEY_HERE'
```

### Step 5 — Configure the Web App

1. Go to **Dashboard → Web → Add a new web app**
2. Choose **Manual configuration** → **Python 3.10**
3. Click the WSGI config file link → paste the contents of `wsgi.py`
4. Click **Save** → **Reload**

### Step 6 — Set Up the Daily Scheduler

> PythonAnywhere free tier does not support scheduled tasks, so use one of these free alternatives:

#### Option A — GitHub Actions (recommended)

Push this repo to GitHub. The file `.github/workflows/daily.yml` is already included. Just update the URL inside it:
```yaml
curl -X POST https://YOURUSERNAME.pythonanywhere.com/api/run-now
```
GitHub will trigger your app every day at 00:30 UTC (6:30 AM Dhaka time). Uses ~2 min/day of your free 2,000 min/month quota.

#### Option B — cron-job.org (no GitHub needed)

1. Sign up at [cron-job.org](https://cron-job.org) (free)
2. Create a new cronjob:
   - **URL:** `https://YOURUSERNAME.pythonanywhere.com/api/run-now`
   - **Method:** POST
   - **Schedule:** Daily, 00:30 UTC
3. Save

### Step 7 — First Run

1. Visit `https://YOURUSERNAME.pythonanywhere.com`
2. Click **▶ RUN NOW** to generate your first forecasts immediately
3. Wait ~60–90 seconds for data fetch + AI generation
4. Your dashboard will populate with live forecasts

---

## 📊 Dashboard Features

- **Forecasts tab** — Browse all AI-generated forecasts, filterable by type (Geopolitical / Market / Bangladesh). Each card shows short, medium, and long-term outlooks, risk level, confidence score, key risks, and opportunities.
- **Markets tab** — Live prices and 24h change for all tracked assets, grouped by category.
- **News Feed tab** — Latest headlines by region with source attribution.
- **▶ RUN NOW button** — Manually trigger a full data refresh and new forecast at any time.

---

## 🌐 Tracked Assets

**US Markets:** S&P 500, Dow Jones, NASDAQ, VIX

**Crypto:** Bitcoin (BTC), Ethereum (ETH)

**Commodities:** Gold, Crude Oil (WTI), Silver, Natural Gas

**Asian Markets:** NIFTY 50, BSE Sensex, Nikkei 225, Hang Seng

**Global ETFs:** Emerging Markets ETF, Oil ETF, Gold ETF, US 10Y Treasury Yield

---

## 🌏 News Regions Monitored

| Region | Focus |
|---|---|
| US & Europe | Economy, equities, policy, geopolitics |
| South Asia | India, Bangladesh, Pakistan — trade, economy |
| Middle East | Oil, conflicts, Saudi Arabia, Iran, Israel |
| Global Markets | Fed, IMF, World Bank, inflation, recession |
| Crypto | Bitcoin, Ethereum, digital asset regulation |

---

## 🇧🇩 Bangladesh-Specific Outlook

Every daily run includes a dedicated Bangladesh & South Asia forecast covering:
- RMG (garment) export sector trends
- Remittance flow outlook
- BDT currency stability
- Inflation trajectory
- Energy supply and cost outlook
- Regional trade dynamics (India, China)

---

## ⚙️ Customization

**Add more stocks:** Edit `fetchers/stocks.py` → `WATCHLIST` dict

**Add more news regions:** Edit `fetchers/news.py` → `REGION_QUERIES` dict

**Change AI model:** Edit `analyzer.py` → `FREE_MODELS` list. Find current free models at [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free)

**Change scheduler time:** Edit `.github/workflows/daily.yml` → `cron` expression

---

## 🔒 Free Tier Limits

| Service | Free Limit | This App Uses |
|---|---|---|
| PythonAnywhere | 1 web app, 512MB storage | Well within limits |
| NewsAPI | 100 requests/day | ~5 requests/day |
| OpenRouter | Free model rate limits | ~3 requests/day |
| yfinance | Unlimited | ~20 symbols/day |
| GitHub Actions | 2,000 min/month | ~2 min/day (~60/month) |
| SQLite | Unlimited (local file) | ~10MB/month growth |

---

## 🐛 Troubleshooting

**500 error on the web app:**
Check **Web tab → Log files → Error log** in PythonAnywhere. Usually a missing dependency or wrong path in `wsgi.py`.

**"No forecasts found" on dashboard:**
Click **▶ RUN NOW**. The database is empty until the first run completes.

**OpenRouter returns an error:**
Verify your API key at [openrouter.ai](https://openrouter.ai). Check that a free model is listed in `FREE_MODELS` in `analyzer.py` — free model availability can change. Current list: [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free)

**NewsAPI 426 or 401 error:**
Double-check your key is correct in `wsgi.py`. Confirm it's active at [newsapi.org/account](https://newsapi.org/account).

**GitHub Actions not triggering:**
GitHub sometimes delays scheduled workflows by up to 1 hour on free accounts. You can also trigger it manually from **Actions tab → Daily Forecast Trigger → Run workflow**.

---

## 📄 License

MIT — free to use, modify, and deploy.

---

*Built with Flask · yfinance · NewsAPI · OpenRouter · PythonAnywhere · GitHub Actions*
