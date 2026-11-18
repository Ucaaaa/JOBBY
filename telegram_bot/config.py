
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "backend"))

load_dotenv(ROOT / ".env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TZ = os.getenv("BOT_TIMEZONE", "Asia/Jakarta")