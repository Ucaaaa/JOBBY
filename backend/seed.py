"""Buat akun demo: demo@jobby.dev / demo12345 (hanya untuk development)."""
from datetime import date, datetime, timedelta
from app import create_app
from app.models import db, User, Application, StatusHistory, Event

app = create_app()
with app.app_context():
    if User.query.filter_by(email="demo@jobby.dev").first():
        print("Demo sudah ada"); raise SystemExit
    u = User(name="Demo User", email="demo@jobby.dev"); u.set_password("demo12345")
    db.session.add(u); db.session.flush()
    for co, pos, st in [("Gojek", "Data Analyst", "Interview"), ("Tokopedia", "Product Analyst", "Applied"),
                        ("Traveloka", "BI Analyst", "Assessment Test"), ("Bank Mandiri", "Data Scientist", "Rejected"),
                        ("Shopee", "Business Analyst", "Wishlist")]:
        a = Application(user_id=u.id, company_name=co, position=pos, status=st, location="Jakarta",
                        employment_type="Full-time", applied_date=date.today() - timedelta(days=5),
                        deadline=date.today() + timedelta(days=7))
        db.session.add(a)
        db.session.add(StatusHistory(application=a, to_status=st))
    db.session.add(Event(user_id=u.id, title="Interview Gojek", event_type="Interview",
                         starts_at=datetime.now() + timedelta(days=2), location="Google Meet"))
    db.session.commit(); print("Seed selesai")
