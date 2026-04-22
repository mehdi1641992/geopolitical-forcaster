"""
analyzer.py - Generate forecasts using OpenRouter (free LLM models)
Uses free models: mistralai/mistral-7b-instruct, google/gemma-3-27b-it:free, etc.
"""
import requests
import os
import json
import re

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY_HERE")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Best free models on OpenRouter (as of 2025) — ranked by quality
FREE_MODELS = [
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-4-maverick:free",
    "meta-llama/llama-4-scout:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "microsoft/phi-4-reasoning-plus:free",
    "qwen/qwen3-14b:free",
    "tngtech/deepseek-r1t-chimera:free",
]


def call_openrouter(prompt: str, system: str = None, model: str = None) -> str:
    models_to_try = [model] + FREE_MODELS if model else FREE_MODELS
    for m in models_to_try:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://geopolitical-forecaster.pythonanywhere.com",
                "X-Title": "GeoMarket Intel Forecaster",
            }
            payload = {
                "model": m,
                "messages": messages,
                "max_tokens": 1800,
                "temperature": 0.4,
            }
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
            if resp.status_code == 429:
                print(f"  ⏳ Rate limited on {m}, waiting 8s...")
                time.sleep(8)
                resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            print(f"  🤖 Model: {m} | Tokens: {data.get('usage', {}).get('total_tokens','?')}")
            return content
        except Exception as e:
            print(f"  ⚠️  Model {m} failed: {e}. Trying next...")
    return '{"error": "All models failed.", "summary": "AI unavailable — check OpenRouter key and model list.", "short_term": "N/A", "medium_term": "N/A", "long_term": "N/A", "confidence": "low", "risk_level": "medium", "title": "Forecast Unavailable"}'


def extract_json(text: str) -> dict:
    # Strip <think>...</think> blocks from reasoning models
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"error": "JSON parse failed", "raw": text[:300], "summary": text[:200],
            "short_term": "Parse error", "medium_term": "Parse error", "long_term": "Parse error",
            "confidence": "low", "risk_level": "medium", "title": "Parse Error"}


SYSTEM_PROMPT = """You are a world-class geopolitical analyst and financial forecaster. You write for a general audience — ordinary citizens, not just investors. You explain what events mean for the cost of everyday life: food, fuel, electricity, rent. You respond ONLY with a valid JSON object. No markdown. No explanation. No preamble. Start your response with { and end with }."""


def generate_geopolitical_forecast(news_digest: str, trend_summary: str) -> dict:
    prompt = f"""Analyze this news and generate a geopolitical risk forecast for ordinary citizens worldwide.

{news_digest}

{trend_summary}

Focus on: wars, diplomacy shifts, sanctions, trade disputes, energy supply disruptions, food security, political instability.
Explain how each risk affects the daily life cost for average people globally.

Respond ONLY with this JSON — no text before or after:
{{
  "title": "Global Geopolitical Risk Forecast — {__import__('datetime').date.today()}",
  "summary": "3-4 sentence plain-language summary of the biggest geopolitical forces at play right now and what they mean for ordinary people",
  "short_term": "Next 2 weeks: specific events, summits, elections, or conflicts to watch. What could change prices of food/fuel?",
  "medium_term": "1-3 months: evolving diplomatic situations, supply chain risks, sanctions impacts on everyday costs",
  "long_term": "3-12 months: structural shifts in global order, alliances, trade routes, energy transition impacts",
  "hotspots": [
    "Region — what is happening and why citizens should care",
    "Region — what is happening and why citizens should care",
    "Region — what is happening and why citizens should care",
    "Region — what is happening and why citizens should care"
  ],
  "citizen_impact": {{
    "global": "How current geopolitics affects everyday people globally — fuel, food, inflation",
    "middle_east": "Impact on Middle Eastern citizens — oil revenues, subsidies, conflict risk, cost of living",
    "south_asia": "Impact on South Asian citizens — remittances, food prices, energy costs, trade",
    "bangladesh": "Specific impact on Bangladeshi citizens — BDT value, import costs, export demand, energy"
  }},
  "diplomacy_watch": ["Diplomatic situation 1 to monitor", "Diplomatic situation 2", "Diplomatic situation 3"],
  "confidence": "medium",
  "risk_level": "high",
  "key_risks": ["Risk 1 with citizen impact", "Risk 2 with citizen impact", "Risk 3 with citizen impact"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    raw = call_openrouter(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_market_forecast(news_digest: str, market_summary: str, trend_summary: str) -> dict:
    prompt = f"""Analyze this market data and news. Generate a financial forecast focused on what matters for ordinary people — cost of living, savings, and daily expenses.

{market_summary}

{trend_summary}

