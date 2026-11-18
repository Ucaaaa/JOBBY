
"""Entry point Telegram Bot JOBBY."""

import logging
import sys
from pathlib import Path

# Menentukan lokasi folder proyek.
TELEGRAM_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TELEGRAM_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Memastikan modul backend dan telegram_bot dapat ditemukan.
for path in (str(BACKEND_DIR), str(TELEGRAM_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import config

from flask import Flask
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app import create_app
from handlers import commands as c
from scheduler.jobs import tick
from services import data


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def create_backend_app():
    """Membuat Flask app agar bot memakai database JOBBY yang sama."""
    backend_app = create_app()
    data.set_app(backend_app)
    return backend_app


def build_telegram_app():
    """Membangun Telegram application dan mendaftarkan handler."""

    if not config.TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN belum diisi di file .env. "
            "Periksa konfigurasi Telegram JOBBY."
        )

    telegram_app = (
        Application.builder()
        .token(config.TOKEN)
        .build()
    )

    command_handlers = [
        ("start", c.start),
        ("help", c.help_),
        ("summary", c.summary),
        ("applications", c.applications),
        ("status", c.status),
        ("upcoming", c.upcoming),
        ("reminders", c.reminders),
        ("update", c.update_cmd),
        ("followup", c.followup),
        ("settings", c.settings),
        ("disconnect", c.disconnect),
    ]

    for command, callback in command_handlers:
        telegram_app.add_handler(
            CommandHandler(command, callback)
        )

    telegram_app.add_handler(
        CallbackQueryHandler(c.callback)
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            c.text
        )
    )

    # Memeriksa pengingat setiap 60 detik.
    if telegram_app.job_queue is None:
        raise RuntimeError(
            "JobQueue tidak tersedia. "
            "Pastikan python-telegram-bot[job-queue] sudah terinstal."
        )

    telegram_app.job_queue.run_repeating(
        tick,
        interval=60,
        first=10
    )

    return telegram_app


def main():
    """Menjalankan backend context dan Telegram bot."""

    if not config.TOKEN:
        sys.exit(
            "TELEGRAM_BOT_TOKEN belum diisi di .env "
            "(lihat docs/TELEGRAM_SETUP.md)."
        )

    try:
        create_backend_app()
        telegram_app = build_telegram_app()

        logger.info("JOBBY Telegram Assistant sedang dijalankan.")

        telegram_app.run_polling()

    except KeyboardInterrupt:
        logger.info("JOBBY Telegram Assistant dihentikan.")

    except Exception:
        logger.exception(
            "Terjadi kesalahan saat menjalankan JOBBY Telegram Assistant."
        )
        raise


if __name__ == "__main__":
    main()