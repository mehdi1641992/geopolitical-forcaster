# wsgi.py — PythonAnywhere WSGI configuration
# In PythonAnywhere Web tab, set WSGI config file to point here
# or paste this content into the auto-generated wsgi.py

import sys
import os

# ── Update this path with YOUR PythonAnywhere username ─────────────────────
PROJECT_HOME = '/home/YOURUSERNAME/geopolitical-forecaster'
# ───────────────────────────────────────────────────────────────────────────

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Set environment variables here if not using .env file
os.environ['NEWS_API_KEY']       = 'YOUR_NEWSAPI_KEY_HERE'
os.environ['OPENROUTER_API_KEY'] = 'YOUR_OPENROUTER_KEY_HERE'

from app import application  # noqa: F401
