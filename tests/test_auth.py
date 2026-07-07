"""Tests for registration and login flows."""

from __future__ import annotations

from sqlalchemy import text

from app.extensions import db
from app.security import verify_password


def test_healthz(client):  # type: ignore[no-untyped-def]
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_customer_register_stores_bcrypt_hash(client, app):  # type: ignore[no-untyped-def]
    resp = client.post(
        "/customer/register",
        data={
            "email_address": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Doe",
            "password": "SafePassw0rd!",
            "building_number": "1",
            "street": "Main",
            "apt_number": "1",
            "city": "NYC",
            "state": "NY",
            "zipcode": "10001",
            "passport_number": "P1234567",
            "passport_expiration": "2030-01-01",
            "passport_country": "USA",
            "date_of_birth": "2000-01-01",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (301, 302)
    with app.app_context():
        row = (
            db.session.execute(
                text("SELECT password FROM Customer WHERE email_address = :e"),
                {"e": "alice@example.com"},
            )
            .mappings()
            .first()
        )
    assert row is not None
    assert row["password"].startswith("$2b$")  # bcrypt marker
    assert verify_password("SafePassw0rd!", row["password"])


def test_customer_register_rejects_weak_password(client):  # type: ignore[no-untyped-def]
    resp = client.post(
        "/customer/register",
        data={
            "email_address": "weak@example.com",
            "first_name": "Weak",
            "last_name": "Pass",
            "password": "short",
            "building_number": "1",
            "street": "Main",
            "apt_number": "1",
            "city": "NYC",
            "state": "NY",
            "zipcode": "10001",
            "passport_number": "P1234567",
            "passport_expiration": "2030-01-01",
            "passport_country": "USA",
            "date_of_birth": "2000-01-01",
        },
    )
    assert resp.status_code == 400


def test_customer_login_success(client, customer):  # type: ignore[no-untyped-def]
    resp = client.post(
        "/customer/login",
        data={
            "email_address": customer["email"],
            "password": customer["password"],
        },
        follow_redirects=False,
    )
    assert resp.status_code in (301, 302)
    assert "/customer/dashboard" in resp.headers["Location"]


def test_customer_login_wrong_password(client, customer):  # type: ignore[no-untyped-def]
    resp = client.post(
        "/customer/login",
        data={
            "email_address": customer["email"],
            "password": "not-the-password",
        },
    )
    assert resp.status_code == 401


def test_customer_login_unknown_email_generic(client):  # type: ignore[no-untyped-def]
    """Unknown-email response must not differ from wrong-password: no user enum."""
    resp = client.post(
        "/customer/login",
        data={
            "email_address": "ghost@example.com",
            "password": "whatever",
        },
    )
    assert resp.status_code == 401
    body = resp.get_data(as_text=True)
    assert "email" not in body.lower() or "invalid" in body.lower()


def test_customer_dashboard_requires_login(client):  # type: ignore[no-untyped-def]
    resp = client.get("/customer/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "/customer/login" in resp.headers["Location"]


def test_staff_dashboard_requires_login(client):  # type: ignore[no-untyped-def]
    resp = client.get("/staff/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "/staff/login" in resp.headers["Location"]


def test_staff_login_success(client, staff_member):  # type: ignore[no-untyped-def]
    resp = client.post(
        "/staff/login",
        data={
            "username": staff_member["username"],
            "password": staff_member["password"],
        },
        follow_redirects=False,
    )
    assert resp.status_code in (301, 302)
    assert "/staff/dashboard" in resp.headers["Location"]
