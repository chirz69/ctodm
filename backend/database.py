import sqlite3

from config import DATABASE


def get_db():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    connection = get_db()


    # ========================================================
    # USERS
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # ========================================================
    # INSTAGRAM ACCOUNTS
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS instagram_accounts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            instagram_user_id TEXT NOT NULL,

            username TEXT,

            access_token TEXT NOT NULL,

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            updated_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE (
                user_id,
                instagram_user_id
            ),

            FOREIGN KEY (
                user_id
            )
            REFERENCES users(id)
            ON DELETE CASCADE
        )
        """
    )


    # ========================================================
    # CAMPAIGNS
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS campaigns (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            instagram_account_id INTEGER NOT NULL,

            keyword TEXT NOT NULL,

            product_url TEXT NOT NULL,

            dm_message TEXT NOT NULL,

            active INTEGER DEFAULT 1,

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (
                user_id
            )
            REFERENCES users(id)
            ON DELETE CASCADE,

            FOREIGN KEY (
                instagram_account_id
            )
            REFERENCES instagram_accounts(id)
            ON DELETE CASCADE
        )
        """
    )


    # ========================================================
    # PROCESSED COMMENTS
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_comments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            instagram_account_id INTEGER,

            campaign_id INTEGER,

            comment_id TEXT UNIQUE NOT NULL,

            comment_text TEXT,

            status TEXT,

            response TEXT,

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (
                user_id
            )
            REFERENCES users(id)
            ON DELETE SET NULL,

            FOREIGN KEY (
                instagram_account_id
            )
            REFERENCES instagram_accounts(id)
            ON DELETE SET NULL,

            FOREIGN KEY (
                campaign_id
            )
            REFERENCES campaigns(id)
            ON DELETE SET NULL
        )
        """
    )


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()

    connection.close()