import secrets
from datetime import datetime, timedelta
from .models import db, TelegramAccount, TelegramLinkCode


def new_link_code(user_id, minutes=10):
    TelegramLinkCode.query.filter_by(user_id=user_id, used=False).update({"used": True})
    code = secrets.token_hex(3).upper()
    db.session.add(TelegramLinkCode(user_id=user_id, code=code, expires_at=datetime.utcnow() + timedelta(minutes=minutes)))
    db.session.commit()
    return code


def consume_link_code(code, telegram_user_id):
    """Dipakai Telegram Bot. Return (ok, message)."""
    lc = TelegramLinkCode.query.filter_by(code=(code or "").strip().upper(), used=False).first()
    if not lc or lc.expires_at < datetime.utcnow(): return False, "Kode tidak valid atau kedaluwarsa"
    if TelegramAccount.query.filter_by(telegram_user_id=telegram_user_id).first():
        return False, "Akun Telegram ini sudah terhubung"
    TelegramAccount.query.filter_by(user_id=lc.user_id).delete()
    db.session.add(TelegramAccount(user_id=lc.user_id, telegram_user_id=telegram_user_id))
    lc.used = True
    db.session.commit()
    return True, "Terhubung"
