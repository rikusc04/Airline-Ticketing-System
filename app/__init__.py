from __future__ import annotations

import logging
import os
from logging.config import dictConfig

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config, get_config
from .extensions import bcrypt, csrf, db


def create_app(config: Config | type[Config] | None = None) -> Flask:
    """Application factory. Accepts a Config instance, subclass, or None."""
    _configure_logging()

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    resolved = config or get_config()
    # If a class was passed, instantiate it so __init__-computed fields
    # (SECRET_KEY, SQLALCHEMY_DATABASE_URI) are populated.
    if isinstance(resolved, type):
        resolved = resolved()
    app.config.from_object(resolved)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore[method-assign]

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    from .blueprints.auth import bp as auth_bp
    from .blueprints.customer import bp as customer_bp
    from .blueprints.main import bp as main_bp
    from .blueprints.staff import bp as staff_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(staff_bp)

    _register_error_handlers(app)
    _register_security_headers(app)

    @app.route("/healthz")
    def healthz() -> tuple[dict[str, str], int]:
        from sqlalchemy import text

        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok"}, 200
        except Exception:
            app.logger.exception("healthz db check failed")
            return {"status": "degraded"}, 503

    return app


def _configure_logging() -> None:
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": ("%(asctime)s %(levelname)s [%(name)s] " "%(message)s"),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {"level": level, "handlers": ["console"]},
        }
    )
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def _register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(404)
    def not_found(_e: Exception) -> tuple[str, int]:
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e: Exception) -> tuple[str, int]:
        app.logger.exception("unhandled exception: %s", e)
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_security_headers(app: Flask) -> None:
    from flask import Response

    @app.after_request
    def set_secure_headers(resp: Response) -> Response:
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; script-src 'self'",
        )
        return resp
