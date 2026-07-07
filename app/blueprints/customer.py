"""Customer-facing routes: dashboard, search, purchase, cancel, review."""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import text

from ..extensions import db
from ..security import (
    customer_required,
    generate_ticket_id,
    mask_card_number,
)

log = logging.getLogger(__name__)
bp = Blueprint("customer", __name__, url_prefix="/customer")


def _get_customer_row(email: str) -> dict | None:
    return (
        db.session.execute(
            text(
                "SELECT email_address, first_name, last_name, "
                "building_number, street, apt_number, city, state, zipcode, "
                "passport_number, passport_expiration, passport_country, "
                "date_of_birth FROM Customer WHERE email_address = :email"
            ),
            {"email": email},
        )
        .mappings()
        .first()
    )


def _get_future_flights(email: str) -> list[dict]:
    rows = (
        db.session.execute(
            text(
                "SELECT t.id_number, t.airline_name, t.flight_number, "
                "t.depart_date, t.depart_time "
                "FROM Purchase p JOIN Ticket t ON p.id_number = t.id_number "
                "WHERE p.email_address = :email "
                "AND t.depart_date >= CURDATE() "
                "ORDER BY t.depart_date, t.depart_time"
            ),
            {"email": email},
        )
        .mappings()
        .all()
    )
    return [dict(r) for r in rows]


def _get_spending(
    email: str, start: str | None = None, end: str | None = None
) -> Decimal:
    if start and end:
        sql = (
            "SELECT COALESCE(SUM(Ticket.sold_price), 0) AS total "
            "FROM Purchase JOIN Ticket "
            "ON Purchase.id_number = Ticket.id_number "
            "WHERE Purchase.email_address = :email "
            "AND Purchase.purchase_date BETWEEN :start AND :end"
        )
        params = {"email": email, "start": start, "end": end}
    else:
        sql = (
            "SELECT COALESCE(SUM(Ticket.sold_price), 0) AS total "
            "FROM Purchase JOIN Ticket "
            "ON Purchase.id_number = Ticket.id_number "
            "WHERE Purchase.email_address = :email "
            "AND Purchase.purchase_date >= "
            "DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
        )
        params = {"email": email}

    row = db.session.execute(text(sql), params).mappings().first()
    return row["total"] if row else Decimal("0")


@bp.get("/dashboard")
@customer_required
def dashboard() -> object:
    email = session["email"]
    customer_row = _get_customer_row(email)
    if not customer_row:
        session.clear()
        flash("Your account is no longer available. Please log in.")
        return redirect(url_for("auth.customer_login"))

    return render_template(
        "customer_dashboard.html",
        customer=customer_row,
        spendings_past_year=_get_spending(email),
        future_flights=_get_future_flights(email),
    )


@bp.get("/search_flights")
@customer_required
def search_flights() -> object:
    email = session["email"]
    customer_row = _get_customer_row(email)
    if not customer_row:
        abort(404)

    airline_name = request.args.get("airline_name")
    flight_number = request.args.get("flight_number")
    depart_date = request.args.get("depart_date")
    depart_time = request.args.get("depart_time")

    found_flight: list[dict] = []
    if all([airline_name, flight_number, depart_date, depart_time]):
        rows = (
            db.session.execute(
                text(
                    "SELECT * FROM Flight WHERE airline_name = :airline "
                    "AND flight_number = :flight AND depart_date = :date "
                    "AND depart_time = :time"
                ),
                {
                    "airline": airline_name,
                    "flight": flight_number,
                    "date": depart_date,
                    "time": depart_time,
                },
            )
            .mappings()
            .all()
        )
        found_flight = [dict(r) for r in rows]

    return render_template(
        "customer_dashboard.html",
        customer=customer_row,
        spendings_past_year=_get_spending(email),
        future_flights=_get_future_flights(email),
        found_flight=found_flight,
    )


@bp.get("/spending_range")
@customer_required
def spending_range() -> object:
    email = session["email"]
    customer_row = _get_customer_row(email)
    if not customer_row:
        abort(404)

    start = request.args.get("start_date") or None
    end = request.args.get("end_date") or None

    range_spending: Decimal | None = None
    if start and end:
        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for("customer.dashboard"))
        range_spending = _get_spending(email, start, end)

    return render_template(
        "customer_dashboard.html",
        customer=customer_row,
        start_date=start,
        end_date=end,
        spendings_past_year=_get_spending(email),
        range_spending=range_spending,
        future_flights=_get_future_flights(email),
    )


