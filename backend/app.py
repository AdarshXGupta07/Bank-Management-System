from flask import Flask
from flask_cors import CORS

from database import db, get_database_uri
from routes import init_routes


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)
    init_routes(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
