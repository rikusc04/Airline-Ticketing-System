"""Test fixtures: real MySQL, wiped between tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import text

# Force testing config before app imports.
os.environ["FLASK_ENV"] = "testing"

from app import create_app  # noqa: E402
from app.config import TestingConfig  # noqa: E402
from app.extensions import db  # noqa: E402

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _load_schema(engine) -> None:  # type: ignore[no-untyped-def]
    """Reload schema from db/schema.sql into the test DB."""
    sql = SCHEMA_PATH.read_text()
    # Split into statements; naive but adequate for our schema (no procedures).
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        # Drop existing tables in dependency-friendly order.
        rows = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = DATABASE()"
            )
        ).all()
        for (table,) in rows:
            conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    with engine.begin() as conn:
        for stmt in sql.split(";"):
            # Strip full-line comments and blank lines from the chunk so
            # `-- separator` lines before a CREATE don't mask the statement.
            lines = [
                line
                for line in stmt.splitlines()
                if line.strip() and not line.strip().startswith("--")
            ]
            cleaned = "\n".join(lines).strip()
            if not cleaned:
                continue
            conn.execute(text(cleaned))


@pytest.fixture(scope="session")
def app():  # type: ignore[no-untyped-def]
    application = create_app(TestingConfig)
    with application.app_context():
        _load_schema(db.engine)
    yield application


@pytest.fixture()
def client(app):  # type: ignore[no-untyped-def]
    return app.test_client()


@pytest.fixture(autouse=True)
def _clean_db(app):  # type: ignore[no-untyped-def]
    """Wipe user-generated data between tests (keeps reference rows)."""
    with app.app_context(), db.engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in (
            "Trips",
            "Reviews",
            "Purchase",
            "Ticket",
            "Flight",
            "Airplane",
            "Maintenance",
            "Employed_By",
            "Airline_Staff_Phone_Number",
            "Airline_Staff_Email_Address",
            "Airline_Staff",
            "CustomerPhone",
            "Customer",
        ):
            conn.execute(text(f"DELETE FROM `{table}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    yield


@pytest.fixture()
def customer(app):  # type: ignore[no-untyped-def]
    """Create a canonical customer and return their email + password."""
    from app.security import hash_password

    email = "test@example.com"
    password = "TestPassw0rd!"
    with app.app_context():
        db.session.execute(
            text(
                "INSERT INTO Customer "
                "(email_address, first_name, last_name, password, "
                "building_number, street, apt_number, city, state, "
                "zipcode, passport_number, passport_expiration, "
                "passport_country, date_of_birth) VALUES "
                "(:email, 'Test', 'User', :pw, 1, 'Main', 1, 'NYC', 'NY', "
                "10001, 'P1234567', '2030-01-01', 'USA', '2000-01-01')"
            ),
            {"email": email, "pw": hash_password(password)},
        )
        db.session.commit()
    return {"email": email, "password": password}


@pytest.fixture()
def staff_member(app):  # type: ignore[no-untyped-def]
    from app.security import hash_password

    username = "testadmin"
    password = "AdminPassw0rd!"
    airline = "Delta"
    with app.app_context():
        db.session.execute(
            text(
                "INSERT INTO Airline_Staff "
                "(username, password, first_name, last_name, date_of_birth) "
                "VALUES (:u, :pw, 'Admin', 'User', '1990-01-01')"
            ),
            {"u": username, "pw": hash_password(password)},
        )
        db.session.execute(
            text("INSERT INTO Employed_By (airline_name, username) " "VALUES (:a, :u)"),
            {"a": airline, "u": username},
        )
        db.session.commit()
    return {"username": username, "password": password, "airline": airline}
