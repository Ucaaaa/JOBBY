from datetime import date, datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from .models import (db, User, Application, Company, Event, Note, ChecklistItem,
                     TelegramAccount, UserPreference, STATUSES)
from .routes import api, err, uid, clean, EMAIL_RE
from .services import new_link_code


def mine(model, i): return model.query.filter_by(id=i, user_id=uid()).first()
def body(): return request.get_json(silent=True) or {}


def set_fields(obj, d, fields):
    for f in fields:
        if f in d: setattr(obj, f, clean(d[f]))


# ---------- Profile ----------
@api.put("/auth/profile")
@jwt_required()
def profile():
    d, u = body(), db.session.get(User, uid())
    if d.get("name"): u.name = clean(d["name"])
    if d.get("email"):
        e = clean(d["email"]).lower()
        if not EMAIL_RE.match(e): return err("Email tidak valid")
        if User.query.filter(User.email == e, User.id != u.id).first(): return err("Email sudah dipakai", 409)
        u.email = e
    db.session.commit()
    return jsonify(user=u.to_dict())


# ---------- Companies ----------
@api.put("/companies/<int:i>")
@jwt_required()
def edit_company(i):
    c = mine(Company, i)
    if not c: return err("Tidak ditemukan", 404)
    set_fields(c, body(), ("name", "industry", "location", "website", "logo_url", "career_page", "description", "research_notes"))
    db.session.commit()
    return jsonify(company=c.to_dict())


@api.delete("/companies/<int:i>")
@jwt_required()
def del_company(i):
    c = mine(Company, i)
    if not c: return err("Tidak ditemukan", 404)
    Application.query.filter_by(company_id=c.id).update({"company_id": None})
    Note.query.filter_by(company_id=c.id).update({"company_id": None})
    db.session.delete(c); db.session.commit()
    return "", 204


# ---------- Events ----------
@api.get("/events")
@jwt_required()
def events():
    q = Event.query.filter_by(user_id=uid())
    try:
        if request.args.get("from"): q = q.filter(Event.starts_at >= datetime.fromisoformat(request.args["from"]))
        if request.args.get("to"): q = q.filter(Event.starts_at <= datetime.fromisoformat(request.args["to"]))
    except ValueError: return err("Format tanggal tidak valid")
    return jsonify(events=[e.to_dict() for e in q.order_by(Event.starts_at)])


@api.put("/events/<int:i>")
@jwt_required()
def edit_event(i):
    e, d = mine(Event, i), body()
    if not e: return err("Tidak ditemukan", 404)
    set_fields(e, d, ("title", "event_type", "location", "description"))
    if d.get("starts_at"):
        try: e.starts_at = datetime.fromisoformat(d["starts_at"])
        except ValueError: return err("starts_at tidak valid")
    db.session.commit()
    return jsonify(event=e.to_dict())


@api.delete("/events/<int:i>")
@jwt_required()
def del_event(i):
    e = mine(Event, i)
    if not e: return err("Tidak ditemukan", 404)
    db.session.delete(e); db.session.commit()
    return "", 204


# ---------- Notes ----------
def valid_links(d):
    if d.get("application_id") and not mine(Application, d["application_id"]): return False
    if d.get("company_id") and not mine(Company, d["company_id"]): return False
    return True


@api.get("/notes")
@jwt_required()
def notes():
    q, a = Note.query.filter_by(user_id=uid()), request.args
    if a.get("category"): q = q.filter_by(category=a["category"])
    if a.get("application_id"): q = q.filter_by(application_id=a["application_id"])
    if a.get("search"):
        s = f"%{a['search']}%"; q = q.filter(db.or_(Note.title.ilike(s), Note.content.ilike(s)))
    return jsonify(notes=[n.to_dict() for n in q.order_by(Note.updated_at.desc())])


@api.post("/notes")
@jwt_required()
def add_note():
    d = body()
    if not clean(d.get("title")): return err("title wajib diisi")
    if d.get("category", "General Notes") not in Note.CATEGORIES: return err("Kategori tidak valid")
    if not valid_links(d): return err("application_id/company_id tidak valid", 404)
    n = Note(user_id=uid(), title=clean(d["title"]), content=d.get("content"),
             category=d.get("category", "General Notes"),
             application_id=d.get("application_id"), company_id=d.get("company_id"))
    db.session.add(n); db.session.commit()
    return jsonify(note=n.to_dict()), 201


@api.put("/notes/<int:i>")
@jwt_required()
def edit_note(i):
    n, d = mine(Note, i), body()
    if not n: return err("Tidak ditemukan", 404)
    if "category" in d and d["category"] not in Note.CATEGORIES: return err("Kategori tidak valid")
    if not valid_links(d): return err("application_id/company_id tidak valid", 404)
    set_fields(n, d, ("title", "content", "category", "application_id", "company_id"))
    db.session.commit()
    return jsonify(note=n.to_dict())


@api.delete("/notes/<int:i>")
@jwt_required()
def del_note(i):
    n = mine(Note, i)
    if not n: return err("Tidak ditemukan", 404)
    db.session.delete(n); db.session.commit()
    return "", 204


