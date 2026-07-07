"""Tests for customer purchase and cancel flows."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text

from app.extensions import db


def _login(client, customer):  # type: ignore[no-untyped-def]
    client.post(
        "/customer/login",
        data={
            "email_address": customer["email"],
            "password": customer["password"],
        },
    )


def _seed_flight(app, airline="Delta"):  # type: ignore[no-untyped-def]
    depart = date.today() + timedelta(days=30)
    with app.app_context():
        db.session.execute(
            text(
                "INSERT INTO Airplane "
                "(airline_name, id_number, num_of_seat, "
                "manufacturing_company, model_number, manufacturing_date, age) "
                "VALUES (:a, 'A1', 100, 'Boeing', '737', '2020-01-01', 5)"
            ),
            {"a": airline},
        )
        db.session.execute(
            text(
                "INSERT INTO Flight "
                "(airline_name, flight_number, depart_date, depart_time, "
                "depart_airport_code, arrival_date, arrival_time, "
                "arrival_airport_code, base_price, status, airplane_id_number)"
                " VALUES (:a, 'DL100', :d, '10:00:00', 'JFK', :d, '13:00:00',"
                " 'HND', 500.00, 'On time', 'A1')"
            ),
            {"a": airline, "d": depart},
        )
        db.session.commit()
    return {
        "airline_name": airline,
        "flight_number": "DL100",
        "depart_date": depart.isoformat(),
        "depart_time": "10:00:00",
    }


def test_purchase_ticket_creates_records(client, app, customer):  # type: ignore[no-untyped-def]
    flight = _seed_flight(app)
    _login(client, customer)

    resp = client.post(
        "/customer/purchase_ticket",
        data={
            **flight,
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "2000-01-01",
            "card_type": "credit",
            "card_number": "4111 1111 1111 4242",
            "name_on_card": "Test User",
            "expiration_date": "2030-01-01",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (301, 302)

    with app.app_context():
        row = (
            db.session.execute(
                text("SELECT card_last4 FROM Purchase " "WHERE email_address = :e"),
                {"e": customer["email"]},
            )
            .mappings()
            .first()
        )
    assert row is not None
    assert row["card_last4"] == "4242"


def test_purchase_masked_card_never_stores_pan(client, app, customer):  # type: ignore[no-untyped-def]
    flight = _seed_flight(app)
    _login(client, customer)
    client.post(
        "/customer/purchase_ticket",
        data={
            **flight,
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "2000-01-01",
            "card_type": "credit",
            "card_number": "4111111111114242",
            "name_on_card": "Test User",
            "expiration_date": "2030-01-01",
        },
    )
    with app.app_context():
        rows = db.session.execute(text("SELECT * FROM Purchase")).all()
    for row in rows:
        for value in row:
            assert "4111" not in str(value)
            assert "1111111111114242" not in str(value)


def test_cancel_ticket_requires_ownership(client, app, customer):  # type: ignore[no-untyped-def]
    """Someone else's ticket must not be cancellable."""
    flight = _seed_flight(app)
    _login(client, customer)
    client.post(
        "/customer/purchase_ticket",
        data={
            **flight,
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "2000-01-01",
            "card_type": "credit",
            "card_number": "4111 1111 1111 4242",
            "name_on_card": "Test User",
            "expiration_date": "2030-01-01",
        },
    )

    with app.app_context():
        ticket_id = (
            db.session.execute(text("SELECT id_number FROM Ticket"))
            .mappings()
            .first()["id_number"]
        )

    # Log out, log in as a different customer.
    from app.security import hash_password

    with app.app_context():
        db.session.execute(
            text(
                "INSERT INTO Customer "
                "(email_address, first_name, last_name, password, "
                "building_number, street, apt_number, city, state, "
                "zipcode, passport_number, passport_expiration, "
                "passport_country, date_of_birth) VALUES "
                "(:e, 'X', 'Y', :pw, 1, 'St', 1, 'C', 'S', 10001, "
                "'P0000000', '2030-01-01', 'USA', '2000-01-01')"
            ),
            {"e": "attacker@example.com", "pw": hash_password("PasswordAbc123!")},
        )
        db.session.commit()

    client.get("/customer/logout")
    client.post(
        "/customer/login",
        data={
            "email_address": "attacker@example.com",
            "password": "PasswordAbc123!",
        },
    )
    client.post("/customer/cancel_ticket", data={"ticket_id": ticket_id})

    with app.app_context():
        still_there = db.session.execute(
            text("SELECT 1 FROM Ticket WHERE id_number = :i"),
            {"i": ticket_id},
        ).first()
    assert still_there is not None, "attacker was able to cancel victim's ticket"


def test_review_rejected_without_purchase(client, app, customer):  # type: ignore[no-untyped-def]
    flight = _seed_flight(app)
    _login(client, customer)
    resp = client.post(
        "/customer/submit_rating",
        data={
            **flight,
            "rating": "5",
            "comments": "would fly again",
        },
        follow_redirects=False,
    )
    assert resp.status_code in (301, 302)
    with app.app_context():
        row = db.session.execute(text("SELECT * FROM Reviews")).first()
    assert row is None
