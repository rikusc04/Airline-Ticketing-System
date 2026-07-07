from __future__ import annotations

import os
from urllib.parse import quote_plus


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Environment variable {name!r} is required but not set.")
    return value


def _mysql_url(user: str, password: str, host: str, port: str, database: str) -> str:
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{database}?charset=utf8mb4"
    )


class Config:
    """Base configuration shared by all environments."""

    # Loaded lazily by subclasses so tests can override.
    SECRET_KEY: str = ""
    SQLALCHEMY_DATABASE_URI: str = ""

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 10,
        "max_overflow": 5,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True

    WTF_CSRF_TIME_LIMIT = 3600

    BCRYPT_LOG_ROUNDS = 12

    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB request body cap


class ProductionConfig(Config):
    def __init__(self) -> None:
        self.SECRET_KEY = _require("SECRET_KEY")
        self.SQLALCHEMY_DATABASE_URI = _require("DATABASE_URL")


class DevelopmentConfig(Config):
    SESSION_COOKIE_SECURE = False
    BCRYPT_LOG_ROUNDS = 4  # faster iteration in dev

    def __init__(self) -> None:
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret")
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            _mysql_url(
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", ""),
                host=os.environ.get("DB_HOST", "127.0.0.1"),
                port=os.environ.get("DB_PORT", "3306"),
                database=os.environ.get("DB_NAME", "air_ticket_system"),
            ),
        )


class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    BCRYPT_LOG_ROUNDS = 4

    def __init__(self) -> None:
        self.SECRET_KEY = "testing-secret"  # noqa: S105 — test-only literal
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "TEST_DATABASE_URL",
            _mysql_url(
                user=os.environ.get("TEST_DB_USER", "root"),
                password=os.environ.get("TEST_DB_PASSWORD", ""),
                host=os.environ.get("TEST_DB_HOST", "127.0.0.1"),
                port=os.environ.get("TEST_DB_PORT", "3306"),
                database=os.environ.get("TEST_DB_NAME", "air_ticket_system_test"),
            ),
        )


def get_config() -> Config:
    env = os.environ.get("FLASK_ENV", "production").lower()
    if env in ("development", "dev"):
        return DevelopmentConfig()
    if env in ("testing", "test"):
        return TestingConfig()
    return ProductionConfig()
