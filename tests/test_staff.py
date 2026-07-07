"""Tests for staff flight-management endpoints."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text

from app.extensions import db


def _login(client, staff):  # type: ignore[no-untyped-def]
    client.post(
        "/staff/login",
        data={"username": staff["username"], "password": staff["password"]},
    )


def test_add_flight_creates_row(client, app, staff_member):  # type: ignore[no-untyped-def]
    _login(client, staff_member)
    depart = (date.today() + timedelta(days=30)).isoformat()
    resp = client.post(
        "/staff/add_flight",
        data={
            "flight_number": "DL500",
            "depart_date": depart,
            "depart_time": "10:00:00",
            "depart_airport_code": "JFK",
            "arrival_date": depart,
            "arrival_time": "13:00:00",
            "arrival_airport_code": "HND",
            "base_price": "700",
            "status": "On time",
            "airplane_id": "",
        },
    )
    assert resp.status_code in (301, 302)
    with app.app_context():
        row = (
            db.session.execute(
                text(
                    "SELECT * FROM Flight WHERE flight_number = :f "
                    "AND airline_name = :a"
                ),
                {"f": "DL500", "a": staff_member["airline"]},
            )
            .mappings()
            .first()
        )
    assert row is not None


def test_add_flight_requires_staff_login(client):  # type: ignore[no-untyped-def]
    resp = client.post(
        "/staff/add_flight", data={"flight_number": "X"}, follow_redirects=False
    )
    assert resp.status_code in (301, 302)
    assert "/staff/login" in resp.headers["Location"]


def test_add_flight_rejects_past_date(client, app, staff_member):  # type: ignore[no-untyped-def]
    _login(client, staff_member)
    depart = (date.today() - timedelta(days=1)).isoformat()
    client.post(
        "/staff/add_flight",
        data={
            "flight_number": "DL999",
            "depart_date": depart,
            "depart_time": "10:00:00",
            "depart_airport_code": "JFK",
            "arrival_date": depart,
            "arrival_time": "13:00:00",
            "arrival_airport_code": "HND",
            "base_price": "700",
            "status": "On time",
        },
    )
    with app.app_context():
        row = db.session.execute(
            text("SELECT * FROM Flight WHERE flight_number = 'DL999'")
        ).first()
    assert row is None
