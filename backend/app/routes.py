import re
import time
from collections import defaultdict, deque
from functools import wraps
from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import func
from .models import db, User, Application, Company, Event, StatusHistory, STATUSES

api = Blueprint("api", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
IN_PROGRESS = ["Applied", "Document Screening", "Assessment Test", "Interview", "Offering"]


def err(msg, code=400): return jsonify(error=msg), code
def uid(): return int(get_jwt_identity())
_hits = defaultdict(deque)
def rate_limit(limit=10, window=60):
    """Pembatas sederhana per IP+endpoint (in-memory; untuk produksi gunakan Redis/Flask-Limiter)."""
    def deco(fn):
        @wraps(fn)
        def w(*a, **k):
            q, t = _hits[(fn.__name__, request.remote_addr)], time.time()
            while q and q[0] < t - window: q.popleft()
            if len(q) >= limit: return err("Terlalu banyak percobaan, coba lagi sebentar lagi", 429)
            q.append(t)
            return fn(*a, **k)
        return w
    return deco
def pdate(v):
    try: return date.fromisoformat(v) if v else None
    except ValueError: return None
def clean(v): return v.strip() if isinstance(v, str) else v


def own_app(app_id):
    return Application.query.filter_by(id=app_id, user_id=uid()).first()


def log_status(app, new):
    db.session.add(StatusHistory(application=app, from_status=app.status if app.id else None, to_status=new))
    app.status = new


# ---------- Auth ----------
@api.post("/auth/register")
@rate_limit()
def register():
    d = request.get_json(silent=True) or {}
    name, email, pw = clean(d.get("name")), (clean(d.get("email")) or "").lower(), d.get("password") or ""
    if not name or not EMAIL_RE.match(email): return err("Nama dan email valid wajib diisi")
    if len(pw) < 8: return err("Password minimal 8 karakter")
    if User.query.filter_by(email=email).first(): return err("Email sudah terdaftar", 409)
    u = User(name=name, email=email); u.set_password(pw)
    db.session.add(u); db.session.commit()
    return jsonify(token=create_access_token(identity=str(u.id)), user=u.to_dict()), 201


@api.post("/auth/login")
@rate_limit()
def login():
    d = request.get_json(silent=True) or {}
    u = User.query.filter_by(email=(d.get("email") or "").lower()).first()
    if not u or not u.check_password(d.get("password") or ""): return err("Email atau password salah", 401)
    return jsonify(token=create_access_token(identity=str(u.id)), user=u.to_dict())


@api.get("/auth/me")
@jwt_required()
def me():
    return jsonify(user=db.session.get(User, uid()).to_dict())


@api.put("/auth/change-password")
@jwt_required()
def change_password():
    d = request.get_json(silent=True) or {}
    u = db.session.get(User, uid())
    if not u.check_password(d.get("old_password") or ""): return err("Password lama salah", 401)
    if len(d.get("new_password") or "") < 8: return err("Password baru minimal 8 karakter")
    u.set_password(d["new_password"]); db.session.commit()
    return jsonify(message="Password diperbarui")


# ---------- Applications ----------
@api.get("/applications")
@jwt_required()
def list_apps():
    q = Application.query.filter_by(user_id=uid())
    a = request.args
    if a.get("status"): q = q.filter_by(status=a["status"])
    if a.get("location"): q = q.filter(Application.location.ilike(f"%{a['location']}%"))
    if a.get("employment_type"): q = q.filter_by(employment_type=a["employment_type"])
    if a.get("search"):
        s = f"%{a['search']}%"
        q = q.filter(db.or_(Application.company_name.ilike(s), Application.position.ilike(s)))
    order = Application.applied_date.asc() if a.get("sort") == "asc" else Application.applied_date.desc()
    return jsonify(applications=[x.to_dict() for x in q.order_by(order, Application.id.desc())])


@api.post("/applications")
@jwt_required()
def create_app_():
    d = request.get_json(silent=True) or {}
    if not clean(d.get("company_name")) or not clean(d.get("position")):
        return err("company_name dan position wajib diisi")
    status = d.get("status", "Wishlist")
    if status not in STATUSES: return err("Status tidak valid")
    app = Application(user_id=uid(), applied_date=pdate(d.get("applied_date")),
                      deadline=pdate(d.get("deadline")), status=status,
                      **{f: clean(d.get(f)) for f in Application.FIELDS if f != "company_id"})
    db.session.add(app)
    db.session.add(StatusHistory(application=app, from_status=None, to_status=status))
    db.session.commit()
    return jsonify(application=app.to_dict()), 201


@api.get("/applications/<int:i>")
@jwt_required()
def get_app(i):
    a = own_app(i)
    if not a: return err("Tidak ditemukan", 404)
    return jsonify(application=a.to_dict(), history=[h.to_dict() for h in a.history])


@api.put("/applications/<int:i>")
@jwt_required()
def update_app(i):
    a = own_app(i)
    if not a: return err("Tidak ditemukan", 404)
    d = request.get_json(silent=True) or {}
    for f in Application.FIELDS:
        if f in d and f != "company_id": setattr(a, f, clean(d[f]))
    if "applied_date" in d: a.applied_date = pdate(d["applied_date"])
    if "deadline" in d: a.deadline = pdate(d["deadline"])
    if d.get("status") and d["status"] != a.status:
        if d["status"] not in STATUSES: return err("Status tidak valid")
        log_status(a, d["status"])
    db.session.commit()
    return jsonify(application=a.to_dict())


@api.put("/applications/<int:i>/status")
@jwt_required()
def set_status(i):
    a = own_app(i)
    if not a: return err("Tidak ditemukan", 404)
    s = (request.get_json(silent=True) or {}).get("status")
    if s not in STATUSES: return err("Status tidak valid")
    if s != a.status:
        log_status(a, s); db.session.commit()
    return jsonify(application=a.to_dict())


@api.delete("/applications/<int:i>")
@jwt_required()
def delete_app(i):
    a = own_app(i)
    if not a: return err("Tidak ditemukan", 404)
    Event.query.filter_by(application_id=a.id).update({"application_id": None})
    db.session.delete(a); db.session.commit()
    return "", 204


@api.get("/applications/<int:i>/history")
@jwt_required()
def history(i):
    a = own_app(i)
    if not a: return err("Tidak ditemukan", 404)
    return jsonify(history=[h.to_dict() for h in a.history])


@api.get("/tracker")
@jwt_required()
def tracker():
    cols = {s: [] for s in STATUSES}
    for a in Application.query.filter_by(user_id=uid()):
        cols[a.status].append(a.to_dict())
    return jsonify(columns=cols)


# ---------- Dashboard ----------
@api.get("/dashboard/summary")
@jwt_required()
def summary():
    rows = dict(db.session.query(Application.status, func.count()).filter_by(user_id=uid())
                .group_by(Application.status).all())
    return jsonify(total=sum(rows.values()), in_progress=sum(rows.get(s, 0) for s in IN_PROGRESS),
                   interviews=rows.get("Interview", 0), accepted=rows.get("Accepted", 0),
                   rejected=rows.get("Rejected", 0), by_status={s: rows.get(s, 0) for s in STATUSES})


@api.get("/dashboard/recent-applications")
@jwt_required()
def recent():
    q = Application.query.filter_by(user_id=uid()).order_by(Application.created_at.desc()).limit(5)
    return jsonify(applications=[a.to_dict() for a in q])


# ---------- Companies & Events ----------
@api.get("/companies")
@jwt_required()
def companies():
    return jsonify(companies=[c.to_dict() for c in Company.query.filter_by(user_id=uid()).order_by(Company.name)])


@api.post("/companies")
@jwt_required()
def add_company():
    d = request.get_json(silent=True) or {}
    if not clean(d.get("name")): return err("name wajib diisi")
    c = Company(user_id=uid(), **{f: clean(d.get(f)) for f in ("name", "industry", "location", "website", "logo_url", "career_page", "description", "research_notes")})
    db.session.add(c)
    try: db.session.commit()
    except Exception:
        db.session.rollback(); return err("Perusahaan sudah ada", 409)
    return jsonify(company=c.to_dict()), 201


@api.get("/dashboard/upcoming-events")
@jwt_required()
def upcoming():
    q = Event.query.filter(Event.user_id == uid(), Event.starts_at >= datetime.utcnow()).order_by(Event.starts_at).limit(10)
    return jsonify(events=[e.to_dict() for e in q])


@api.post("/events")
@jwt_required()
def add_event():
    d = request.get_json(silent=True) or {}
    try: start = datetime.fromisoformat(d["starts_at"])
    except (KeyError, ValueError): return err("starts_at (ISO datetime) wajib diisi")
    if not clean(d.get("title")) or not d.get("event_type"): return err("title dan event_type wajib diisi")
    e = Event(user_id=uid(), title=clean(d["title"]), event_type=d["event_type"], starts_at=start,
              location=clean(d.get("location")), description=clean(d.get("description")))
    if d.get("application_id") and own_app(d["application_id"]): e.application_id = d["application_id"]
    db.session.add(e); db.session.commit()
    return jsonify(event=e.to_dict()), 201
