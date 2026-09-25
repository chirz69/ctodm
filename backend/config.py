import os

from dotenv import load_dotenv


load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "Comment2DM"
)


FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:5173"
)


DATABASE = os.getenv(
    "DATABASE",
    "comment2dm.db"
)


INSTAGRAM_APP_ID = os.getenv(
    "INSTAGRAM_APP_ID"
)


INSTAGRAM_APP_SECRET = os.getenv(
    "INSTAGRAM_APP_SECRET"
)


INSTAGRAM_REDIRECT_URI = os.getenv(
    "INSTAGRAM_REDIRECT_URI",
    "http://localhost:8000/auth/instagram/callback"
)


INSTAGRAM_VERIFY_TOKEN = os.getenv(
    "INSTAGRAM_VERIFY_TOKEN",
    "comment2dm_verify_12345"
)


INSTAGRAM_API_VERSION = os.getenv(
    "INSTAGRAM_API_VERSION",
    "v25.0"
)