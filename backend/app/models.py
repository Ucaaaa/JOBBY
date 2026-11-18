from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
STATUSES = ["Wishlist", "Applied", "Document Screening", "Assessment Test",
            "Interview", "Offering", "Accepted", "Rejected", "Withdrawn"]


class Stamp:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Stamp, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)
    def to_dict(self): return {"id": self.id, "name": self.name, "email": self.email}


class Company(Stamp, db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    industry = db.Column(db.String(120))
    location = db.Column(db.String(160))
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(500))
    career_page = db.Column(db.String(500))
    description = db.Column(db.Text)
    research_notes = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("user_id", "name"),)

    def to_dict(self):
        return {c: getattr(self, c) for c in ("id", "name", "industry", "location", "website", "logo_url", "career_page", "description", "research_notes")}


class Application(Stamp, db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    company_name = db.Column(db.String(160), nullable=False)
    position = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(160))
    employment_type = db.Column(db.String(60))
    work_arrangement = db.Column(db.String(30))
    salary_range = db.Column(db.String(80))
    job_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    applied_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(30), default="Wishlist", nullable=False)
    history = db.relationship("StatusHistory", backref="application", cascade="all, delete-orphan",
                              order_by="StatusHistory.changed_at")

    FIELDS = ("company_name", "position", "location", "employment_type", "work_arrangement",
              "salary_range", "job_url", "description", "notes", "company_id")

    def to_dict(self):
        d = {f: getattr(self, f) for f in self.FIELDS}
        d.update(id=self.id, status=self.status,
                 applied_date=self.applied_date.isoformat() if self.applied_date else None,
                 deadline=self.deadline.isoformat() if self.deadline else None)
        return d


class StatusHistory(db.Model):
    __tablename__ = "application_status_history"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False, index=True)
    from_status = db.Column(db.String(30))
    to_status = db.Column(db.String(30), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"from": self.from_status, "to": self.to_status, "changed_at": self.changed_at.isoformat()}


class Event(Stamp, db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"))
    title = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(40), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(300))
    description = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "event_type": self.event_type,
                "starts_at": self.starts_at.isoformat(), "location": self.location,
                "description": self.description, "application_id": self.application_id}


class Note(Stamp, db.Model):
    __tablename__ = "notes"
    CATEGORIES = ["Interview Preparation", "Interview Questions", "Interview Answers",
                  "Assessment Preparation", "Company Research", "General Notes"]
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(40), default="General Notes", nullable=False)
    items = db.relationship("ChecklistItem", backref="note", cascade="all, delete-orphan")

    def to_dict(self):
        done = sum(1 for i in self.items if i.done)
        return {"id": self.id, "title": self.title, "content": self.content, "category": self.category,
                "application_id": self.application_id, "company_id": self.company_id,
                "progress": {"done": done, "total": len(self.items)},
                "items": [i.to_dict() for i in self.items]}


class ChecklistItem(Stamp, db.Model):
    __tablename__ = "checklist_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    note_id = db.Column(db.Integer, db.ForeignKey("notes.id"))
    text = db.Column(db.String(300), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self): return {"id": self.id, "note_id": self.note_id, "text": self.text, "done": self.done}


class TelegramAccount(Stamp, db.Model):
    __tablename__ = "telegram_accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    telegram_user_id = db.Column(db.BigInteger, unique=True, nullable=False)


class TelegramLinkCode(db.Model):
    __tablename__ = "telegram_link_codes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code = db.Column(db.String(12), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)


class UserPreference(Stamp, db.Model):
    __tablename__ = "user_preferences"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    reminder_days = db.Column(db.String(40), default="3,1,0", nullable=False)
    briefing_time = db.Column(db.String(5), default="08:00", nullable=False)
    telegram_notifications = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {"reminder_days": [int(x) for x in self.reminder_days.split(",") if x],
                "briefing_time": self.briefing_time, "telegram_notifications": self.telegram_notifications}


class NotificationLog(db.Model):
    """Catatan pengingat yang sudah terkirim, supaya bot tidak mengirim ulang."""
    __tablename__ = "notification_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    kind = db.Column(db.String(20), nullable=False)
    ref = db.Column(db.String(80), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "ref"),)
