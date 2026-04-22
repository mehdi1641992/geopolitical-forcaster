"""
analyzer.py - Generate highly decisive regional forecasts using Google Gemini
"""
import requests
import os
import json
import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

def call_gemini(prompt: str, system: str = "") -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": f"System: {system}\n\nUser: {prompt}"}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text']
        return '{"error": "Gemini returned empty response"}'
    except Exception as e:
        print(f"  ⚠️ Gemini failed: {e}")
        return '{"error": "Gemini API failed"}'

def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        return {"error": "JSON parse failed", "title": "Parse Error", "summary": "Failed to parse API response."}

SYSTEM_PROMPT = """You are a highly decisive, data-driven geopolitical analyst. You write for ordinary citizens in specific regions, providing comprehensive, actionable advice. Tell them exactly what to expect, what to stock, what to avoid, and how to prepare. Respond ONLY in valid JSON."""

# --- THE 5 REGIONAL PROMPTS ---

def generate_global_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze global news and generate an actionable geopolitical risk forecast for the World.
{news_digest}
JSON Schema Requirement:
{{
  "title": "🌍 Global Geopolitical Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed summary of the biggest global shifts (trade, war, inflation) and the threat/opportunity they present.",
  "short_term": "Next 2 weeks: Immediate global supply chain or price shocks to brace for.",
  "medium_term": "1-3 months: Where ordinary citizens globally should invest savings or brace for inflation.",
  "long_term": "3-12 months: Structural shifts in global order and energy.",
  "action_plan": {{
    "what_to_stock": "Specific global commodities (e.g., rice, gold) facing supply risks.",
    "what_to_avoid": "Specific assets or purchases to hold off on globally.",
    "energy_strategy": "Global advice on handling upcoming fuel costs."
  }},
  "confidence": "high", "risk_level": "critical", "key_risks": ["Risk 1", "Risk 2"], "opportunities": ["Opportunity 1"]
}}"""
    return extract_json(call_gemini(prompt, system=SYSTEM_PROMPT))

def generate_europe_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze news for Europe/US and generate an actionable economic forecast for European/Western citizens.
{news_digest}
JSON Schema Requirement:
{{
  "title": "🇪🇺 Europe & West Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed summary of European/US economic shifts, energy policies, and inflation.",
  "short_term": "Next 2 weeks: Immediate actions regarding heating/energy bills or grocery costs.",
  "medium_term": "1-3 months: Financial moves for EUR/USD stability and household budgets.",
  "long_term": "3-12 months: Job market and industrial shifts.",
  "action_plan": {{
    "what_to_stock": "Specific goods to secure in Europe/US.",
    "what_to_avoid": "Major purchases to delay.",
    "energy_strategy": "Actionable advice on winter heating, electricity, and fuel."
  }},
  "confidence": "high", "risk_level": "high", "key_risks": ["Risk 1", "Risk 2"], "opportunities": ["Opportunity 1"]
}}"""
    return extract_json(call_gemini(prompt, system=SYSTEM_PROMPT))

def generate_middle_east_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze Middle East news and generate an actionable economic/safety forecast for citizens living in the Middle East.
{news_digest}
JSON Schema Requirement:
{{
  "title": "🐪 Middle East Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed summary of oil revenues, conflict risks, and local inflation impacts.",
  "short_term": "Next 2 weeks: Immediate actions regarding travel, currency exchange, or supply stocking.",
  "medium_term": "1-3 months: Financial moves regarding real estate, gold, and savings.",
  "long_term": "3-12 months: Structural changes to subsidies and job markets.",
  "action_plan": {{
    "what_to_stock": "Specific local goods or stable currencies to hold.",
    "what_to_avoid": "Investments or regions to avoid.",
    "energy_strategy": "Fuel and local utility cost advice."
  }},
  "confidence": "high", "risk_level": "high", "key_risks": ["Risk 1", "Risk 2"], "opportunities": ["Opportunity 1"]
}}"""
    return extract_json(call_gemini(prompt, system=SYSTEM_PROMPT))

def generate_south_asia_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze South Asia news (India, Pakistan, Sri Lanka) and generate an actionable forecast for regional citizens.
{news_digest}
JSON Schema Requirement:
{{
  "title": "🌏 South Asia Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed summary of regional inflation, INR stability, and agricultural risks.",
  "short_term": "Next 2 weeks: Immediate commodity/food price hikes to beat.",
  "medium_term": "1-3 months: Job security, cross-border trade impacts, and remittance advice.",
  "long_term": "3-12 months: Climate and agricultural outlooks affecting daily food costs.",
  "action_plan": {{
    "what_to_stock": "Specific agricultural goods (e.g., wheat, cooking oil) to buy now.",
    "what_to_avoid": "Specific local assets to avoid.",
    "energy_strategy": "Actionable advice on handling regional power grid issues/costs."
  }},
  "confidence": "high", "risk_level": "high", "key_risks": ["Risk 1", "Risk 2"], "opportunities": ["Opportunity 1"]
}}"""
    return extract_json(call_gemini(prompt, system=SYSTEM_PROMPT))

def generate_bd_specific_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze news and generate an actionable, highly decisive economic outlook for citizens in Bangladesh.
{news_digest}
JSON Schema Requirement:
{{
  "title": "🇧🇩 Bangladesh Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed, data-backed summary of how global events hit the BD economy and BDT purchasing power.",
  "short_term": "Next 2 weeks: Immediate actions for BD citizens (groceries, remittances).",
  "medium_term": "1-3 months: Financial moves for savings and gold.",
  "long_term": "3-12 months: Career security in RMG/Tech.",
  "action_plan": {{
    "what_to_stock": "Specific items (e.g., onion, rice, soybean oil) to stock up on.",
    "remittance_advice": "When expats should send money given BDT trajectory.",
    "investment_moves": "Where local citizens should keep their money (land, gold)."
  }},
  "confidence": "high", "risk_level": "high", "key_risks": ["Risk 1", "Risk 2"], "opportunities": ["Opportunity 1"]
}}"""
    return extract_json(call_gemini(prompt, system=SYSTEM_PROMPT))