# ---------- Checklists ----------
@api.get("/checklists")
@jwt_required()
def checklists():
    q = ChecklistItem.query.filter_by(user_id=uid())
    if request.args.get("note_id"): q = q.filter_by(note_id=request.args["note_id"])
    if request.args.get("pending") == "1": q = q.filter_by(done=False)
    return jsonify(items=[i.to_dict() for i in q.order_by(ChecklistItem.id)])


@api.post("/checklists")
@jwt_required()
def add_item():
    d = body()
    if not clean(d.get("text")): return err("text wajib diisi")
    if d.get("note_id") and not mine(Note, d["note_id"]): return err("Note tidak ditemukan", 404)
    it = ChecklistItem(user_id=uid(), text=clean(d["text"]), note_id=d.get("note_id"))
    db.session.add(it); db.session.commit()
    return jsonify(item=it.to_dict()), 201


@api.put("/checklists/<int:i>")
@jwt_required()
def edit_item(i):
    it, d = mine(ChecklistItem, i), body()
    if not it: return err("Tidak ditemukan", 404)
    if d.get("text"): it.text = clean(d["text"])
    if "done" in d: it.done = bool(d["done"])
    db.session.commit()
    return jsonify(item=it.to_dict())


@api.delete("/checklists/<int:i>")
@jwt_required()
def del_item(i):
    it = mine(ChecklistItem, i)
    if not it: return err("Tidak ditemukan", 404)
    db.session.delete(it); db.session.commit()
    return "", 204


# ---------- Dashboard statistics ----------
@api.get("/dashboard/statistics")
@jwt_required()
def statistics():
    month = func.strftime("%Y-%m", Application.applied_date)
    rows = (db.session.query(month, func.count())
            .filter(Application.user_id == uid(), Application.applied_date.isnot(None))
            .group_by(month).order_by(month).all())
    by_status = dict(db.session.query(Application.status, func.count()).filter_by(user_id=uid())
                     .group_by(Application.status).all())
    return jsonify(by_status=[{"status": s, "count": by_status.get(s, 0)} for s in STATUSES],
                   by_month=[{"month": m, "count": c} for m, c in rows])


# ---------- Telegram ----------
@api.post("/telegram/link-code")
@jwt_required()
def link_code():
    return jsonify(code=new_link_code(uid()), expires_in_minutes=10), 201


@api.get("/telegram/status")
@jwt_required()
def tg_status():
    return jsonify(connected=TelegramAccount.query.filter_by(user_id=uid()).first() is not None)


@api.post("/telegram/disconnect")
@jwt_required()
def tg_disconnect():
    TelegramAccount.query.filter_by(user_id=uid()).delete(); db.session.commit()
    return jsonify(connected=False)


def prefs():
    p = UserPreference.query.filter_by(user_id=uid()).first()
    if not p:
        p = UserPreference(user_id=uid()); db.session.add(p); db.session.commit()
    return p


@api.get("/telegram/settings")
@jwt_required()
def tg_settings(): return jsonify(settings=prefs().to_dict())


@api.put("/telegram/settings")
@jwt_required()
def tg_settings_put():
    p, d = prefs(), body()
    if "reminder_days" in d:
        days = d["reminder_days"]
        if not isinstance(days, list) or not all(isinstance(x, int) and 0 <= x <= 30 for x in days):
            return err("reminder_days harus list angka 0-30")
        p.reminder_days = ",".join(str(x) for x in sorted(set(days), reverse=True))
    if "briefing_time" in d:
        try: datetime.strptime(d["briefing_time"], "%H:%M")
        except (TypeError, ValueError): return err("briefing_time harus HH:MM")
        p.briefing_time = d["briefing_time"]
    if "telegram_notifications" in d: p.telegram_notifications = bool(d["telegram_notifications"])
    db.session.commit()
    return jsonify(settings=p.to_dict())


# ---------- Reset password ----------
import os
from flask import current_app
from itsdangerous import BadSignature, URLSafeTimedSerializer
from .routes import rate_limit


def _ser(): return URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"], salt="jobby-reset")


@api.post("/auth/forgot-password")
@rate_limit(5, 60)
def forgot_password():
    """Belum ada layanan email: di mode development, link reset dicetak ke log server dan dikembalikan di response."""
    u = User.query.filter_by(email=(body().get("email") or "").strip().lower()).first()
    res = {"message": "Jika email terdaftar, instruksi reset password akan dikirim."}
    if u:
        link = f"{os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173')}/reset-password?token=" + _ser().dumps({"id": u.id, "h": u.password_hash[-12:]})
        current_app.logger.warning("RESET LINK untuk %s: %s", u.email, link)
        if os.getenv("APP_ENV", "development") != "production": res["dev_reset_link"] = link
    return jsonify(res)


@api.post("/auth/reset-password")
@rate_limit(10, 60)
def reset_password():
    d = body()
    if len(d.get("new_password") or "") < 8: return err("Password baru minimal 8 karakter")
    try: p = _ser().loads(d.get("token") or "", max_age=3600)
    except BadSignature: return err("Link reset tidak valid atau kedaluwarsa", 400)
    u = db.session.get(User, p["id"])
    if not u or u.password_hash[-12:] != p["h"]: return err("Link reset sudah dipakai atau tidak valid", 400)
    u.set_password(d["new_password"]); db.session.commit()  # hash berubah -> token lama otomatis tidak berlaku
    return jsonify(message="Password diperbarui, silakan masuk")
