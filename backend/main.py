from fastapi import (
    FastAPI,
    Request,
    Header,
    Query
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.responses import (
    RedirectResponse,
    JSONResponse
)

from pydantic import BaseModel

import secrets


from config import (
    FRONTEND_URL,
    INSTAGRAM_VERIFY_TOKEN
)


from database import (
    create_database,
    get_db
)


from auth import (
    create_user,
    login_user,
    create_session,
    get_user_from_session,
    delete_session,
    get_instagram_login_url,
    exchange_instagram_code
)


from instagram import (
    get_instagram_profile,
    save_instagram_account,
    get_user_instagram_accounts,
    get_account_for_user
)


from webhooks import (
    process_webhook_payload
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Comment2DM",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)


# ============================================================
# DATABASE
# ============================================================

create_database()


# ============================================================
# REQUEST MODELS
# ============================================================

class RegisterRequest(BaseModel):

    email: str

    password: str


class LoginRequest(BaseModel):

    email: str

    password: str


class CampaignRequest(BaseModel):

    instagram_account_id: int

    keyword: str

    product_url: str

    dm_message: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "Comment2DM API is running!"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status":
            "ok"
    }


# ============================================================
# REGISTER
# ============================================================

@app.post("/api/auth/register")
def register(
    request: RegisterRequest
):

    user = create_user(

        request.email,

        request.password
    )


    token = create_session(
        user["id"]
    )


    return {

        "message":
            "Account created.",

        "token":
            token,

        "user":
            user
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/auth/login")
def login(
    request: LoginRequest
):

    user = login_user(

        request.email,

        request.password
    )


    token = create_session(
        user["id"]
    )


    return {

        "message":
            "Login successful.",

        "token":
            token,

        "user":
            user
    }


# ============================================================
# LOGOUT
# ============================================================

@app.post("/api/auth/logout")
def logout(
    authorization: str | None = Header(
        default=None
    )
):

    if authorization:

        token = authorization.replace(
            "Bearer ",
            ""
        )

        delete_session(
            token
        )


    return {
        "message":
            "Logged out."
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/api/auth/me")
def current_user(
    authorization: str | None = Header(
        default=None
    )
):

    if not authorization:

        raise_exception = True

    else:

        raise_exception = False


    if raise_exception:

        return JSONResponse(
            status_code=401,
            content={
                "error":
                    "Not authenticated."
            }
        )


    token = authorization.replace(
        "Bearer ",
        ""
    )


    user_id = get_user_from_session(
        token
    )


    connection = get_db()


    user = connection.execute(
        """
        SELECT
            id,
            email,
            created_at
        FROM users
        WHERE id = ?
        """,
        (
            user_id,
        )
    ).fetchone()


    connection.close()


    if not user:

        return JSONResponse(
            status_code=404,
            content={
                "error":
                    "User not found."
            }
        )


    return dict(user)


# ============================================================
# INSTAGRAM CONNECT
# ============================================================

@app.get("/auth/instagram")
def instagram_login(
    session: str | None = None
):

    if not session:

        return JSONResponse(
            status_code=401,
            content={
                "error":
                    "Login to Comment2DM first."
            }
        )


    user_id = get_user_from_session(
        session
    )


    state = (
        f"{user_id}:"
        f"{secrets.token_urlsafe(24)}"
    )


    url = get_instagram_login_url(
        state
    )


    return RedirectResponse(
        url=url
    )
# ============================================================
# INSTAGRAM CALLBACK
# ============================================================

@app.get("/auth/instagram/callback")
def instagram_callback(

    code: str | None = None,

    state: str | None = None,

    error: str | None = None,

    error_reason: str | None = None,

    error_description: str | None = None
):

    if error:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"{error_description or error}"
            )
        )


    if not code:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"missing_code"
            )
        )


    if not state:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"missing_state"
            )
        )


    # --------------------------------------------------------
    # Get user ID from state
    # --------------------------------------------------------

    try:

        user_id = int(
            state.split(":")[0]
        )

    except Exception:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"invalid_state"
            )
        )


    # --------------------------------------------------------
    # Exchange code
    # --------------------------------------------------------

    try:

        token_data = exchange_instagram_code(
            code
        )

    except Exception as error:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"oauth_failed"
            )
        )


    access_token = token_data.get(
        "access_token"
    )


    if not access_token:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"missing_token"
            )
        )


    # --------------------------------------------------------
    # Get Instagram profile
    # --------------------------------------------------------

    try:

        profile = get_instagram_profile(
            access_token
        )

    except Exception:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"profile_failed"
            )
        )


    instagram_user_id = profile.get(
        "id"
    )


    username = profile.get(
        "username",
        ""
    )


    if not instagram_user_id:

        return RedirectResponse(

            url=(
                f"{FRONTEND_URL}"
                f"/?instagram_error="
                f"missing_instagram_id"
            )
        )


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_instagram_account(

        user_id,

        instagram_user_id,

        username,

        access_token
    )


    # --------------------------------------------------------
    # Back to React
    # --------------------------------------------------------

    return RedirectResponse(

        url=(
            f"{FRONTEND_URL}"
            f"/?instagram=connected"
        )
    )


