
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

SECRET_KEY = os.getenv("SECRET_KEY")

missing = [
    key for key in ("host", "user", "password", "database")
    if not DB_CONFIG.get(key)
]

if missing:
    raise RuntimeError(
        "Missing Render database environment variables: "
        + ", ".join(missing)
    )

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")
