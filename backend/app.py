from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

from database import db, get_database_uri
from routes import init_routes

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


def create_app():
    app = Flask(__name__)
    
    # Strictly get database URL from environment
    database_uri = get_database_uri()
    if not database_uri or "mysql" not in database_uri:
        raise ValueError("DATABASE_URL must be a MySQL connection string (e.g., mysql+pymysql://...)")
    
    print(f"Connecting to MySQL: {database_uri}")
    
    # Test database connection
    try:
        from sqlalchemy import create_engine, text
        test_engine = create_engine(database_uri)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("MySQL connection successful")
    except Exception as e:
        print(f"CRITICAL: MySQL connection failed: {e}")
        raise e
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)
    init_routes(app)

    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        return send_from_directory(FRONTEND_DIR, path)

    @app.route("/api/health")
    def health():
        return {"status": "ok", "database_type": "MySQL", "uri": app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1]}
    
    @app.route("/routes")
    def list_routes():
        import urllib
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            url = rule.rule
            output.append({"endpoint": rule.endpoint, "methods": methods, "url": url})
        return {"routes": output}

    with app.app_context():
        try:
            db.create_all()
            print("Database schemas verified/created")
        except Exception as e:
            print(f"Error creating tables: {e}")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
