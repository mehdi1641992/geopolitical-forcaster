# 🌍 GeoMarket Intel — Daily Geopolitical & Market Forecaster v2

> AI-powered geopolitical and market forecasting dashboard for global citizens — with a dedicated Bangladesh/South Asia lens.  
> Uses **Gemma 3** (local via Ollama) or **Google Gemini** (cloud), **Alpha Vantage**, **NewsAPI**, and **Worldometer scraping**.

---

## What It Does

Every day the app:
1. **Fetches global news** across 7 regions (NewsAPI)
2. **Scrapes Worldometer** for live global stats (population, oil, food, Bangladesh data)
3. **Pulls live market prices** for 10+ assets via Alpha Vantage (SPY, BTC, Gold, Oil ETFs, etc.)
4. **Generates 5 regional AI forecasts** via Gemma 3 (local) or Google Gemini (cloud):
   - 🌍 Global Geopolitical Alert
   - 🇪🇺 Europe & West Alert
   - 🐪 Middle East Alert
   - 🌏 South Asia Alert
   - 🇧🇩 Bangladesh Citizen Alert

---

## Project Structure

```
geomarket/
├── app.py                        # Flask web app + API routes
├── scheduler.py                  # Daily job: fetch → analyze → store
├── analyzer.py                   # AI forecast (Gemma via Ollama / Gemini fallback)
├── database.py                   # SQLite setup and queries
├── wsgi.py                       # PythonAnywhere WSGI config
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for your API keys
├── fetchers/
│   ├── __init__.py
│   ├── news.py                   # NewsAPI fetcher (7 regions)
│   ├── stocks.py                 # Alpha Vantage market data
│   └── worldometer.py            # Web scraper for Worldometer
├── templates/
│   └── index.html                # Dashboard UI (single file)
└── .github/
    └── workflows/
        └── daily.yml             # GitHub Actions daily scheduler
```

---

## API Keys You Need

| Service | URL | Free Tier |
|---|---|---|
| NewsAPI | https://newsapi.org/register | 100 req/day |
| Alpha Vantage | https://www.alphavantage.co/support/#api-key | 25 req/day |
| Google Gemini | https://aistudio.google.com/app/apikey | Free tier available |
| Ollama (local) | https://ollama.com | Free, runs on your machine |

---

## Option A — Deploy on PythonAnywhere (Free Cloud Hosting)

### Step 1 — Register

Sign up at https://www.pythonanywhere.com (free). Your app will be at:
`https://YOUR_USERNAME.pythonanywhere.com`

### Step 2 — Upload Files

In PythonAnywhere Dashboard → Files, create this folder structure:
```
/home/YOUR_USERNAME/geomarket/
/home/YOUR_USERNAME/geomarket/fetchers/
/home/YOUR_USERNAME/geomarket/templates/
/home/YOUR_USERNAME/geomarket/.github/workflows/
```

Upload all files from this project into the matching folders.

### Step 3 — Install Dependencies

Go to Dashboard → Consoles → Bash and run:
```bash
cd ~/geomarket
pip3.10 install --user flask requests python-dotenv beautifulsoup4 lxml
```

### Step 4 — Create Your .env File

In the Bash console:
```bash
cp ~/.../geomarket/.env.example ~/geomarket/.env
nano ~/geomarket/.env
```

Fill in your keys:
```
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_KEY=your_alphavantage_key
GEMINI_API_KEY=your_gemini_key
```

Save with Ctrl+O, exit with Ctrl+X.

### Step 5 — Edit wsgi.py

Open `wsgi.py` and change this line to your username:
```python
PROJECT_HOME = '/home/YOUR_USERNAME/geomarket'
```

### Step 6 — Configure the Web App

1. Dashboard → Web → Add a new web app
2. Choose **Manual configuration** → **Python 3.10**
3. In **Code** section, set:
   - **Source code:** `/home/YOUR_USERNAME/geomarket`
   - **Working directory:** `/home/YOUR_USERNAME/geomarket`
4. Click the **WSGI configuration file** link
5. Delete everything and paste the contents of `wsgi.py`
6. Click **Save** → **Reload**