# ============================================================
# INSTAGRAM ACCOUNTS
# ============================================================

@app.get("/api/instagram/accounts")
def instagram_accounts(
    authorization: str | None = Header(
        default=None
    )
):

    if not authorization:

        return JSONResponse(
            status_code=401,
            content={
                "error":
                    "Not authenticated."
            }
        )


    token = authorization.replace(
        "Bearer ",
        ""
    )


    user_id = get_user_from_session(
        token
    )


    return {
        "accounts":
            get_user_instagram_accounts(
                user_id
            )
    }


# ============================================================
# CREATE CAMPAIGN
# ============================================================

@app.post("/api/campaigns")
def create_campaign(
    request: CampaignRequest,

    authorization: str | None = Header(
        default=None
    )
):

    if not authorization:

        return JSONResponse(
            status_code=401,
            content={
                "error":
                    "Not authenticated."
            }
        )


    token = authorization.replace(
        "Bearer ",
        ""
    )


    user_id = get_user_from_session(
        token
    )


    account = get_account_for_user(

        user_id,

        request.instagram_account_id
    )


    keyword = request.keyword.strip()

    product_url = request.product_url.strip()

    dm_message = request.dm_message.strip()


    if not keyword:

        return JSONResponse(
            status_code=400,
            content={
                "error":
                    "Keyword is required."
            }
        )


    if not product_url:

        return JSONResponse(
            status_code=400,
            content={
                "error":
                    "Product URL is required."
            }
        )


    if not dm_message:

        dm_message = (
            "Here is your link:\n"
            + product_url
        )


    connection = get_db()


    cursor = connection.execute(
        """
        INSERT INTO campaigns
        (
            user_id,
            instagram_account_id,
            keyword,
            product_url,
            dm_message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,

            account["id"],

            keyword,

            product_url,

            dm_message
        )
    )


    connection.commit()


    campaign_id = cursor.lastrowid


    connection.close()


    return {

        "message":
            "Campaign created successfully.",

        "id":
            campaign_id
    }


# ============================================================
# GET CAMPAIGNS
# ============================================================

@app.get("/api/campaigns")
def campaigns(
    authorization: str | None = Header(
        default=None
    )
):

    if not authorization:

        return JSONResponse(
            status_code=401,
            content={
                "error":
                    "Not authenticated."
            }
        )


    token = authorization.replace(
        "Bearer ",
        ""
    )


    user_id = get_user_from_session(
        token
    )


    connection = get_db()


    rows = connection.execute(
        """
        SELECT
            campaigns.id,
            campaigns.keyword,
            campaigns.product_url,
            campaigns.dm_message,
            campaigns.active,
            campaigns.created_at,

            instagram_accounts.username

        FROM campaigns

        JOIN instagram_accounts

        ON campaigns.instagram_account_id =
           instagram_accounts.id

        WHERE campaigns.user_id = ?

        ORDER BY campaigns.id DESC
        """,
        (
            user_id,
        )
    ).fetchall()


    connection.close()


    return {
        "campaigns":
            [
                dict(row)
                for row in rows
            ]
    }


# ============================================================
# DELETE CAMPAIGN
# ============================================================

@app.delete("/api/campaigns/{campaign_id}")
def delete_campaign(
    campaign_id: int,

    authorization: str | None = Header(
        default=None
    )
):

    if not authorization:

        return JSONResponse(
            status_code=401,
            content={
                "error":
                    "Not authenticated."
            }
        )


    token = authorization.replace(
        "Bearer ",
        ""
    )


    user_id = get_user_from_session(
        token
    )


    connection = get_db()


    connection.execute(
        """
        DELETE FROM campaigns

        WHERE
            id = ?
            AND user_id = ?
        """,
        (
            campaign_id,

            user_id
        )
    )


    connection.commit()

    connection.close()


    return {
        "message":
            "Campaign deleted."
    }


# ============================================================
# WEBHOOK VERIFY
# ============================================================

@app.get("/webhooks/instagram")
def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    if (
        hub_mode == "subscribe"
        and hub_verify_token == INSTAGRAM_VERIFY_TOKEN
        and hub_challenge
    ):
        return int(hub_challenge)

    return JSONResponse(
        status_code=403,
        content={
            "error": "Webhook verification failed."
        }
    )


# ============================================================
# WEBHOOK RECEIVE
# ============================================================

@app.post("/webhooks/instagram")
async def receive_webhook(
    request: Request
):

    try:

        body = await request.json()

    except Exception:

        return JSONResponse(
            status_code=400,
            content={
                "error":
                    "Invalid JSON."
            }
        )


    print(
        "Instagram webhook:"
    )

    print(
        body
    )


    try:

        results = process_webhook_payload(
            body
        )

    except Exception as error:

        print(
            "Webhook processing error:",
            error
        )

        results = []


    return {

        "status":
            "received",

        "processed":
            len(results)
    }