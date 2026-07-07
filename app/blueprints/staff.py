"""Airline-staff routes: dashboard, flight/airplane/airport/maintenance CRUD."""

from __future__ import annotations

import logging
from datetime import date, datetime

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
from flask.typing import ResponseReturnValue
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..security import staff_required

log = logging.getLogger(__name__)
bp = Blueprint("staff", __name__, url_prefix="/staff")


def _airline_for(username: str) -> str | None:
    row = (
        db.session.execute(
            text("SELECT airline_name FROM Employed_By " "WHERE username = :username"),
            {"username": username},
        )
        .mappings()
        .first()
    )
    return row["airline_name"] if row else None


def _current_context() -> tuple[str, str] | None:
    username = session.get("username")
    if not username:
        return None
    airline = _airline_for(username)
    if not airline:
        return None
    return username, airline


@bp.get("/dashboard")
@staff_required
def dashboard() -> ResponseReturnValue:
    ctx = _current_context()
    if not ctx:
        session.clear()
        flash("Your account is not associated with an airline.")
        return redirect(url_for("auth.staff_login"))
    username, airline_name = ctx

    staff_row = (
        db.session.execute(
            text(
                "SELECT username, first_name, last_name, date_of_birth "
                "FROM Airline_Staff WHERE username = :username"
            ),
            {"username": username},
        )
        .mappings()
        .first()
    )
    if not staff_row:
        session.clear()
        return redirect(url_for("auth.staff_login"))

    future_flights = (
        db.session.execute(
            text(
                "SELECT * FROM Flight "
                "WHERE airline_name = :airline AND depart_date > CURDATE() "
                "ORDER BY depart_date, depart_time"
            ),
            {"airline": airline_name},
        )
        .mappings()
        .all()
    )

    reviews = (
        db.session.execute(
            text(
                "SELECT r.airline_name, r.flight_number, r.depart_date, "
                "r.depart_time, r.rating, r.comment "
                "FROM Reviews r JOIN Flight f "
                "ON r.airline_name = f.airline_name "
                "AND r.flight_number = f.flight_number "
                "AND r.depart_date = f.depart_date "
                "AND r.depart_time = f.depart_time "
                "WHERE r.airline_name = :airline "
                "ORDER BY r.depart_date DESC"
            ),
            {"airline": airline_name},
        )
        .mappings()
        .all()
    )

    top = (
        db.session.execute(
            text(
                "SELECT p.email_address, COUNT(*) AS purchase_count "
                "FROM Purchase p JOIN Ticket t "
                "ON p.id_number = t.id_number "
                "WHERE t.airline_name = :airline "
                "AND p.purchase_date >= "
                "DATE_SUB(CURDATE(), INTERVAL 1 YEAR) "
                "GROUP BY p.email_address "
                "ORDER BY purchase_count DESC LIMIT 1"
            ),
            {"airline": airline_name},
        )
        .mappings()
        .first()
    )

    customer_info = None
    ticket_count = None
    if top:
        ticket_count = top["purchase_count"]
        customer_info = (
            db.session.execute(
                text(
                    "SELECT email_address, first_name, last_name "
                    "FROM Customer WHERE email_address = :email"
                ),
                {"email": top["email_address"]},
            )
            .mappings()
            .first()
        )

    return render_template(
        "airline_staff_dashboard.html",
        staff=staff_row,
        airline_name=airline_name,
        future_flights=[dict(r) for r in future_flights],
        reviews=[dict(r) for r in reviews],
        ticket_count=ticket_count,
        customer_info=customer_info,
    )


