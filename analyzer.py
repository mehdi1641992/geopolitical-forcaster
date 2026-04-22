"""
analyzer.py - Generate forecasts using Google Gemini
"""
import requests
import os
import json
import re
import time
import datetime
from dotenv import load_dotenv

# Load env vars if running this file directly for testing
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

def call_gemini(prompt: str, system: str = "") -> str:
    """Call Google Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return '{"error": "GEMINI_API_KEY is missing from environment variables."}'

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": f"System: {system}\n\nUser: {prompt}"}]
        }],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 1500,
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Check if the API returned a candidate
        if 'candidates' in data and len(data['candidates']) > 0:
            content = data['candidates'][0]['content']['parts'][0]['text']
            print("  🤖 Model used: gemini-2.5-flash")
            return content
        else:
            print("  ⚠️ Gemini returned empty or blocked response.")
            return '{"error": "Gemini returned empty response"}'
            
    except Exception as e:
        print(f"  ⚠️ Gemini failed: {e}")
        return '{"error": "Gemini API failed"}'

def extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
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
  "title": "Global Geopolitical Risk Forecast — {datetime.date.today()}",
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
    # FIX: Changed from call_openrouter to call_gemini
    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_market_forecast(news_digest: str, market_summary: str, trend_summary: str) -> dict:
    prompt = f"""Analyze this market data and news. Generate a financial forecast focused on what matters for ordinary people — cost of living, savings, and daily expenses.

{market_summary}

{trend_summary}

{news_digest}

Explain gold, oil, and silver prices in terms of what they mean for everyday citizens, not just investors.

Respond ONLY with this JSON — no text before or after:
{{
  "title": "Global Market & Cost-of-Living Forecast — {datetime.date.today()}",
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
    # FIX: Changed from call_openrouter to call_gemini
    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_bd_specific_forecast(news_digest: str, market_summary: str) -> dict:
    prompt = f"""Based on global news and market conditions, generate a detailed economic outlook for Bangladesh and South Asia, written for ordinary Bangladeshi citizens.

{news_digest}

{market_summary}

Be specific about: what global events mean for the cost of daily goods in Bangladesh, electricity and gas prices, job security in the RMG sector, remittance income for families, and BDT purchasing power.

Respond ONLY with this JSON — no text before or after:
{{
  "title": "Bangladesh & South Asia Citizen Economic Outlook — {datetime.date.today()}",
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
    # FIX: Changed from call_openrouter to call_gemini
    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


if __name__ == "__main__":
    test_news = "US-China trade tensions rising. Bangladesh garment exports up 12%. Oil at $85."
    test_market = "SPY: +0.5%. GLD: +1.2%. USO: -0.8%."
    test_trends = "SPY 90d: +8%. GLD 90d: +15%."
    result = generate_geopolitical_forecast(test_news, test_trends)
    print(json.dumps(result, indent=2))
