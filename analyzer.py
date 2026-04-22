"""
analyzer.py - Generate comprehensive citizen forecasts using Google Gemini
"""
import requests
import os
import json
import re
import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

def call_gemini(prompt: str, system: str = "") -> str:
    """Call Google Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return '{"error": "GEMINI_API_KEY is missing."}'

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": f"System: {system}\n\nUser: {prompt}"}]
        }],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 8000, # FIXED: Increased to prevent Parse Errors
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        if 'candidates' in data and len(data['candidates']) > 0:
            content = data['candidates'][0]['content']['parts'][0]['text']
            print("  🤖 Model used: gemini-2.5-flash")
            return content
        else:
            return '{"error": "Gemini returned empty response"}'
            
    except Exception as e:
        print(f"  ⚠️ Gemini failed: {e}")
        return '{"error": "Gemini API failed"}'

def extract_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"error": "JSON parse failed", "title": "Parse Error", "summary": "The AI generated a response that was too long or invalid."}

SYSTEM_PROMPT = """You are a world-class geopolitical analyst and economic strategist. You write strictly for ordinary citizens. Be highly decisive. Give data-backed instructions on what people should do with their money, what goods they should stock up on, and what they should prepare for. Respond ONLY with a valid JSON object. No markdown. No preamble."""

def generate_geopolitical_forecast(news_digest: str) -> dict:
    prompt = f"""Analyze this news and generate a highly comprehensive risk forecast for ordinary citizens.

{news_digest}

Focus on actionable advice: What should normal people buy, sell, stock up on, or prepare for based on current wars, diplomacy, and inflation?

Respond ONLY with this JSON:
{{
  "title": "Global Geopolitical & Economic Action Plan",
  "summary": "Write a highly comprehensive, 2-to-3 paragraph summary. Use data from the news. Be decisive about the current state of the world and how it is affecting the cost of living.",
  "short_term": ["Next 2 weeks action 1 (e.g. Stock up on X because...)", "Action 2", "Action 3"],
  "medium_term": ["1-3 months action 1 (e.g. Prepare for Y price hikes by...)", "Action 2", "Action 3"],
  "long_term": ["3-12 months action 1 (e.g. Invest in or reallocate budget for...)", "Action 2", "Action 3"],
  "citizen_impact": {{
    "global": "Impact on everyday people globally (fuel, food, inflation)",
    "middle_east": "Impact on Middle Eastern citizens",
    "south_asia": "Impact on South Asian citizens"
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Specific risk 1", "Specific risk 2"]
}}"""
    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)

def generate_bd_specific_forecast(news_digest: str) -> dict:
    prompt = f"""Based on global news, generate a detailed, decisive economic action plan specifically for ordinary citizens in Bangladesh.

{news_digest}

Tell Bangladeshi families exactly what to do regarding food prices, remittances, electricity/gas bills, and gold/savings. 

Respond ONLY with this JSON:
{{
  "title": "Bangladesh Citizen Action Plan",
  "summary": "Write a highly comprehensive, 2-to-3 paragraph summary explaining exactly what the global situation means for the daily life of a Bangladeshi family right now.",
  "short_term": ["Next 2 weeks action 1 (e.g. Buy rice/oil now due to...)", "Action 2", "Action 3"],
  "medium_term": ["1-3 months action 1 (e.g. Handle remittance savings by...)", "Action 2", "Action 3"],
  "long_term": ["3-12 months action 1 (e.g. Prepare for energy costs by...)", "Action 2", "Action 3"],
  "sector_views": {{
    "rmg_exports": "Job security outlook for RMG workers",
    "remittances": "Advice for families relying on remittances",
    "inflation_food": "Specific outlook for rice, onion, and cooking oil prices",
    "energy_gas": "Gas and electricity cost outlook for households"
  }},
  "confidence": "high",
  "risk_level": "high",
  "key_risks": ["Risk 1", "Risk 2"]
}}"""
    raw = call_gemini(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)
