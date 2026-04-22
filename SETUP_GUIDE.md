# 🌍 GeoMarket Intel — Complete Setup Guide
# Zero-cost Geopolitical & Market Forecaster on PythonAnywhere

---

## STEP 1 — Get Your Free API Keys

### A. NewsAPI (newsapi.org)
1. Go to: https://newsapi.org/register
2. Sign up with email (free)
3. Copy your API key from the dashboard
4. Free tier: 100 requests/day — more than enough

### B. OpenRouter (openrouter.ai)
1. Go to: https://openrouter.ai/
2. Sign up (free)
3. Go to Keys → Create API Key
4. Free models included: mistral-7b, gemma-3, llama-3.1 (all free with rate limits)
5. No credit card required for free models

---

## STEP 2 — Set Up PythonAnywhere (free tier)

1. Go to: https://www.pythonanywhere.com/registration/register/beginner/
2. Sign up for FREE account (username = your app subdomain)
3. Your app will be at: https://YOURUSERNAME.pythonanywhere.com

---

## STEP 3 — Upload the Project Files

### Option A: Via PythonAnywhere Files Tab (easiest)
1. Go to Dashboard → Files
2. Create folder: /home/YOURUSERNAME/geopolitical-forecaster/
3. Create subfolder: /home/YOURUSERNAME/geopolitical-forecaster/fetchers/
4. Create subfolder: /home/YOURUSERNAME/geopolitical-forecaster/templates/
5. Upload each file into its correct folder

### Option B: Via Bash Console (faster)
1. Go to Dashboard → Consoles → Bash
2. Run:
   ```bash
   mkdir -p ~/geopolitical-forecaster/fetchers
   mkdir -p ~/geopolitical-forecaster/templates
   # Then upload files via Files tab
   ```

---

## STEP 4 — Install Dependencies

1. Go to Dashboard → Consoles → Bash
2. Run:
   ```bash
   cd ~/geopolitical-forecaster
   pip3 install --user flask requests yfinance
   ```
   Wait for installation to complete (~2 min).

---

## STEP 5 — Add Your API Keys

Edit wsgi.py and replace:
- `YOURUSERNAME` → your PythonAnywhere username
- `YOUR_NEWSAPI_KEY_HERE` → your NewsAPI key
- `YOUR_OPENROUTER_KEY_HERE` → your OpenRouter key

---

## STEP 6 — Configure the Web App

1. Go to Dashboard → Web → Add a new web app
2. Choose: Manual configuration
3. Choose: Python 3.10
4. WSGI config file → click the link → paste the contents of wsgi.py
5. Save → Reload

---

## STEP 7 — Set Up Daily Scheduler

1. Go to Dashboard → Tasks
2. Click "Add a new scheduled task"
3. Command: `python3 /home/YOURUSERNAME/geopolitical-forecaster/scheduler.py`
4. Time: 00:30 UTC (runs once daily, midnight UTC = 6:30 AM Dhaka time)
5. Save

---

## STEP 8 — Test It!

1. Visit your app: https://YOURUSERNAME.pythonanywhere.com
2. Click "▶ RUN NOW" button to trigger first forecast immediately
3. Wait ~60-90 seconds for all data to load and AI to generate forecasts
4. Refresh and view your forecasts!

---

## File Structure Reference

```
geopolitical-forecaster/
├── app.py              ← Flask web app
├── scheduler.py        ← Daily job runner
├── analyzer.py         ← OpenRouter LLM calls
├── database.py         ← SQLite storage
├── wsgi.py             ← PythonAnywhere config
├── requirements.txt    ← Dependencies
├── fetchers/
│   ├── __init__.py
│   ├── news.py         ← NewsAPI fetcher
│   └── stocks.py       ← yfinance fetcher
└── templates/
    └── index.html      ← Dashboard UI
```

---

## Free Tier Limits Summary

| Service          | Free Limit              | Our Usage           |
|------------------|-------------------------|---------------------|
| PythonAnywhere   | 1 app, 1 task, 512MB    | Well within limits  |
| NewsAPI          | 100 req/day             | ~5 req/day          |
| OpenRouter       | Free models, rate limits| ~3 req/day          |
| yfinance         | Unlimited               | ~20 symbols/day     |
| SQLite           | Unlimited (local)       | ~10MB/month         |

**Total cost: $0.00/month**

---

## Troubleshooting

**App shows 500 error:**
- Check the error log: Web tab → Log files → Error log
- Make sure all files are uploaded in correct folders
- Verify API keys are set in wsgi.py

**"No forecasts found" message:**
- Click "▶ RUN NOW" to generate first set of forecasts
- Check error log if it fails

**OpenRouter returns error:**
- Verify your API key is correct
- Try a different free model in analyzer.py FREE_MODELS list
- Check https://openrouter.ai/models?q=free for current free models

**NewsAPI returns 426 error:**
- Free tier doesn't support some query types
- The app uses /everything endpoint — make sure key is valid at newsapi.org/account

---

## Customization

**Add more stocks to track:**
Edit fetchers/stocks.py → WATCHLIST dict

**Change forecast regions:**
Edit fetchers/news.py → REGION_QUERIES dict

**Change AI model:**
Edit analyzer.py → FREE_MODELS list (first model = default)

**Add email alerts:**
PythonAnywhere free tier includes email sending — extend scheduler.py to send alerts when risk_level == "critical"
