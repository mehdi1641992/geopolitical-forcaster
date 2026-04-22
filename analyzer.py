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
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]


def call_openrouter(prompt: str, system: str = None, model: str = None) -> str:
    """
    Call OpenRouter API. Falls back through free models if one fails.
    Returns the response text.
    """
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
                "X-Title": "Geopolitical & Market Forecaster",
            }

            payload = {
                "model": m,
                "messages": messages,
                "max_tokens": 1200,
                "temperature": 0.5,
            }

            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            print(f"  🤖 Model used: {m} | Tokens: {data.get('usage', {})}")
            return content

        except Exception as e:
            print(f"  ⚠️  Model {m} failed: {e}. Trying next...")

    return '{"error": "All models failed. Check your OpenRouter API key and quota."}'


def extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = re.sub(r"```json|```", "", text).strip()
    # Find the first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"error": "Could not parse JSON", "raw": text[:500]}


SYSTEM_PROMPT = """You are a world-class geopolitical analyst and financial forecaster with expertise in:
- Global macroeconomics and monetary policy
- South Asian economies (Bangladesh, India, Pakistan)
- Middle East geopolitics and oil markets
- Cryptocurrency and digital assets
- Equity markets (S&P 500, Asian markets)

You always respond in valid JSON only. No markdown, no preamble. Just the JSON object."""


def generate_geopolitical_forecast(news_digest: str, trend_summary: str) -> dict:
    """Generate a geopolitical risk forecast."""
    prompt = f"""Based on the following news and market data, generate a geopolitical risk forecast.

{news_digest}

{trend_summary}

Respond ONLY with this exact JSON structure:
{{
  "title": "Geopolitical Risk Forecast — [today's date]",
  "summary": "2-3 sentence executive summary of the current geopolitical situation",
  "short_term": "Next 1-2 weeks outlook: key risks and events to watch",
  "medium_term": "Next 1-3 months: structural trends and geopolitical shifts",
  "long_term": "3-12 month outlook: major geopolitical forces at play",
  "hotspots": ["region1: brief note", "region2: brief note", "region3: brief note"],
  "confidence": "low|medium|high",
  "risk_level": "low|medium|high|critical",
  "key_risks": ["risk 1", "risk 2", "risk 3"],
  "opportunities": ["opportunity 1", "opportunity 2"]
}}"""

    raw = call_openrouter(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_market_forecast(news_digest: str, market_summary: str, trend_summary: str) -> dict:
    """Generate a stock/crypto/commodity market forecast."""
    prompt = f"""Based on the following market data, historical trends, and news, generate a financial market forecast.

{market_summary}

{trend_summary}

{news_digest}

Respond ONLY with this exact JSON structure:
{{
  "title": "Market Forecast — [today's date]",
  "summary": "2-3 sentence executive summary of current market conditions",
  "short_term": "Next 1-2 weeks: price action, key support/resistance, catalysts",
  "medium_term": "Next 1-3 months: macro trends, sector rotation, risks",
  "long_term": "3-12 month outlook: structural market forces",
  "asset_views": {{
    "sp500": "bullish|bearish|neutral — brief reason",
    "bitcoin": "bullish|bearish|neutral — brief reason",
    "gold": "bullish|bearish|neutral — brief reason",
    "oil": "bullish|bearish|neutral — brief reason",
    "emerging_markets": "bullish|bearish|neutral — brief reason",
    "bangladesh_india": "brief comment on South Asian market outlook"
  }},
  "confidence": "low|medium|high",
  "risk_level": "low|medium|high|critical",
  "key_risks": ["risk 1", "risk 2", "risk 3"],
  "watch_list": ["catalyst 1 to watch", "catalyst 2 to watch", "catalyst 3 to watch"]
}}"""

    raw = call_openrouter(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


def generate_bd_specific_forecast(news_digest: str, market_summary: str) -> dict:
    """Generate a Bangladesh & South Asia specific economic outlook."""
    prompt = f"""Based on the following global news and market data, generate an economic outlook specifically for Bangladesh and South Asia.

{news_digest}

{market_summary}

Consider: remittance flows, garment exports (RMG sector), Indian rupee impact on BDT, regional trade, political stability, IMF/World Bank programs, energy costs.

Respond ONLY with this exact JSON structure:
{{
  "title": "Bangladesh & South Asia Economic Outlook",
  "summary": "2-3 sentence overview of Bangladesh economic situation in global context",
  "short_term": "Near-term outlook for BDT, remittances, exports, inflation",
  "medium_term": "1-3 month view: trade flows, regional dynamics, policy risks",
  "long_term": "Structural outlook: growth prospects, risks, opportunities",
  "sector_views": {{
    "rmg_exports": "brief outlook for garment sector",
    "remittances": "brief outlook for remittance flows",
    "currency_bdt": "BDT stability outlook",
    "inflation": "inflation trajectory outlook",
    "energy": "energy cost and supply outlook"
  }},
  "confidence": "low|medium|high",
  "risk_level": "low|medium|high|critical",
  "key_risks": ["risk 1", "risk 2", "risk 3"],
  "opportunities": ["opportunity 1", "opportunity 2"]
}}"""

    raw = call_openrouter(prompt, system=SYSTEM_PROMPT)
    return extract_json(raw)


if __name__ == "__main__":
    # Quick test
    test_news = "Test: US-China trade tensions rising. Bangladesh garment exports up 12%."
    test_market = "S&P 500: +0.5%. Bitcoin: -2.1%. Gold: +0.8%."
    test_trends = "S&P500 180d: +15%. BTC 180d: -8%. Gold 180d: +12%."

    result = generate_geopolitical_forecast(test_news, test_trends)
    print(json.dumps(result, indent=2))
