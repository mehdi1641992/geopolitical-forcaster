"""
analyzer.py - Generate highly decisive regional forecasts using Google Gemini
"""
import requests
import os
import json
import re
import datetime

def call_gemini(prompt: str, system: str = "") -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return '{"error": "GEMINI_API_KEY not set", "title": "API Error", "summary": "Missing API key"}'

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
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
            text = data['candidates'][0]['content']['parts'][0]['text']
            print(f"  🤖 Gemini 2.0 Flash | Response length: {len(text)} chars")
            return text

        return '{"error": "Gemini returned empty response", "title": "API Error", "summary": "Empty response from Gemini"}'

    except Exception as e:
        print(f"  ⚠️ Gemini failed: {e}")
        return f'{{"error": "Gemini API failed: {str(e)}", "title": "API Error", "summary": "API call failed"}}'


def extract_json(text: str) -> dict:
    try:
        # Strip markdown code fences if present
        text = re.sub(r'```json\s*|\s*```', '', text).strip()

        # Try direct parse first
        return json.loads(text)

    except json.JSONDecodeError:
        # Fallback: find first { ... } block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        # Last resort: return safe default
        return {
            "error": "JSON parse failed",
            "title": "Parse Error",
            "summary": "Failed to parse API response. Check Gemini API key and quota.",
            "short_term": "N/A",
            "medium_term": "N/A",
            "long_term": "N/A",
            "confidence": "low",
            "risk_level": "medium",
            "key_risks": ["API parsing error"],
            "opportunities": []
        }


SYSTEM_PROMPT = """You are a highly decisive, data-driven geopolitical analyst. You write for ordinary citizens in specific regions, providing comprehensive, actionable advice. Tell them exactly what to expect, what to stock, what to avoid, and how to prepare. Respond ONLY in valid JSON format with no markdown."""


# --- THE 5 REGIONAL FORECAST FUNCTIONS ---

def generate_global_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze global news and generate an actionable geopolitical risk forecast for the World.

{news_digest}

Respond with ONLY this JSON structure (no markdown, no extra text):
{{
  "title": "🌍 Global Geopolitical Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed 3-4 sentence summary of the biggest global shifts (trade, war, inflation) and the threat/opportunity they present to ordinary people.",
  "short_term": "Next 2 weeks: Immediate global supply chain or price shocks citizens should brace for.",
  "medium_term": "1-3 months: Where ordinary citizens globally should adjust savings or brace for inflation.",
  "long_term": "3-12 months: Structural shifts in global order, energy, and food security.",
  "action_plan": {{
    "what_to_stock": "Specific global commodities (e.g., rice, gold) facing supply risks.",
    "what_to_avoid": "Specific assets or purchases to hold off on globally.",
    "energy_strategy": "Global advice on handling upcoming fuel costs."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1 with citizen impact", "Risk 2 with citizen impact", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""

    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_europe_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze news for Europe/US and generate an actionable economic forecast for European/Western citizens.

{news_digest}

Respond with ONLY this JSON structure (no markdown):
{{
  "title": "🇪🇺 Europe & West Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed 3-4 sentence summary of European/US economic shifts, energy policies, and inflation impacts on daily life.",
  "short_term": "Next 2 weeks: Immediate actions regarding heating/energy bills or grocery costs.",
  "medium_term": "1-3 months: Financial moves for EUR/USD stability and household budgets.",
  "long_term": "3-12 months: Job market and industrial shifts affecting Western citizens.",
  "action_plan": {{
    "what_to_stock": "Specific goods to secure in Europe/US before price hikes.",
    "what_to_avoid": "Major purchases to delay due to upcoming shifts.",
    "energy_strategy": "Actionable advice on winter heating, electricity, and fuel management."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""

    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_middle_east_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze Middle East news and generate an actionable economic/safety forecast for citizens living in the Middle East.

{news_digest}

Respond with ONLY this JSON structure (no markdown):
{{
  "title": "🐪 Middle East Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed 3-4 sentence summary of oil revenues, conflict risks, and local inflation impacts on Middle Eastern households.",
  "short_term": "Next 2 weeks: Immediate actions regarding travel, currency exchange, or supply stocking.",
  "medium_term": "1-3 months: Financial moves regarding real estate, gold, and savings security.",
  "long_term": "3-12 months: Structural changes to subsidies, job markets, and regional stability.",
  "action_plan": {{
    "what_to_stock": "Specific local goods or stable currencies to hold.",
    "what_to_avoid": "Investments or regions to avoid given current tensions.",
    "energy_strategy": "Fuel and local utility cost advice for Middle Eastern families."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""

    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_south_asia_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze South Asia news (India, Pakistan, Sri Lanka) and generate an actionable forecast for regional citizens.

{news_digest}

Respond with ONLY this JSON structure (no markdown):
{{
  "title": "🌏 South Asia Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed 3-4 sentence summary of regional inflation, INR stability, and agricultural risks affecting South Asian households.",
  "short_term": "Next 2 weeks: Immediate commodity/food price hikes to prepare for.",
  "medium_term": "1-3 months: Job security outlook, cross-border trade impacts, and remittance advice.",
  "long_term": "3-12 months: Climate and agricultural outlooks affecting daily food costs and availability.",
  "action_plan": {{
    "what_to_stock": "Specific agricultural goods (e.g., wheat, cooking oil, lentils) to buy now.",
    "what_to_avoid": "Specific local assets to avoid given currency pressures.",
    "energy_strategy": "Actionable advice on handling regional power grid issues and rising electricity costs."
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""

    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_bd_specific_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze news and generate an actionable, highly decisive economic outlook for citizens in Bangladesh.

{news_digest}

Respond with ONLY this JSON structure (no markdown):
{{
  "title": "🇧🇩 Bangladesh Citizen Alert — {datetime.date.today().strftime('%b %d, %Y')}",
  "summary": "Detailed 3-4 sentence, data-backed summary of how global events hit the BD economy, BDT purchasing power, and household budgets.",
  "short_term": "Next 2 weeks: Immediate actions for BD citizens (groceries to stock, remittance timing, currency moves).",
  "medium_term": "1-3 months: Financial moves for savings, gold purchases, and RMG sector job security.",
  "long_term": "3-12 months: Career security in RMG/Tech sectors, BDT trajectory, inflation outlook.",
  "action_plan": {{
    "what_to_stock": "Specific items Bangladeshi families should stock up on now (e.g., onion, rice, soybean oil, lentils).",
    "remittance_advice": "When expats should send money given BDT exchange rate trajectory.",
    "investment_moves": "Where local citizens should keep their money (land, gold, bank deposits, USD)."
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

    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


# Compatibility aliases for the scheduler
def generate_geopolitical_forecast(news_digest: str, trend_summary: str = "") -> dict:
    """Alias for global forecast to match scheduler expectations."""
    return generate_global_forecast(news_digest)


def generate_market_forecast(news_digest: str, market_summary: str = "", trend_summary: str = "") -> dict:
    """Alias for Europe forecast to match scheduler expectations."""
    return generate_europe_forecast(news_digest)


if __name__ == "__main__":
    test_news = "Test: US-China trade tensions rising. Bangladesh garment exports up 12%. Oil at $85."
    result = generate_bd_specific_forecast(test_news)
    print(json.dumps(result, indent=2))