### Step 7 — Test It

Visit `https://YOUR_USERNAME.pythonanywhere.com` → Click **▶ RUN NOW**

Wait 60–120 seconds. Your dashboard will populate.

### Step 8 — Set Up Daily Scheduler

PythonAnywhere free tier has no cron. Use one of these free options:

**Option A — GitHub Actions (recommended)**

1. Push this repo to GitHub
2. Edit `.github/workflows/daily.yml` — replace `YOUR_USERNAME` with your PythonAnywhere username
3. GitHub will trigger your app every day at 6:30 AM Dhaka time (00:30 UTC)

**Option B — cron-job.org**

1. Sign up at https://cron-job.org (free)
2. Create new job:
   - URL: `https://YOUR_USERNAME.pythonanywhere.com/api/run-now`
   - Method: POST
   - Schedule: Daily, 00:30 UTC

---

## Option B — Run Locally with Gemma 3 (Recommended for Bangladesh / Home Server)

This is the best setup if you want to use the local Gemma 3 model (free, private, no API limits).

### Step 1 — Install Ollama

Download and install Ollama from https://ollama.com

**Windows:**
```
Download and run the installer from ollama.com
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2 — Download Gemma 3

```bash
# Recommended: 12B model (needs ~8GB RAM)
ollama pull gemma3:12b

# If you have more RAM/VRAM:
ollama pull gemma3:27b

# Lightweight option (4GB RAM):
ollama pull gemma3:4b
```

Verify Ollama is running:
```bash
ollama serve         # Start the Ollama server
ollama list          # Should show your model
```

### Step 3 — Clone and Configure

```bash
git clone https://github.com/YOUR_USERNAME/geomarket.git
cd geomarket
```

Create `.env`:
```
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_KEY=your_alphavantage_key

# Enable local Gemma:
USE_LOCAL_AI=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
```

### Step 4 — Install and Run

```bash
pip install flask requests python-dotenv beautifulsoup4 lxml

# Run the web app:
python app.py

# In another terminal, trigger a forecast run:
python scheduler.py
```

Visit: http://localhost:5000

### Step 5 — Daily Schedule (Local)

**Windows Task Scheduler:**
1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily at 6:30 AM
3. Action: Run `python C:\path\to\geomarket\scheduler.py`

**Linux cron:**
```bash
crontab -e
# Add:
30 6 * * * cd /path/to/geomarket && python scheduler.py >> /tmp/geomarket.log 2>&1
```

---

## Customization

**Add more stocks:** Edit `fetchers/stocks.py` → `WATCHLIST` dict

**Add more news regions:** Edit `fetchers/news.py` → `REGION_QUERIES` dict

**Switch AI model:** Edit `.env` — set `OLLAMA_MODEL=gemma3:27b` or change to any Ollama model

**Add more Worldometer pages:** Edit `fetchers/worldometer.py` → `WORLDOMETER_URLS` dict

---

## API Rate Limits

| Service | Free Limit | This App Uses |
|---|---|---|
| NewsAPI | 100 req/day | 7 req/day |
| Alpha Vantage | 25 req/day (5/min) | ~15 req/day |
| Gemini | Free tier rate limits | 5 req/day |
| Ollama (local) | Unlimited | 5 req/day |
| Worldometer | No limit (ethical scraping) | 5 pages/day |

---

## Troubleshooting

**500 error on PythonAnywhere:**
Check Web → Error log. Usually a missing dependency or wrong path in `wsgi.py`.

**"No forecasts" on dashboard:**
Click ▶ RUN NOW. The database is empty until the first run.

**Alpha Vantage rate limit:**
Free tier allows only 5 requests/minute. The app adds `time.sleep(12)` between calls automatically.

**Ollama not responding:**
Make sure Ollama is running: `ollama serve` in a terminal.

**Worldometer scraping blocked:**
Worldometer occasionally blocks scrapers. The scraper will return empty data rather than crash — forecasts will still generate using news data.

---

## License

MIT — free to use, modify, and deploy.
