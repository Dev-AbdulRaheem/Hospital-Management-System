"""Application configuration."""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Default configuration for HMS."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hms-dev-secret-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(basedir, "instance", "hms.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
