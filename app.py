"""
app.py - Flask web application for GeoMarket Intel
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from database import init_db, get_latest_forecasts, get_latest_news, get_latest_market_data, get_price_history
from datetime import datetime
import json

app = Flask(__name__)

@app.before_request
def ensure_db():
    init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/forecasts")
def api_forecasts():
    forecast_type = request.args.get("type", "all")
    forecasts = get_latest_forecasts(limit=50)
    if forecast_type != "all":
        forecasts = [f for f in forecasts if f["forecast_type"] == forecast_type]
    for f in forecasts:
        try:
            f["data"] = json.loads(f["raw_json"])
        except Exception:
            f["data"] = {}
    return jsonify(forecasts)

@app.route("/api/news")
def api_news():
    region = request.args.get("region", None)
    news = get_latest_news(limit=40)
    if region:
        news = [n for n in news if n.get("region") == region]
    return jsonify(news)

@app.route("/api/market")
def api_market():
    data = get_latest_market_data()
    return jsonify(data)

@app.route("/api/history/<symbol>")
def api_history(symbol):
    days = int(request.args.get("days", 90))
    history = get_price_history(symbol, days=days)
    return jsonify(history)

@app.route("/api/worldometer")
def api_worldometer():
    forecasts = get_latest_forecasts(limit=20)
    for f in forecasts:
        if f["forecast_type"] == "worldometer":
            try:
                return jsonify(json.loads(f["raw_json"]))
            except:
                pass
    return jsonify({})

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

@app.route("/api/run-now", methods=["POST"])
def run_now():
    try:
        from scheduler import run_daily_job
        run_daily_job()
        return jsonify({"status": "success", "message": "Forecast job completed."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

application = app  # PythonAnywhere WSGI entry point

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