{news_digest}

Explain gold, oil, and silver prices in terms of what they mean for everyday citizens, not just investors.

Respond ONLY with this JSON — no text before or after:
{{
  "title": "Global Market & Cost-of-Living Forecast — {__import__('datetime').date.today()}",
  "summary": "3-4 sentence plain-language summary: what markets are doing and what it means for your wallet",
  "short_term": "Next 2 weeks: expected moves in oil, gold, food commodity prices and their citizen impact",
  "medium_term": "1-3 months: inflation trajectory, interest rate expectations, currency pressures on imports",
  "long_term": "3-12 months: structural commodity trends, energy transition, food security outlook",
  "asset_views": {{
    "sp500": "bullish|bearish|neutral — what this means for pension funds and global confidence",
    "bitcoin": "bullish|bearish|neutral — brief reason",
    "gold": "bullish|bearish|neutral — what rising/falling gold means for central banks and savings",
    "oil": "bullish|bearish|neutral — direct impact on fuel and transport costs for citizens",
    "silver": "bullish|bearish|neutral — industrial demand signal",
    "emerging_markets": "bullish|bearish|neutral — impact on developing nation currencies and imports",
    "bangladesh_india": "Specific outlook for South Asian markets and BDT/INR currency impact on import costs"
  }},
  "commodities_citizen_impact": {{
    "oil_and_fuel": "Current oil trend and what it means for petrol/diesel prices and electricity bills",
    "gold": "Gold price trend and what it signals for inflation and currency stability",
    "silver": "Silver trend — industrial signal for electronics and solar energy costs",
    "food_commodities": "Wheat, rice, palm oil trends and food price outlook for households"
  }},
  "gold_reserves_context": "Brief note on major central bank gold buying/selling trends and what it signals for the global monetary system",
  "confidence": "medium",
  "risk_level": "medium",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "watch_list": ["Catalyst 1 to watch this week", "Catalyst 2", "Catalyst 3"]
}}"""
    raw = call_openrouter(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_bd_specific_forecast(news_digest: str, market_summary: str) -> dict:
    prompt = f"""Based on global news and market conditions, generate a detailed economic outlook for Bangladesh and South Asia, written for ordinary Bangladeshi citizens.

{news_digest}

{market_summary}

Be specific about: what global events mean for the cost of daily goods in Bangladesh, electricity and gas prices, job security in the RMG sector, remittance income for families, and BDT purchasing power.

Respond ONLY with this JSON — no text before or after:
{{
  "title": "Bangladesh & South Asia Citizen Economic Outlook — {__import__('datetime').date.today()}",
  "summary": "3-4 sentences: what is happening in the global economy right now and what Bangladeshi families should know about its impact on their daily lives",
  "short_term": "Next 2 weeks: expected changes in import costs, fuel prices, and remittance rates for Bangladeshi families",
  "medium_term": "1-3 months: RMG export demand outlook, BDT pressure, inflation trajectory, energy costs",
  "long_term": "3-12 months: structural trends — trade shifts, climate impact on agriculture, regional geopolitics affecting BD",
  "sector_views": {{
    "rmg_exports": "Garment sector outlook — US/EU buyer demand, order pipeline, worker income security",
    "remittances": "Remittance flow outlook — Middle East and US economic conditions affecting diaspora earnings",
    "currency_bdt": "BDT vs USD outlook — import cost implications for fuel, medicine, electronics",
    "inflation_food": "Food price outlook — rice, onion, cooking oil, based on global commodity trends",
    "energy_gas": "Gas and electricity cost outlook for households and factories",
    "agriculture": "Agricultural outlook — monsoon risks, fertilizer costs, food self-sufficiency"
  }},
  "citizen_alerts": [
    "⚠️ Alert 1: specific actionable warning for Bangladeshi households",
    "⚠️ Alert 2: specific actionable warning",
    "✅ Positive signal 1 for Bangladeshi economy"
  ],
  "regional_context": {{
    "india": "How India economic conditions spill over into Bangladesh",
    "pakistan": "Pakistan situation and regional stability note",
    "middle_east": "Gulf state conditions affecting BD remittances and oil import costs"
  }},
  "confidence": "medium",
  "risk_level": "medium",
  "key_risks": ["Risk 1 with household impact", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
    raw = call_openrouter(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


if __name__ == "__main__":
    test_news = "US-China trade tensions rising. Bangladesh garment exports up 12%. Oil at $85."
    test_market = "SPY: +0.5%. GLD: +1.2%. USO: -0.8%."
    test_trends = "SPY 90d: +8%. GLD 90d: +15%."
    result = generate_geopolitical_forecast(test_news, test_trends)
    print(json.dumps(result, indent=2))
