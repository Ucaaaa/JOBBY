from datetime import datetime, timedelta
import config  # noqa: F401  (menambah backend ke sys.path)
from app import create_app
from app.models import db, User, Application, Event, StatusHistory, Note, ChecklistItem
from app.services import new_link_code
from services import data


def test_bot_logic():
    data.set_app(create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}))
    with data.ctx():
        u = User(name="Rani", email="r@x.com"); u.set_password("password1"); db.session.add(u); db.session.commit()
        assert data.user_for(111) is None
        assert data.link(new_link_code(u.id), 111)[0] and data.user_for(111).id == u.id
        a = Application(user_id=u.id, company_name="Gojek", position="Data Analyst", status="Applied")
        db.session.add(a); db.session.flush(); db.session.add(StatusHistory(application=a, to_status="Applied")); db.session.commit()
        assert "Total: 1" in data.summary_text(u) and len(data.find_apps(u, "goj")) == 1
        # perubahan lewat bot tercatat di DB + riwayat
        data.set_status(u, a.id, "Interview"); data.add_note(u, a.id, "Tanya soal SQL")
        a = db.session.get(Application, a.id)
        assert a.status == "Interview" and len(a.history) == 2 and "SQL" in a.notes
        assert data.set_status(u, 9999, "Interview") is None
        # pengingat: event besok -> H-1, terkirim sekali saja
        n = datetime(2026, 11, 18, 12, 0)
        n_ev = Event(user_id=u.id, application_id=a.id, title="Interview Gojek", event_type="Interview", starts_at=datetime(2026, 11, 19, 10, 0), location="Meet")
        db.session.add(n_ev); n_note = Note(user_id=u.id, application_id=a.id, title="Persiapan SQL"); db.session.add(n_note); db.session.commit()
        msgs = data.due_messages(n)
        ev = [m for m in msgs if m["key"].startswith("ev:")]
        assert len(ev) == 1 and "Gojek" in ev[0]["text"] and "Persiapan SQL" in ev[0]["text"]
        data.mark_sent(ev[0]["user_id"], ev[0]["key"])
        assert not [m for m in data.due_messages(n) if m["key"].startswith("ev:")]
        # briefing jam 08:00 (jendela 3 jam), tidak di luar jendela
        assert any(m["key"].startswith("brief:") for m in data.due_messages(datetime(2026, 11, 18, 9, 0)))
        assert not any(m["key"].startswith("brief:") for m in data.due_messages(datetime(2026, 11, 18, 15, 0)))
        # follow-up: tanpa kabar > 7 hari
        for h in a.history: h.changed_at = n - timedelta(days=10)
        db.session.commit()
        assert "Data Analyst" in data.followups_text(u)
        # notifikasi dimatikan -> tidak ada pesan
        data.toggle_notif(u)
        assert data.due_messages(n) == []
        data.disconnect(111); assert data.user_for(111) is None
