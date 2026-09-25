import json
import re

from database import get_db

from instagram import (
    send_instagram_message
)


# ============================================================
# NORMALIZE
# ============================================================

def normalize(
    text: str
):

    return text.strip().lower()


# ============================================================
# KEYWORD MATCH
# ============================================================

def keyword_matches(
    comment: str,
    keyword: str
):

    comment = normalize(
        comment
    )

    keyword = normalize(
        keyword
    )


    if not comment or not keyword:

        return False


    if comment == keyword:

        return True


    pattern = (
        r"\b"
        + re.escape(keyword)
        + r"\b"
    )


    return re.search(
        pattern,
        comment,
        re.IGNORECASE
    ) is not None


# ============================================================
# FIND ACCOUNT
# ============================================================

def find_account_by_instagram_id(
    instagram_user_id: str
):

    connection = get_db()


    account = connection.execute(
        """
        SELECT *
        FROM instagram_accounts
        WHERE instagram_user_id = ?
        LIMIT 1
        """,
        (
            instagram_user_id,
        )
    ).fetchone()


    connection.close()


    return account


# ============================================================
# FIND CAMPAIGN
# ============================================================

def find_campaign(
    user_id: int,
    instagram_account_id: int,
    comment_text: str
):

    connection = get_db()


    campaigns = connection.execute(
        """
        SELECT *
        FROM campaigns
        WHERE
            user_id = ?
            AND instagram_account_id = ?
            AND active = 1
        ORDER BY id DESC
        """,
        (
            user_id,
            instagram_account_id
        )
    ).fetchall()


    connection.close()


    for campaign in campaigns:

        if keyword_matches(
            comment_text,
            campaign["keyword"]
        ):

            return campaign


    return None


# ============================================================
# DUPLICATE CHECK
# ============================================================

def already_processed(
    comment_id: str
):

    connection = get_db()


    row = connection.execute(
        """
        SELECT id
        FROM processed_comments
        WHERE comment_id = ?
        """,
        (
            comment_id,
        )
    ).fetchone()


    connection.close()


    return row is not None


# ============================================================
# SAVE PROCESSING RESULT
# ============================================================

def save_processing_result(
    user_id,
    instagram_account_id,
    campaign_id,
    comment_id,
    comment_text,
    status,
    response
):

    connection = get_db()


    connection.execute(
        """
        INSERT OR IGNORE INTO processed_comments
        (
            user_id,
            instagram_account_id,
            campaign_id,
            comment_id,
            comment_text,
            status,
            response
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            instagram_account_id,
            campaign_id,
            comment_id,
            comment_text,
            status,
            json.dumps(
                response
            )
        )
    )


    connection.commit()

    connection.close()


# ============================================================
# PROCESS COMMENT
# ============================================================

def process_comment(
    value: dict
):

    comment_id = value.get(
        "id"
    )

    comment_text = value.get(
        "text",
        ""
    )


    # The exact field names can vary
    # by webhook event/version.
    #
    # Keep these flexible for now.

    instagram_user_id = (
        value.get(
            "instagram_user_id"
        )
        or value.get(
            "recipient_id"
        )
        or value.get(
            "from",
            {}
        ).get(
            "id"
        )
    )


    if not comment_id:

        return {
            "status":
                "ignored",

            "reason":
                "No comment ID."
        }


    if already_processed(
        comment_id
    ):

        return {
            "status":
                "duplicate"
        }


    if not instagram_user_id:

        return {
            "status":
                "ignored",

            "reason":
                "Instagram account ID missing."
        }


    account = find_account_by_instagram_id(
        instagram_user_id
    )


    if not account:

        return {
            "status":
                "ignored",

            "reason":
                "Instagram account not connected."
        }


    campaign = find_campaign(
        account["user_id"],
        account["id"],
        comment_text
    )


    if not campaign:

        save_processing_result(

            account["user_id"],

            account["id"],

            None,

            comment_id,

            comment_text,

            "ignored",

            {
                "reason":
                    "No matching campaign."
            }
        )


        return {
            "status":
                "ignored",

            "reason":
                "No matching campaign."
        }


    # --------------------------------------------------------
    # Send reply/message
    # --------------------------------------------------------

    # NOTE:
    # The recipient identifier and private-reply endpoint
    # must match the exact webhook payload/API operation
    # Meta enables for the selected Instagram Login flow.
    #
    # We keep the API operation isolated here so it can be
    # adjusted without rewriting the SaaS.

    recipient_id = (
        value.get(
            "from",
            {}
        ).get(
            "id"
        )
    )


    if not recipient_id:

        save_processing_result(

            account["user_id"],

            account["id"],

            campaign["id"],

            comment_id,

            comment_text,

            "waiting",

            {
                "reason":
                    "Comment matched but recipient ID was not available in event."
            }
        )


        return {
            "status":
                "waiting"
        }


    result = send_instagram_message(

        account["instagram_user_id"],

        account["access_token"],

        recipient_id,

        campaign["dm_message"]
    )


    status = (
        "sent"
        if result["success"]
        else "failed"
    )


    save_processing_result(

        account["user_id"],

        account["id"],

        campaign["id"],

        comment_id,

        comment_text,

        status,

        result
    )


    return {
        "status":
            status,

        "result":
            result
    }


# ============================================================
# WEBHOOK PAYLOAD
# ============================================================

def process_webhook_payload(
    body: dict
):

    results = []


    entries = body.get(
        "entry",
        []
    )


    for entry in entries:

        changes = entry.get(
            "changes",
            []
        )


        for change in changes:

            field = change.get(
                "field"
            )


            if field != "comments":

                continue


            value = change.get(
                "value",
                {}
            )


            result = process_comment(
                value
            )


            results.append(
                result
            )


    return results