import os
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def get_database_uri() -> str:
    """Resolve database URI from environment."""
    return os.getenv("DATABASE_URL")
