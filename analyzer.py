"""
analyzer.py - AI forecast generation
  Priority 1: Local Gemma via Ollama (your machine / local server)
  Priority 2: Google Gemini API (cloud fallback)
"""
import requests, os, json, re, datetime

# ── Model configuration ─────────────────────────────────────────────────────
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")
OLLAMA_MODEL    = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
USE_LOCAL_AI    = os.environ.get("USE_LOCAL_AI", "false").lower() == "true"

# ── LOCAL: Ollama / Gemma ────────────────────────────────────────────────────
def call_ollama(prompt: str, system: str = "") -> str:
    """Call local Ollama server running Gemma via ngrok tunnel."""
    if not OLLAMA_BASE_URL:
        return None

    try:
        # Standardize URL and add required ngrok bypass header
        url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        headers = {
            "ngrok-skip-browser-warning": "true",
            "Content-Type": "application/json"
        }

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": f"System: {system}\n\nUser: {prompt}" if system else prompt,
            "stream": False,
            "format": "json", # Forces gemma to output valid JSON
            "options": {"temperature": 0.3, "num_predict": 2048},
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()

        text = resp.json().get("response", "")
        print(f"  🤖 Ollama/{OLLAMA_MODEL} | {len(text)} chars")
        return text

    except Exception as e:
        print(f"  ⚠️ Ollama failed: {e} — falling back to Gemini")
        return None

# ── CLOUD: Google Gemini ─────────────────────────────────────────────────────
def call_gemini(prompt: str, system: str = "") -> str:
    if not GEMINI_API_KEY:
        return '{"error": "GEMINI_API_KEY not set"}'
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
        "generationConfig": {
            "temperature": 0.35, "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
        },
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"  🤖 Gemini Flash | {len(text)} chars")
        return text
    except Exception as e:
        print(f"  ⚠️ Gemini failed: {e}")
        return f'{{"error": "Gemini API failed: {str(e)}"}}'

# ── Router ───────────────────────────────────────────────────────────────────
def call_ai(prompt: str, system: str = "") -> str:
    """Gateway: Tries local Gemma first, falls back to Gemini."""
    if USE_LOCAL_AI:
        result = call_ollama(prompt, system)
        if result: return result
    return call_gemini(prompt, system)

