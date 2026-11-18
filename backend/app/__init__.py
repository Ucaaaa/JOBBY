import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .models import db

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///jobby.db"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-me-please-32bytes"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=7),
    )
    if test_config:
        app.config.update(test_config)
    CORS(app, origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")])
    db.init_app(app)
    JWTManager(app)
    from .routes import api
    from . import routes_more  # noqa: F401
    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(404)
    def nf(_): return jsonify(error="Not found"), 404

    with app.app_context():
        db.create_all()
    return app
