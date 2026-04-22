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
