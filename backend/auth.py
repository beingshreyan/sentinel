import os
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
from fastapi.responses import Response
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)

load_dotenv()

SESSION_COOKIE = "sentinel_admin_session"
SESSION_MAX_AGE = 60 * 60 * 12  # 12 hours

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
SESSION_SECRET = os.getenv("SESSION_SECRET")

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "true").lower() == "true"
)

password_hasher = PasswordHasher()


def _serializer() -> URLSafeTimedSerializer:
    if not SESSION_SECRET:
        raise RuntimeError("SESSION_SECRET is not configured.")

    return URLSafeTimedSerializer(SESSION_SECRET)


def verify_admin_credentials(
    username: str,
    password: str,
) -> bool:

    if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
        raise RuntimeError(
            "ADMIN_USERNAME and ADMIN_PASSWORD_HASH "
            "must be configured."
        )

    if not secrets.compare_digest(
        username,
        ADMIN_USERNAME,
    ):
        return False

    try:
        return password_hasher.verify(
            ADMIN_PASSWORD_HASH,
            password,
        )

    except (
        VerificationError,
        InvalidHashError,
    ):
        return False


def create_session(response: Response) -> None:

    token = _serializer().dumps(
        "authenticated-admin"
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_MAX_AGE,
        httponly=True,

        # Required because Vercel and Render are
        # different sites in production.
        secure=COOKIE_SECURE,

        # Allows the browser to send the cookie
        # with cross-site HTTPS API requests.
        samesite="none" if COOKIE_SECURE else "lax",

        path="/",
    )


def destroy_session(response: Response) -> None:

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )


def require_admin(request: Request) -> None:

    cookie = request.cookies.get(
        SESSION_COOKIE
    )

    if not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:

        value = _serializer().loads(
            cookie,
            max_age=SESSION_MAX_AGE,
        )

    except (
        BadSignature,
        SignatureExpired,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    if value != "authenticated-admin":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session.",
        )