@bp.post("/add_flight")
@staff_required
def add_flight() -> ResponseReturnValue:
    ctx = _current_context()
    if not ctx:
        abort(403)
    _, airline_name = ctx
    form = request.form

    try:
        depart_dt = datetime.strptime(form.get("depart_date") or "", "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid depart date.")
        return redirect(url_for("staff.dashboard"))

    if depart_dt <= date.today():
        flash("Departure date must be in the future.")
        return redirect(url_for("staff.dashboard"))

    params = {
        "airline": airline_name,
        "flight_number": form.get("flight_number") or "",
        "depart_date": form.get("depart_date"),
        "depart_time": form.get("depart_time"),
        "depart_airport": form.get("depart_airport_code") or "",
        "arrival_date": form.get("arrival_date"),
        "arrival_time": form.get("arrival_time"),
        "arrival_airport": form.get("arrival_airport_code") or "",
        "base_price": form.get("base_price") or 0,
        "status": form.get("status") or "On time",
        "airplane_id": form.get("airplane_id") or None,
    }

    try:
        db.session.execute(
            text(
                "INSERT INTO Flight "
                "(airline_name, flight_number, depart_date, depart_time, "
                "depart_airport_code, arrival_date, arrival_time, "
                "arrival_airport_code, base_price, status, airplane_id_number)"
                " VALUES (:airline, :flight_number, :depart_date, "
                ":depart_time, :depart_airport, :arrival_date, "
                ":arrival_time, :arrival_airport, :base_price, :status, "
                ":airplane_id)"
            ),
            params,
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Flight already exists.")
        return redirect(url_for("staff.dashboard"))
    except Exception:
        db.session.rollback()
        log.exception("add_flight failed")
        flash("Could not add flight.")
        return redirect(url_for("staff.dashboard"))

    flash("Flight added.")
    return redirect(url_for("staff.dashboard"))


@bp.post("/change_flight_status")
@staff_required
def change_flight_status() -> ResponseReturnValue:
    ctx = _current_context()
    if not ctx:
        abort(403)
    _, airline_name = ctx
    form = request.form

    result = db.session.execute(
        text(
            "UPDATE Flight SET status = :status "
            "WHERE airline_name = :airline "
            "AND flight_number = :flight_number "
            "AND depart_date = :depart_date "
            "AND depart_time = :depart_time"
        ),
        {
            "status": form.get("status") or "",
            "airline": airline_name,
            "flight_number": form.get("flight_number") or "",
            "depart_date": form.get("depart_date"),
            "depart_time": form.get("depart_time"),
        },
    )
    db.session.commit()

    if result.rowcount == 0:
        flash("Flight not found for your airline.")
    else:
        flash("Flight status updated.")
    return redirect(url_for("staff.dashboard"))


@bp.post("/add_airport")
@staff_required
def add_airport() -> ResponseReturnValue:
    form = request.form
    try:
        db.session.execute(
            text(
                "INSERT INTO Airport "
                "(code, name, city, country, number_of_terminals, type) "
                "VALUES (:code, :name, :city, :country, :terminals, :type)"
            ),
            {
                "code": (form.get("code") or "").upper(),
                "name": form.get("name") or "",
                "city": form.get("city") or "",
                "country": form.get("country") or "",
                "terminals": form.get("number_of_terminals") or 0,
                "type": form.get("type") or "",
            },
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Airport already exists.")
        return redirect(url_for("staff.dashboard"))

    flash("Airport added.")
    return redirect(url_for("staff.dashboard"))


@bp.post("/add_airplane")
@staff_required
def add_airplane() -> ResponseReturnValue:
    ctx = _current_context()
    if not ctx:
        abort(403)
    _, airline_name = ctx
    form = request.form

    try:
        db.session.execute(
            text(
                "INSERT INTO Airplane "
                "(airline_name, id_number, maintenance_id, num_of_seat, "
                "manufacturing_company, model_number, manufacturing_date, "
                "age) VALUES (:airline, :id, NULL, :seats, :company, "
                ":model, :manufactured, :age)"
            ),
            {
                "airline": airline_name,
                "id": form.get("id_number") or "",
                "seats": form.get("num_of_seats") or 0,
                "company": form.get("manufacturing_company") or "",
                "model": form.get("model_number") or "",
                "manufactured": form.get("manufacturing_date"),
                "age": form.get("age") or 0,
            },
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Airplane already exists.")
        return redirect(url_for("staff.dashboard"))

    flash("Airplane added.")
    return redirect(url_for("staff.dashboard"))


@bp.post("/schedule_maintenance")
@staff_required
def schedule_maintenance() -> ResponseReturnValue:
    ctx = _current_context()
    if not ctx:
        abort(403)
    _, airline_name = ctx
    form = request.form
    maintenance_id = form.get("maintenance_id") or ""
    airplane_id = form.get("airplane_id") or ""

    if not maintenance_id or not airplane_id:
        flash("Maintenance and airplane IDs are required.")
        return redirect(url_for("staff.dashboard"))

    try:
        db.session.execute(
            text(
                "INSERT INTO Maintenance "
                "(id, start_date, start_time, end_date, end_time) "
                "VALUES (:id, :start_date, :start_time, :end_date, :end_time)"
            ),
            {
                "id": maintenance_id,
                "start_date": form.get("start_date"),
                "start_time": form.get("start_time"),
                "end_date": form.get("end_date"),
                "end_time": form.get("end_time"),
            },
        )
        db.session.execute(
            text(
                "UPDATE Airplane SET maintenance_id = :mid "
                "WHERE airline_name = :airline AND id_number = :aid"
            ),
            {
                "mid": maintenance_id,
                "airline": airline_name,
                "aid": airplane_id,
            },
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Maintenance record already exists.")
        return redirect(url_for("staff.dashboard"))

    flash("Maintenance scheduled.")
    return redirect(url_for("staff.dashboard"))
