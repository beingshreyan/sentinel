import ipaddress
import os
import traceback
import uuid
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, EmailStr, Field

from .auth import (
    create_session,
    destroy_session,
    require_admin,
    verify_admin_credentials,
)
from .sheets import append_record, get_records


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Sentinel API",
    description="Sentinel MVP backend",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# =========================================================
# MODELS
# =========================================================

class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=100,
    )

    password: str = Field(
        min_length=1,
        max_length=200,
    )


class CollectionRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    email: EmailStr

    phone: str = Field(
        min_length=3,
        max_length=30,
    )

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )

    accuracy: Optional[float] = Field(
        default=None,
        ge=0,
    )

    ipv6: Optional[str] = None

    browser: Optional[str] = None

    os: Optional[str] = None

    device: Optional[str] = None


# =========================================================
# HELPERS
# =========================================================

def get_client_ip(request: Request) -> str:
    """
    Get the directly connected client IP.

    We intentionally do not blindly trust forwarded headers
    in this MVP.
    """

    if request.client is None:
        return ""

    return request.client.host


def validate_ip(value: Optional[str]) -> Optional[str]:
    """
    Validate an IPv4 or IPv6 address.
    """

    if not value:
        return None

    try:
        ipaddress.ip_address(value)
        return value

    except ValueError:
        return None


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():
    return {
        "name": "Sentinel",
        "status": "online",
        "version": "0.1.0",
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
    }


# =========================================================
# DATA COLLECTION
# =========================================================

@app.post("/api/collect")
async def collect_data(
    data: CollectionRequest,
    request: Request,
):
    """
    Receive explicitly submitted user information and
    browser-permitted location information.

    Server-side metadata such as timestamp and request IP
    is added here.
    """

    # -----------------------------------------------------
    # Get client IP
    # -----------------------------------------------------

    client_ip = get_client_ip(request)

    validated_ip = validate_ip(client_ip)

    ipv4 = ""
    detected_ipv6 = ""

    if validated_ip:

        try:
            parsed_ip = ipaddress.ip_address(validated_ip)

            if parsed_ip.version == 4:
                ipv4 = validated_ip

            elif parsed_ip.version == 6:
                detected_ipv6 = validated_ip

        except ValueError:
            pass


    # -----------------------------------------------------
    # Browser / User Agent
    # -----------------------------------------------------

    browser = (
        data.browser
        or request.headers.get(
            "user-agent",
            "",
        )
    )


    # -----------------------------------------------------
    # Determine IPv6 value
    # -----------------------------------------------------

    ipv6 = data.ipv6 or detected_ipv6


    # -----------------------------------------------------
    # Build record
    # -----------------------------------------------------

    record = {
        "ID": str(uuid.uuid4()),

        "Timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "Name": data.name,

        "Email": str(data.email),

        "Phone": data.phone,

        "IPv4": ipv4,

        "IPv6": ipv6,

        "Network": "",

        "Browser": browser,

        "OS": data.os or "",

        "Device": data.device or "",

        "Latitude": (
            str(data.latitude)
            if data.latitude is not None
            else ""
        ),

        "Longitude": (
            str(data.longitude)
            if data.longitude is not None
            else ""
        ),

        "Accuracy": (
            str(data.accuracy)
            if data.accuracy is not None
            else ""
        ),
    }


    # -----------------------------------------------------
    # Store record in Google Sheets
    # -----------------------------------------------------

    try:

        append_record(record)

    except Exception as exc:

        print()
        print("==============================================")
        print("[SENTINEL] GOOGLE SHEETS ERROR")
        print("==============================================")
        print(
            f"Exception type: {type(exc).__name__}"
        )
        print(
            f"Exception repr: {repr(exc)}"
        )
        print(
            f"Exception message: {str(exc)}"
        )
        print("Traceback:")
        traceback.print_exc()
        print("==============================================")
        print()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to store the record.",
        )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "success": True,
        "id": record["ID"],
    }


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.post("/api/admin/login")
async def admin_login(
    data: LoginRequest,
):
    """
    Authenticate the single Sentinel administrator.
    """

    try:

        valid = verify_admin_credentials(
            data.username,
            data.password,
        )

    except RuntimeError as exc:

        print()
        print("[SENTINEL] AUTHENTICATION CONFIGURATION ERROR")
        print(f"Exception type: {type(exc).__name__}")
        print(f"Exception: {exc}")
        print()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication is not configured.",
        )


    if not valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )


    response = JSONResponse(
        content={
            "success": True,
            "message": "Authentication successful.",
        }
    )


    create_session(response)


    return response


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.post("/api/admin/logout")
async def admin_logout(
    response: Response,
    _: None = Depends(require_admin),
):
    """
    Destroy the administrator session.
    """

    destroy_session(response)

    return {
        "success": True,
        "message": "Logged out.",
    }


# =========================================================
# ADMIN AUTH CHECK
# =========================================================

@app.get("/api/admin/check")
async def admin_check(
    _: None = Depends(require_admin),
):
    """
    Check whether the current browser has a valid
    administrator session.
    """

    return {
        "authenticated": True,
    }


# =========================================================
# ADMIN DATA
# =========================================================

@app.get("/api/admin/data")
async def admin_data(
    _: None = Depends(require_admin),
):
    """
    Return all stored Sentinel records.

    This endpoint requires a valid admin session.
    """

    try:

        records = get_records()

    except Exception as exc:

        print()
        print("==============================================")
        print("[SENTINEL] GOOGLE SHEETS READ ERROR")
        print("==============================================")
        print(
            f"Exception type: {type(exc).__name__}"
        )
        print(
            f"Exception repr: {repr(exc)}"
        )
        print(
            f"Exception message: {str(exc)}"
        )
        print("Traceback:")
        traceback.print_exc()
        print("==============================================")
        print()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve records.",
        )


    return {
        "success": True,
        "count": len(records),
        "records": records,
    }