# wsgi.py — PythonAnywhere WSGI configuration
import sys, os
from dotenv import load_dotenv

# ── UPDATE THIS with your PythonAnywhere username ───────────────────────────
PROJECT_HOME = '/home/YOUR_USERNAME/geomarket'
# ───────────────────────────────────────────────────────────────────────────

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Load environment variables from .env file
load_dotenv(os.path.join(PROJECT_HOME, '.env'))

from app import application  # noqa: F401
