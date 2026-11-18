from app import create_app
from app.services import consume_link_code


def test_stage2():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    c = app.test_client()
    def reg(e): return {"Authorization": "Bearer " + c.post("/api/auth/register", json={"name": "N", "email": e, "password": "password1"}).json["token"]}
    h, h2 = reg("a@x.com"), reg("b@x.com")
    n = c.post("/api/notes", headers=h, json={"title": "SQL", "category": "Interview Preparation"}).json["note"]
    assert c.post("/api/notes", headers=h, json={"title": "x", "category": "Salah"}).status_code == 400
    it = c.post("/api/checklists", headers=h, json={"text": "Review SQL", "note_id": n["id"]}).json["item"]
    c.post("/api/checklists", headers=h, json={"text": "Portfolio", "note_id": n["id"]})
    c.put(f"/api/checklists/{it['id']}", headers=h, json={"done": True})
    assert c.get("/api/notes", headers=h).json["notes"][0]["progress"] == {"done": 1, "total": 2}
    assert c.put(f"/api/checklists/{it['id']}", headers=h2, json={"done": False}).status_code == 404
    assert c.get("/api/notes?search=sql", headers=h2).json["notes"] == []
    e = c.post("/api/events", headers=h, json={"title": "Int", "event_type": "Interview", "starts_at": "2030-01-01T10:00"}).json["event"]
    assert c.put(f"/api/events/{e['id']}", headers=h, json={"title": "Int2"}).json["event"]["title"] == "Int2"
    assert c.delete(f"/api/events/{e['id']}", headers=h2).status_code == 404
    c.post("/api/applications", headers=h, json={"company_name": "X", "position": "Y", "applied_date": "2026-10-05"})
    assert c.get("/api/dashboard/statistics", headers=h).json["by_month"] == [{"month": "2026-10", "count": 1}]
    assert c.put("/api/telegram/settings", headers=h, json={"reminder_days": [1, 3, 0], "briefing_time": "07:30"}).json["settings"]["reminder_days"] == [3, 1, 0]
    assert c.put("/api/telegram/settings", headers=h, json={"briefing_time": "25:99"}).status_code == 400
    code = c.post("/api/telegram/link-code", headers=h).json["code"]
    with app.app_context():
        assert consume_link_code(code, 111)[0]
        assert not consume_link_code(code, 222)[0]  # sekali pakai
    assert c.get("/api/telegram/status", headers=h).json["connected"] is True
    code2 = c.post("/api/telegram/link-code", headers=h2).json["code"]
    with app.app_context():
        assert not consume_link_code(code2, 111)[0]  # telegram id unik
    assert c.post("/api/telegram/disconnect", headers=h).json["connected"] is False
    assert c.put("/api/auth/profile", headers=h, json={"email": "b@x.com"}).status_code == 409