def extract_json(text: str) -> dict:
    text = re.sub(r"
http://googleusercontent.com/immersive_entry_chip/0


# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM = """You are a highly decisive, data-driven geopolitical and economic analyst.
You write for ordinary citizens in specific regions, providing comprehensive, actionable advice.
Tell them exactly what to expect, what to prepare, and how to act.
Respond ONLY in valid JSON format with no markdown, no preamble, no code fences."""

TODAY = datetime.date.today().strftime("%b %d, %Y")


# ── The 5 Regional Forecast Functions ───────────────────────────────────────

def generate_global_forecast(news_digest: str, worldometer: str = "") -> dict:
    prompt = f"""Analyze global news and Worldometer data. Generate an actionable geopolitical risk forecast for the WORLD.

{news_digest}

{worldometer}

Return ONLY this JSON (no markdown):
{{
  "title": "🌍 Global Alert — {TODAY}",
  "summary": "3-4 sentence data-backed summary of the biggest global shifts and their impact on ordinary people.",
  "short_term": "Next 2 weeks: Immediate global supply/price shocks to brace for.",
  "medium_term": "1-3 months: Where ordinary people should adjust finances.",
  "long_term": "3-12 months: Structural shifts in global order, energy, and food security.",
  "action_plan": {{
    "what_to_stock": "Specific commodities facing supply risks.",
    "what_to_avoid": "Assets or purchases to hold off on.",
    "energy_strategy": "Global advice on fuel/electricity costs."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1 with citizen impact", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    return extract_json(call_ai(prompt, SYSTEM))


def generate_europe_forecast(news_digest: str, worldometer: str = "") -> dict:
    prompt = f"""Analyze news for Europe/US. Generate actionable economic forecast for European/Western citizens.

{news_digest}

Return ONLY this JSON (no markdown):
{{
  "title": "🇪🇺 Europe & West Alert — {TODAY}",
  "summary": "3-4 sentence summary of European/US economic shifts, energy, and inflation impact on daily life.",
  "short_term": "Next 2 weeks: Immediate actions for energy bills or grocery costs.",
  "medium_term": "1-3 months: Financial moves for EUR/USD stability.",
  "long_term": "3-12 months: Job market and industrial shifts.",
  "action_plan": {{
    "what_to_stock": "Specific goods to secure before price hikes.",
    "what_to_avoid": "Major purchases to delay.",
    "energy_strategy": "Actionable advice on heating, electricity, fuel management."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    return extract_json(call_ai(prompt, SYSTEM))


def generate_middle_east_forecast(news_digest: str, worldometer: str = "") -> dict:
    prompt = f"""Analyze Middle East news. Generate actionable forecast for Middle Eastern citizens.

{news_digest}

Return ONLY this JSON (no markdown):
{{
  "title": "🐪 Middle East Alert — {TODAY}",
  "summary": "3-4 sentence summary of oil revenues, conflict risks, and inflation on Middle Eastern households.",
  "short_term": "Next 2 weeks: Immediate travel, currency, or supply actions.",
  "medium_term": "1-3 months: Real estate, gold, and savings security moves.",
  "long_term": "3-12 months: Structural changes to subsidies, job markets, regional stability.",
  "action_plan": {{
    "what_to_stock": "Local goods or stable currencies to hold.",
    "what_to_avoid": "Investments or regions to avoid given tensions.",
    "energy_strategy": "Fuel and utility cost advice for Middle Eastern families."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    return extract_json(call_ai(prompt, SYSTEM))


def generate_south_asia_forecast(news_digest: str, worldometer: str = "") -> dict:
    prompt = f"""Analyze South Asia news (India, Pakistan, Sri Lanka). Generate actionable forecast for regional citizens.

{news_digest}

Return ONLY this JSON (no markdown):
{{
  "title": "🌏 South Asia Alert — {TODAY}",
  "summary": "3-4 sentence summary of regional inflation, INR/PKR stability, agricultural risks on South Asian households.",
  "short_term": "Next 2 weeks: Immediate commodity/food price hikes to prepare for.",
  "medium_term": "1-3 months: Job security, cross-border trade impacts, and remittance advice.",
  "long_term": "3-12 months: Climate and agricultural outlooks affecting food costs.",
  "action_plan": {{
    "what_to_stock": "Specific agricultural goods (wheat, oil, lentils) to buy now.",
    "what_to_avoid": "Local assets to avoid given currency pressures.",
    "energy_strategy": "Advice on handling regional power grid issues and rising electricity."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    return extract_json(call_ai(prompt, SYSTEM))


def generate_bd_specific_forecast(news_digest: str, worldometer: str = "") -> dict:
    prompt = f"""Analyze news and generate a highly decisive, actionable economic outlook for citizens in Bangladesh.

{news_digest}

{worldometer}

Return ONLY this JSON (no markdown):
{{
  "title": "🇧🇩 Bangladesh Citizen Alert — {TODAY}",
  "summary": "3-4 sentence data-backed summary: how global events hit the BD economy, BDT purchasing power, and household budgets.",
  "short_term": "Next 2 weeks: Immediate actions for BD citizens (groceries to stock, remittance timing, currency moves).",
  "medium_term": "1-3 months: Financial moves for savings, gold purchases, and RMG sector job security.",
  "long_term": "3-12 months: Career security in RMG/Tech, BDT trajectory, inflation outlook.",
  "action_plan": {{
    "what_to_stock": "Specific items Bangladeshi families should stock now (onion, rice, soybean oil, lentils).",
    "remittance_advice": "When expats should send money given BDT exchange rate trajectory.",
    "investment_moves": "Where citizens should keep money (land, gold, bank deposits, USD)."
  }},
  "citizen_alerts": [
    "⚠️ Specific warning 1 for Bangladeshi households",
    "⚠️ Specific warning 2",
    "✅ Positive signal for Bangladesh economy"
  ],
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1 with household impact", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    return extract_json(call_ai(prompt, SYSTEM))
