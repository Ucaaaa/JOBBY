from app import create_app


def test_flow():
    c = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}).test_client()
    tok = c.post("/api/auth/register", json={"name": "A", "email": "a@x.com", "password": "password1"}).json["token"]
    h = {"Authorization": f"Bearer {tok}"}
    tok2 = c.post("/api/auth/register", json={"name": "B", "email": "b@x.com", "password": "password1"}).json["token"]
    aid = c.post("/api/applications", headers=h, json={"company_name": "X", "position": "Y", "status": "Applied"}).json["application"]["id"]
    assert c.put(f"/api/applications/{aid}/status", headers=h, json={"status": "Interview"}).status_code == 200
    assert len(c.get(f"/api/applications/{aid}/history", headers=h).json["history"]) == 2
    s = c.get("/api/dashboard/summary", headers=h).json
    assert s["total"] == 1 and s["interviews"] == 1
    assert c.get(f"/api/applications/{aid}", headers={"Authorization": f"Bearer {tok2}"}).status_code == 404
    assert c.get("/api/applications").status_code == 401
    assert c.post("/api/auth/login", json={"email": "a@x.com", "password": "salah"}).status_code == 401
    assert c.delete(f"/api/applications/{aid}", headers=h).status_code == 204