@bp.post("/purchase_ticket")
@customer_required
def purchase_ticket() -> object:
    email = session["email"]
    form = request.form

    airline_name = form.get("airline_name")
    flight_number = form.get("flight_number")
    depart_date = form.get("depart_date")
    depart_time = form.get("depart_time")
    if not all([airline_name, flight_number, depart_date, depart_time]):
        flash("Missing flight details.")
        return redirect(url_for("customer.dashboard"))

    # Compute a discounted price atomically, then insert.
    flight = (
        db.session.execute(
            text(
                "SELECT f.base_price, f.airplane_id_number, "
                "COALESCE(a.num_of_seat, 0) AS num_of_seat "
                "FROM Flight f "
                "LEFT JOIN Airplane a "
                "ON f.airplane_id_number = a.id_number "
                "AND f.airline_name = a.airline_name "
                "WHERE f.airline_name = :airline "
                "AND f.flight_number = :flight "
                "AND f.depart_date = :date "
                "AND f.depart_time = :time"
            ),
            {
                "airline": airline_name,
                "flight": flight_number,
                "date": depart_date,
                "time": depart_time,
            },
        )
        .mappings()
        .first()
    )
    if not flight:
        flash("Flight not found.")
        return redirect(url_for("customer.dashboard"))

    total_seats = flight["num_of_seat"] or 0
    if total_seats <= 0:
        flash("Flight has no seats assigned.")
        return redirect(url_for("customer.dashboard"))

    taken_row = (
        db.session.execute(
            text(
                "SELECT COUNT(*) AS n FROM Ticket "
                "WHERE airline_name = :airline "
                "AND flight_number = :flight "
                "AND depart_date = :date "
                "AND depart_time = :time"
            ),
            {
                "airline": airline_name,
                "flight": flight_number,
                "date": depart_date,
                "time": depart_time,
            },
        )
        .mappings()
        .first()
    )
    taken = int(taken_row["n"]) if taken_row else 0
    if taken >= total_seats:
        flash("This flight is fully booked.")
        return redirect(url_for("customer.dashboard"))

    price = Decimal(flight["base_price"])
    if taken / total_seats >= 0.8:
        price = (price * Decimal("0.75")).quantize(Decimal("0.01"))

    ticket_id = generate_ticket_id()
    card_last4 = mask_card_number(form.get("card_number") or "")
    if not card_last4:
        flash("Invalid card number.")
        return redirect(url_for("customer.dashboard"))

    try:
        db.session.execute(
            text(
                "INSERT INTO Ticket "
                "(id_number, airline_name, flight_number, depart_date, "
                "depart_time, sold_price, first_name, last_name, "
                "date_of_birth) VALUES "
                "(:id, :airline, :flight, :date, :time, :price, "
                ":first_name, :last_name, :dob)"
            ),
            {
                "id": ticket_id,
                "airline": airline_name,
                "flight": flight_number,
                "date": depart_date,
                "time": depart_time,
                "price": price,
                "first_name": form.get("first_name") or "",
                "last_name": form.get("last_name") or "",
                "dob": form.get("date_of_birth"),
            },
        )
        db.session.execute(
            text(
                "INSERT INTO Purchase "
                "(id_number, email_address, purchase_time, purchase_date, "
                "card_type, card_last4, name_on_card, expiration_date) "
                "VALUES (:id, :email, CURTIME(), CURDATE(), "
                ":card_type, :card_last4, :name_on_card, :expiration_date)"
            ),
            {
                "id": ticket_id,
                "email": email,
                "card_type": form.get("card_type") or "",
                "card_last4": card_last4,
                "name_on_card": form.get("name_on_card") or "",
                "expiration_date": form.get("expiration_date"),
            },
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        log.exception("purchase failed for %s", email)
        flash("Could not complete purchase — please try again.")
        return redirect(url_for("customer.dashboard"))

    flash("Ticket purchased.")
    return redirect(url_for("customer.dashboard"))


@bp.post("/cancel_ticket")
@customer_required
def cancel_ticket() -> object:
    email = session["email"]
    ticket_id = (request.form.get("ticket_id") or "").strip()
    if not ticket_id:
        flash("Ticket ID required.")
        return redirect(url_for("customer.dashboard"))

    ticket = (
        db.session.execute(
            text(
                "SELECT t.depart_date FROM Ticket t "
                "JOIN Purchase p ON p.id_number = t.id_number "
                "WHERE t.id_number = :id AND p.email_address = :email"
            ),
            {"id": ticket_id, "email": email},
        )
        .mappings()
        .first()
    )
    if not ticket:
        flash("Ticket not found or not owned by you.")
        return redirect(url_for("customer.dashboard"))

    if ticket["depart_date"] <= date.today():
        flash("Cannot cancel a ticket for today or a past date.")
        return redirect(url_for("customer.dashboard"))

    try:
        db.session.execute(
            text(
                "DELETE FROM Trips WHERE outbound_ticket_id = :id "
                "OR return_ticket_id = :id"
            ),
            {"id": ticket_id},
        )
        db.session.execute(
            text("DELETE FROM Purchase WHERE id_number = :id"),
            {"id": ticket_id},
        )
        db.session.execute(
            text("DELETE FROM Ticket WHERE id_number = :id"),
            {"id": ticket_id},
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        log.exception("cancel failed for ticket %s", ticket_id)
        flash("Could not cancel ticket.")
        return redirect(url_for("customer.dashboard"))

    flash("Ticket cancelled.")
    return redirect(url_for("customer.dashboard"))


@bp.get("/rating")
@customer_required
def rating() -> object:
    return render_template("rating.html")


@bp.post("/submit_rating")
@customer_required
def submit_rating() -> object:
    email = session["email"]
    form = request.form
    airline_name = form.get("airline_name")
    flight_number = form.get("flight_number")
    depart_date = form.get("depart_date")
    depart_time = form.get("depart_time")
    rating_val = form.get("rating")
    comments = form.get("comments") or ""

    if not all([airline_name, flight_number, depart_date, depart_time, rating_val]):
        flash("All rating fields are required.")
        return redirect(url_for("customer.dashboard"))

    try:
        rating_num = Decimal(rating_val)
    except (TypeError, ValueError):
        flash("Invalid rating.")
        return redirect(url_for("customer.dashboard"))
    if not (Decimal("0") <= rating_num <= Decimal("10")):
        flash("Rating must be between 0 and 10.")
        return redirect(url_for("customer.dashboard"))

    # Must have flown the flight (i.e. have a Purchase+Ticket) and it must be
    # in the past.
    flew = (
        db.session.execute(
            text(
                "SELECT 1 FROM Purchase p JOIN Ticket t "
                "ON p.id_number = t.id_number "
                "WHERE p.email_address = :email "
                "AND t.airline_name = :airline "
                "AND t.flight_number = :flight "
                "AND t.depart_date = :date "
                "AND t.depart_time = :time "
                "AND (t.depart_date < CURDATE() OR "
                "(t.depart_date = CURDATE() AND t.depart_time < CURTIME()))"
            ),
            {
                "email": email,
                "airline": airline_name,
                "flight": flight_number,
                "date": depart_date,
                "time": depart_time,
            },
        )
        .mappings()
        .first()
    )
    if not flew:
        flash("You can only review flights you have taken.")
        return redirect(url_for("customer.dashboard"))

    try:
        db.session.execute(
            text(
                "INSERT INTO Reviews (email_address, airline_name, "
                "flight_number, depart_date, depart_time, rating, comment) "
                "VALUES (:email, :airline, :flight, :date, :time, "
                ":rating, :comment) "
                "ON DUPLICATE KEY UPDATE rating = VALUES(rating), "
                "comment = VALUES(comment)"
            ),
            {
                "email": email,
                "airline": airline_name,
                "flight": flight_number,
                "date": depart_date,
                "time": depart_time,
                "rating": rating_num,
                "comment": comments,
            },
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        log.exception("rating submit failed")
        flash("Could not save review.")
        return redirect(url_for("customer.dashboard"))

    flash("Thanks for your review!")
    return redirect(url_for("customer.dashboard"))
