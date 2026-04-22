"""
app.py - Flask web application for the Geopolitical & Market Forecaster
Deploy on PythonAnywhere as a WSGI web app.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from database import (
    init_db, get_latest_forecasts, get_latest_news,
    get_latest_market_data, get_price_history
)
from datetime import datetime

app = Flask(__name__)


@app.before_request
def ensure_db():
    init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/forecasts")
def api_forecasts():
    forecast_type = request.args.get("type")
    # Increased limit to 50 so old broken records don't push new ones out of view
    forecasts = get_latest_forecasts(limit=50)

    if forecast_type and forecast_type != "all":
        forecasts = [f for f in forecasts if f["forecast_type"] == forecast_type]

    import json
    for f in forecasts:
        try:
            f["data"] = json.loads(f["raw_json"])
        except Exception:
            f["data"] = {}
    return jsonify(forecasts)


@app.route("/api/market")
def api_market():
    data = get_latest_market_data()
    return jsonify(data)


@app.route("/api/news")
def api_news():
    news = get_latest_news(limit=30)
    return jsonify(news)


@app.route("/api/history/<symbol>")
def api_history(symbol):
    days = int(request.args.get("days", 90))
    history = get_price_history(symbol, days=days)
    return jsonify(history)


@app.route("/api/run-now", methods=["POST"])
def run_now():
    """Manually trigger a forecast run (useful for testing)."""
    try:
        from scheduler import run_daily_job
        run_daily_job()
        return jsonify({"status": "success", "message": "Forecast job completed."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/status")
def api_status():
    forecasts = get_latest_forecasts(limit=1)
    market = get_latest_market_data()
    last_run = forecasts[0]["created_at"] if forecasts else "Never"
    return jsonify({
        "last_run": last_run,
        "forecasts_count": len(get_latest_forecasts(limit=100)),
        "market_assets": len(market),
        "server_time": datetime.utcnow().isoformat(),
    })


# ── PythonAnywhere WSGI entry point ──────────────────────────────────────────
application = app  # PythonAnywhere looks for 'application'

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
