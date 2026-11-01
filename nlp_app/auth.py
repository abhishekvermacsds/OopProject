"""User registration and login.

Passwords are never stored in plain text: each one is hashed with a random
salt using PBKDF2-HMAC-SHA256 (standard library only, no extra dependencies).
Users are persisted to a JSON file so accounts survive restarts.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path

ITERATIONS = 200_000
MIN_PASSWORD_LENGTH = 8
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthError(Exception):
    """Registration / login problem. The message is safe to show to the user."""


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)


class UserStore:
    """File-backed user database."""

    def __init__(self, path: str | Path):
        self._path = Path(path)

    # ---- persistence -------------------------------------------------
    def _load(self) -> dict:
        if not self._path.exists():
            return {}
        try:
            with self._path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            raise AuthError("The user database is unreadable or corrupted.") from exc

    def _save(self, users: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temp file first so a crash can never corrupt the database.
        fd, tmp = tempfile.mkstemp(dir=self._path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2)
            os.replace(tmp, self._path)
        except Exception:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    # ---- public API --------------------------------------------------
    def register(self, name: str, email: str, password: str) -> None:
        name = name.strip()
        email = self._normalize_email(email)

        if not name:
            raise AuthError("Name cannot be empty.")
        if not EMAIL_RE.match(email):
            raise AuthError("Please enter a valid email address.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AuthError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

        users = self._load()
        if email in users:
            raise AuthError("This email is already registered. Please log in.")

        salt = os.urandom(16)
        users[email] = {
            "name": name,
            "salt": salt.hex(),
            "hash": _hash_password(password, salt).hex(),
        }
        self._save(users)

    def authenticate(self, email: str, password: str) -> str:
        """Return the user's name on success, raise AuthError otherwise."""
        email = self._normalize_email(email)
        user = self._load().get(email)

        if user is None:
            _hash_password(password, b"\x00" * 16)  # keep timing similar for unknown emails
            raise AuthError("Invalid email or password.")

        candidate = _hash_password(password, bytes.fromhex(user["salt"]))
        if not hmac.compare_digest(candidate, bytes.fromhex(user["hash"])):
            raise AuthError("Invalid email or password.")
        return user["name"]
