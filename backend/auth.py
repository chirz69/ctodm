import hashlib
import secrets
import time

import requests

from fastapi import HTTPException

from database import get_db

from config import (
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_REDIRECT_URI,
    INSTAGRAM_API_VERSION,
)


# ============================================================
# SIMPLE PASSWORD HASH
# ============================================================

def hash_password(
    password: str
):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    email: str,
    password: str
):

    email = email.strip().lower()


    if not email:

        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )


    if not password:

        raise HTTPException(
            status_code=400,
            detail="Password is required."
        )


    connection = get_db()


    existing = connection.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()


    if existing:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )


    password_hash = hash_password(
        password
    )


    cursor = connection.execute(
        """
        INSERT INTO users
        (
            email,
            password_hash
        )
        VALUES (?, ?)
        """,
        (
            email,
            password_hash
        )
    )


    connection.commit()


    user_id = cursor.lastrowid


    connection.close()


    return {
        "id": user_id,
        "email": email
    }


# ============================================================
# LOGIN
# ============================================================

def login_user(
    email: str,
    password: str
):

    email = email.strip().lower()


    password_hash = hash_password(
        password
    )


    connection = get_db()


    user = connection.execute(
        """
        SELECT
            id,
            email
        FROM users
        WHERE
            email = ?
            AND password_hash = ?
        """,
        (
            email,
            password_hash
        )
    ).fetchone()


    connection.close()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    return {
        "id": user["id"],
        "email": user["email"]
    }


# ============================================================
# TEMPORARY LOCAL SESSION
# ============================================================
#
# This is intentionally simple for development.
#
# Before production we will replace this with proper
# signed/JWT sessions and secure password hashing such
# as Argon2/bcrypt.
#
# ============================================================

SESSIONS = {}


def create_session(
    user_id: int
):

    token = secrets.token_urlsafe(
        32
    )


    SESSIONS[token] = {
        "user_id": user_id,
        "created_at": time.time()
    }


    return token


def get_user_from_session(
    token: str
):

    session = SESSIONS.get(
        token
    )


    if not session:

        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )


    return session["user_id"]


def delete_session(
    token: str
):

    SESSIONS.pop(
        token,
        None
    )


# ============================================================
# INSTAGRAM OAUTH URL
# ============================================================

def get_instagram_login_url(
    state: str
):

    if not INSTAGRAM_APP_ID:

        raise HTTPException(
            status_code=500,
            detail="Instagram App ID is not configured."
        )


    permissions = ",".join(
        [
            "instagram_business_basic",
            "instagram_business_manage_comments",
            "instagram_business_manage_messages"
        ]
    )


    url = (
        "https://www.instagram.com/oauth/authorize"
        f"?client_id={INSTAGRAM_APP_ID}"
        f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
        "&response_type=code"
        f"&scope={permissions}"
        f"&state={state}"
    )


    return url


# ============================================================
# EXCHANGE OAUTH CODE
# ============================================================

def exchange_instagram_code(
    code: str
):

    if not INSTAGRAM_APP_ID:

        raise HTTPException(
            status_code=500,
            detail="Instagram App ID missing."
        )


    if not INSTAGRAM_APP_SECRET:

        raise HTTPException(
            status_code=500,
            detail="Instagram App Secret missing."
        )


    response = requests.post(

        "https://api.instagram.com/oauth/access_token",

        data={
            "client_id":
                INSTAGRAM_APP_ID,

            "client_secret":
                INSTAGRAM_APP_SECRET,

            "grant_type":
                "authorization_code",

            "redirect_uri":
                INSTAGRAM_REDIRECT_URI,

            "code":
                code
        },

        timeout=30
    )


    try:

        data = response.json()

    except Exception:

        data = {
            "raw": response.text
        }


    if response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail={
                "message":
                    "Instagram OAuth failed.",
                "response":
                    data
            }
        )


    return data