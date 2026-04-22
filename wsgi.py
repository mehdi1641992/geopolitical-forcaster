# wsgi.py — PythonAnywhere WSGI configuration
# In PythonAnywhere Web tab, set WSGI config file to point here
# or paste this content into the auto-generated wsgi.py

import sys
import os

# ── Update this path with YOUR PythonAnywhere username ─────────────────────
PROJECT_HOME = '/home/datacodex/geopolitical-forecaster'
# ───────────────────────────────────────────────────────────────────────────

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Set environment variables here if not using .env file
os.environ['NEWS_API_KEY']       = 'cd24517469524b30acdccd9f3946c76f'
os.environ['OPENROUTER_API_KEY'] = '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'

from app import application  # noqa: F401
