# wsgi.py — PythonAnywhere WSGI configuration

import sys
import os
from dotenv import load_dotenv

# ── Update this path with YOUR PythonAnywhere username ─────────────────────
PROJECT_HOME = '/home/datacodex/geopolitical-forecaster'
# ───────────────────────────────────────────────────────────────────────────

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Load environment variables from the .env file
load_dotenv(os.path.join(PROJECT_HOME, '.env'))

from app import application  # noqa: F401