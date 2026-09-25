import requests

from fastapi import HTTPException

from config import INSTAGRAM_API_VERSION
from database import get_db


# ============================================================
# INSTAGRAM PROFILE
# ============================================================
def get_instagram_profile(access_token: str):
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="Instagram access token is missing."
        )

    response = requests.get(
        f"https://graph.facebook.com/{INSTAGRAM_API_VERSION}/me",
        params={
            "fields": "id,username",
            "access_token": access_token,
        },
        timeout=30,
    )

    try:
        data = response.json()
    except ValueError:
        data = {"raw": response.text}

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Could not fetch Instagram profile.",
                "response": data,
            },
        )

    return data


# ============================================================
# SAVE ACCOUNT
# ============================================================
def save_instagram_account(user_id, instagram_user_id, username, access_token):
    connection = get_db()

    connection.execute(
        """
        INSERT INTO instagram_accounts
        (
            user_id,
            instagram_user_id,
            username,
            access_token
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, instagram_user_id)
        DO UPDATE SET
            username = excluded.username,
            access_token = excluded.access_token,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            user_id,
            str(instagram_user_id),
            username or "",
            access_token,
        ),
    )

    connection.commit()
    connection.close()

    return {"status": "saved"}


# ============================================================
# LIST ACCOUNTS
# ============================================================
def get_user_instagram_accounts(user_id: int):
    connection = get_db()

    rows = connection.execute(
        """
        SELECT
            id,
            user_id,
            instagram_user_id,
            username,
            access_token,
            created_at,
            updated_at
        FROM instagram_accounts
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# GET ACCOUNT BY USER
# ============================================================
def get_account_for_user(user_id: int, instagram_account_id: int):
    connection = get_db()

    row = connection.execute(
        """
        SELECT *
        FROM instagram_accounts
        WHERE user_id = ?
          AND id = ?
        LIMIT 1
        """,
        (user_id, instagram_account_id),
    ).fetchone()

    connection.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Instagram account not found.",
        )

    return dict(row)


# ============================================================
# SEND MESSAGE
# ============================================================
def send_instagram_message(sender_id, access_token, recipient_id, text):
    payload = {
        "recipient": {"id": str(recipient_id)},
        "message": {"text": text},
    }

    response = requests.post(
        f"https://graph.facebook.com/{INSTAGRAM_API_VERSION}/{sender_id}/messages",
        params={"access_token": access_token},
        json=payload,
        timeout=30,
    )

    try:
        data = response.json()
    except ValueError:
        data = {"raw": response.text}

    return {
        "success": response.status_code == 200,
        "status_code": response.status_code,
        "response": data,
    }
