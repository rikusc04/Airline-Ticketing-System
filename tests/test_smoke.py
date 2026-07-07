"""End-to-end smoke test that walks every page and every flow.

Serves as a regression net: if any template stops rendering, a URL breaks,
or a form field name changes, this test fails.
"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text

from app.extensions import db

CUSTOMER_EMAIL = "smoke-customer@example.com"
CUSTOMER_PW = "SmokePassw0rd!"
STAFF_USER = "smokestaff"
STAFF_PW = "SmokeStaffPw1!"


def _register_customer(client):  # type: ignore[no-untyped-def]
    return client.post(
        "/customer/register",
        data={
            "email_address": CUSTOMER_EMAIL,
            "first_name": "Smoke",
            "last_name": "Tester",
            "password": CUSTOMER_PW,
            "building_number": "1",
            "street": "Main",
            "apt_number": "1",
            "city": "NYC",
            "state": "NY",
            "zipcode": "10001",
            "phone_number": "5555550100",
            "passport_number": "P0000001",
            "passport_expiration": "2030-01-01",
            "passport_country": "USA",
            "date_of_birth": "2000-01-01",
        },
    )


def _login_customer(client):  # type: ignore[no-untyped-def]
    return client.post(
        "/customer/login",
        data={"email_address": CUSTOMER_EMAIL, "password": CUSTOMER_PW},
    )


def _register_staff(client, airline="Delta"):  # type: ignore[no-untyped-def]
    return client.post(
        "/staff/register",
        data={
            "airline_name": airline,
            "username": STAFF_USER,
            "password": STAFF_PW,
            "first_name": "Smoke",
            "last_name": "Staff",
            "date_of_birth": "1990-01-01",
            "phone_number": "5555550101",
            "email_address": "smokestaff@example.com",
        },
    )


def _login_staff(client):  # type: ignore[no-untyped-def]
    return client.post(
        "/staff/login",
        data={"username": STAFF_USER, "password": STAFF_PW},
    )


def test_unauthenticated_pages_render(client):  # type: ignore[no-untyped-def]
    """Every anonymous-accessible page returns 200 and expected content."""
    for path, needle in [
        ("/", b"Book flights"),
        ("/customer/login", b"Welcome back"),
        ("/customer/register", b"Create your customer account"),
        ("/staff/login", b"Staff login"),
        ("/staff/register", b"Airline staff registration"),
    ]:
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"
        assert needle in resp.data, f"{path} missing expected content {needle!r}"


def test_error_pages_render(client):  # type: ignore[no-untyped-def]
    resp = client.get("/definitely-not-a-page")
    assert resp.status_code == 404
    assert b"Page not found" in resp.data


def test_full_customer_and_staff_journey(client, app):  # type: ignore[no-untyped-def]
    """Register → login → dashboards → staff adds flight → customer buys → cancels."""

    # 1. Anonymous can't reach protected pages.
    resp = client.get("/customer/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)
    resp = client.get("/staff/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)

    # 2. Register + login a customer.
    resp = _register_customer(client)
    assert resp.status_code in (301, 302)
    resp = _login_customer(client)
    assert resp.status_code in (301, 302)

    # 3. Customer dashboard renders with the seeded name and zero spending.
    resp = client.get("/customer/dashboard")
    assert resp.status_code == 200
    assert b"Welcome back, Smoke" in resp.data
    assert b"$0" in resp.data or b"$0.00" in resp.data

    # 4. Search-flights page renders (no flight yet).
    resp = client.get(
        "/customer/search_flights?airline_name=Delta&flight_number=SM100"
        "&depart_date=2030-01-01&depart_time=10:00:00"
    )
    assert resp.status_code == 200
    assert b"Search for flights" in resp.data

    # 5. Rating page renders.
    resp = client.get("/customer/rating")
    assert resp.status_code == 200
    assert b"Rate a flight" in resp.data

    # 6. Log out, register + login staff.
    client.get("/customer/logout")
    resp = _register_staff(client)
    assert resp.status_code in (301, 302)
    resp = _login_staff(client)
    assert resp.status_code in (301, 302)

    # 7. Staff dashboard renders and shows the airline badge.
    resp = client.get("/staff/dashboard")
    assert resp.status_code == 200
    assert b"Delta" in resp.data

    # 8. Seed an airplane + airport (add_airplane / add_airport routes),
    # then staff adds a future flight.
    depart = (date.today() + timedelta(days=30)).isoformat()
    resp = client.post(
        "/staff/add_airplane",
        data={
            "id_number": "SMOKE-A1",
            "num_of_seats": "100",
            "manufacturing_company": "Boeing",
            "model_number": "737",
            "manufacturing_date": "2020-01-01",
            "age": "5",
        },
    )
    assert resp.status_code in (301, 302)

    # airport JFK/HND are already seeded; use them.
    resp = client.post(
        "/staff/add_flight",
        data={
            "flight_number": "SM100",
            "depart_date": depart,
            "depart_time": "10:00:00",
            "depart_airport_code": "JFK",
            "arrival_date": depart,
            "arrival_time": "13:00:00",
            "arrival_airport_code": "HND",
            "base_price": "500",
            "status": "On time",
            "airplane_id": "SMOKE-A1",
        },
    )
    assert resp.status_code in (301, 302)

    # 9. Change status via staff route.
    resp = client.post(
        "/staff/change_flight_status",
        data={
            "flight_number": "SM100",
            "depart_date": depart,
            "depart_time": "10:00:00",
            "status": "delayed",
        },
    )
    assert resp.status_code in (301, 302)

    with app.app_context():
        row = (
            db.session.execute(
                text("SELECT status FROM Flight WHERE flight_number = 'SM100'")
            )
            .mappings()
            .first()
        )
    assert row and row["status"] == "delayed"

    # 10. Staff logs out. Customer logs back in and purchases the flight.
    client.get("/staff/logout")
    resp = _login_customer(client)
    assert resp.status_code in (301, 302)

    resp = client.post(
        "/customer/purchase_ticket",
        data={
            "airline_name": "Delta",
            "flight_number": "SM100",
            "depart_date": depart,
            "depart_time": "10:00:00",
            "first_name": "Smoke",
            "last_name": "Tester",
            "date_of_birth": "2000-01-01",
            "card_type": "credit",
            "card_number": "4111 1111 1111 4242",
            "name_on_card": "Smoke Tester",
            "expiration_date": "2030-01-01",
        },
    )
    assert resp.status_code in (301, 302)

    # 11. Dashboard now shows the future flight and non-zero spending.
    resp = client.get("/customer/dashboard")
    assert resp.status_code == 200
    assert b"SM100" in resp.data

    with app.app_context():
        ticket = (
            db.session.execute(
                text(
                    "SELECT t.id_number, p.card_last4 "
                    "FROM Ticket t JOIN Purchase p ON p.id_number = t.id_number "
                    "WHERE p.email_address = :email"
                ),
                {"email": CUSTOMER_EMAIL},
            )
            .mappings()
            .first()
        )
    assert ticket is not None
    assert ticket["card_last4"] == "4242"
    ticket_id = ticket["id_number"]

    # 12. Spending range renders with numbers now.
    resp = client.get(
        "/customer/spending_range?start_date=2020-01-01&end_date=2099-01-01"
    )
    assert resp.status_code == 200

    # 13. Cancel the ticket.
    resp = client.post(
        "/customer/cancel_ticket",
        data={"ticket_id": ticket_id},
    )
    assert resp.status_code in (301, 302)

    with app.app_context():
        still_there = db.session.execute(
            text("SELECT 1 FROM Ticket WHERE id_number = :i"),
            {"i": ticket_id},
        ).first()
    assert still_there is None, "cancel_ticket did not delete the ticket"
