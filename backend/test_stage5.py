from app import create_app
from app import routes


def test_reset_ratelimit_company():
    routes._hits.clear()
    c = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}).test_client()
    tok = c.post("/api/auth/register", json={"name": "A", "email": "a@x.com", "password": "password1"}).json["token"]
    link = c.post("/api/auth/forgot-password", json={"email": "a@x.com"}).json["dev_reset_link"]
    t = link.split("token=")[1]
    assert "dev_reset_link" not in c.post("/api/auth/forgot-password", json={"email": "nobody@x.com"}).json
    assert c.post("/api/auth/reset-password", json={"token": "salah", "new_password": "password2"}).status_code == 400
    assert c.post("/api/auth/reset-password", json={"token": t, "new_password": "password2"}).status_code == 200
    assert c.post("/api/auth/reset-password", json={"token": t, "new_password": "password3"}).status_code == 400  # sekali pakai
    assert c.post("/api/auth/login", json={"email": "a@x.com", "password": "password2"}).status_code == 200
    h = {"Authorization": "Bearer " + tok}
    co = c.post("/api/companies", headers=h, json={"name": "Gojek", "career_page": "https://x.id/jobs", "description": "Ride"}).json["company"]
    assert co["career_page"] == "https://x.id/jobs" and co["description"] == "Ride"
    routes._hits.clear()
    codes = [c.post("/api/auth/login", json={"email": "a@x.com", "password": "x"}).status_code for _ in range(12)]
    assert codes[-1] == 429 and codes[0] == 401
