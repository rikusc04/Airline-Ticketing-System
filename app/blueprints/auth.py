"""Authentication routes for customers and airline staff."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
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
from ..security import (
    hash_password,
    validate_password_strength,
    verify_password,
)

log = logging.getLogger(__name__)
bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------


@bp.route("/customer/login", methods=["GET", "POST"])
def customer_login() -> ResponseReturnValue:
    if request.method == "POST":
        email = (request.form.get("email_address") or "").strip().lower()
        password = request.form.get("password") or ""

        row = (
            db.session.execute(
                text("SELECT password FROM Customer " "WHERE email_address = :email"),
                {"email": email},
            )
            .mappings()
            .first()
        )
        stored_hash = row["password"] if row else ""

        if verify_password(password, stored_hash):
            session.clear()
            session["email"] = email
            return redirect(url_for("customer.dashboard"))

        # Deliberately generic to avoid user enumeration.
        flash("Invalid email or password.")
        return render_template("customer_login_page.html"), 401

    return render_template("customer_login_page.html")


@bp.route("/customer/register", methods=["GET", "POST"])
def customer_register() -> ResponseReturnValue:
    if request.method == "POST":
        form = request.form
        email = (form.get("email_address") or "").strip().lower()
        password = form.get("password") or ""

        pw_err = validate_password_strength(password)
        if pw_err:
            flash(pw_err)
            return (
                render_template("registration_for_customer_page.html"),
                400,
            )

        params = {
            "email": email,
            "first_name": form.get("first_name") or "",
            "last_name": form.get("last_name") or "",
            "password": hash_password(password),
            "building_number": form.get("building_number") or 0,
            "street": form.get("street") or "",
            "apt_number": form.get("apt_number") or 0,
            "city": form.get("city") or "",
            "state": form.get("state") or "",
            "zipcode": form.get("zipcode") or 0,
            "passport_number": form.get("passport_number") or "",
            "passport_expiration": form.get("passport_expiration"),
            "passport_country": form.get("passport_country") or "",
            "date_of_birth": form.get("date_of_birth"),
        }
        phone = form.get("phone_number") or ""

        try:
            db.session.execute(
                text(
                    "INSERT INTO Customer "
                    "(email_address, first_name, last_name, password, "
                    "building_number, street, apt_number, city, state, "
                    "zipcode, passport_number, passport_expiration, "
                    "passport_country, date_of_birth) VALUES "
                    "(:email, :first_name, :last_name, :password, "
                    ":building_number, :street, :apt_number, :city, :state, "
                    ":zipcode, :passport_number, :passport_expiration, "
                    ":passport_country, :date_of_birth)"
                ),
                params,
            )
            if phone:
                db.session.execute(
                    text(
                        "INSERT INTO CustomerPhone "
                        "(email_address, phone_number) VALUES "
                        "(:email, :phone)"
                    ),
                    {"email": email, "phone": phone},
                )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with this email already exists.")
            return (
                render_template("registration_for_customer_page.html"),
                409,
            )

        flash("Account created — please log in.")
        return redirect(url_for("auth.customer_login"))

    return render_template("registration_for_customer_page.html")


@bp.get("/customer/logout")
def customer_logout() -> ResponseReturnValue:
    session.pop("email", None)
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# Airline staff
# ---------------------------------------------------------------------------


@bp.route("/staff/login", methods=["GET", "POST"])
def staff_login() -> ResponseReturnValue:
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        row = (
            db.session.execute(
                text(
                    "SELECT password FROM Airline_Staff " "WHERE username = :username"
                ),
                {"username": username},
            )
            .mappings()
            .first()
        )
        stored_hash = row["password"] if row else ""

        if verify_password(password, stored_hash):
            session.clear()
            session["username"] = username
            return redirect(url_for("staff.dashboard"))

        flash("Invalid username or password.")
        return render_template("airline_staff_login_page.html"), 401

    return render_template("airline_staff_login_page.html")


@bp.route("/staff/register", methods=["GET", "POST"])
def staff_register() -> ResponseReturnValue:
    if request.method == "POST":
        form = request.form
        username = (form.get("username") or "").strip()
        password = form.get("password") or ""
        airline_name = (form.get("airline_name") or "").strip()

        pw_err = validate_password_strength(password)
        if pw_err:
            flash(pw_err)
            return (
                render_template("registration_for_airline_staff_page.html"),
                400,
            )

        airline_exists = (
            db.session.execute(
                text("SELECT 1 FROM Airline WHERE name = :name"),
                {"name": airline_name},
            )
            .mappings()
            .first()
        )
        if not airline_exists:
            flash("Unknown airline. Contact an administrator.")
            return (
                render_template("registration_for_airline_staff_page.html"),
                400,
            )

        try:
            db.session.execute(
                text(
                    "INSERT INTO Airline_Staff "
                    "(username, password, first_name, last_name, "
                    "date_of_birth) VALUES "
                    "(:username, :password, :first_name, :last_name, :dob)"
                ),
                {
                    "username": username,
                    "password": hash_password(password),
                    "first_name": form.get("first_name") or "",
                    "last_name": form.get("last_name") or "",
                    "dob": form.get("date_of_birth"),
                },
            )
            email = form.get("email_address") or ""
            if email:
                db.session.execute(
                    text(
                        "INSERT INTO Airline_Staff_Email_Address "
                        "(username, email_address) VALUES "
                        "(:username, :email)"
                    ),
                    {"username": username, "email": email},
                )
            phone = form.get("phone_number") or ""
            if phone:
                db.session.execute(
                    text(
                        "INSERT INTO Airline_Staff_Phone_Number "
                        "(username, phone_number) VALUES "
                        "(:username, :phone)"
                    ),
                    {"username": username, "phone": phone},
                )
            db.session.execute(
                text(
                    "INSERT INTO Employed_By (airline_name, username) VALUES "
                    "(:airline, :username)"
                ),
                {"airline": airline_name, "username": username},
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("A staff account with this username already exists.")
            return (
                render_template("registration_for_airline_staff_page.html"),
                409,
            )

        flash("Account created — please log in.")
        return redirect(url_for("auth.staff_login"))

    return render_template("registration_for_airline_staff_page.html")


@bp.get("/staff/logout")
def staff_logout() -> ResponseReturnValue:
    session.pop("username", None)
    return redirect(url_for("main.index"))
