"""Authentication + password helpers."""

from __future__ import annotations

import re
import secrets
from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import flash, redirect, session, url_for

from .extensions import bcrypt

# Bcrypt hashes are ~60 chars; schema allows 300 which is generous.
_PASSWORD_MIN_LEN = 12
_PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


def hash_password(plaintext: str) -> str:
    return bcrypt.generate_password_hash(plaintext).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    if not hashed:
        # Defend against empty hash comparison (e.g. account never set password).
        # Still run bcrypt against a dummy hash to keep timing constant.
        bcrypt.check_password_hash(
            "$2b$12$abcdefghijklmnopqrstuu", "not-a-real-password"
        )
        return False
    try:
        return bcrypt.check_password_hash(hashed, plaintext)
    except ValueError:
        # Legacy or corrupted hash — treat as auth failure.
        return False


def validate_password_strength(password: str) -> str | None:
    if len(password) < _PASSWORD_MIN_LEN:
        return f"Password must be at least {_PASSWORD_MIN_LEN} characters."
    if not _PASSWORD_RE.match(password):
        return "Password must contain both letters and digits."
    return None


def mask_card_number(card_number: str) -> str:
    """Return the last 4 digits of a card number, discarding the rest.

    We never store the full PAN — that would require PCI compliance and is
    absolutely never appropriate for this app's threat model.
    """
    digits = re.sub(r"\D", "", card_number or "")
    return digits[-4:] if len(digits) >= 4 else ""


def generate_ticket_id() -> str:
    """Generate a collision-resistant ticket id (fits varchar(20))."""
    return secrets.token_hex(8)  # 16 chars


def customer_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not session.get("email"):
            flash("Please log in to continue.")
            return redirect(url_for("auth.customer_login"))
        return view(*args, **kwargs)

    return wrapper


def staff_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not session.get("username"):
            flash("Please log in to continue.")
            return redirect(url_for("auth.staff_login"))
        return view(*args, **kwargs)

    return wrapper
