from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


def engine_init_local():
    return create_engine("sqlite:///data/olj-scraper.db")


def engine_init_remote():
    load_dotenv()
    TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
    TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

    engine = create_engine(
        f"sqlite+{TURSO_DATABASE_URL}?secure=true",
        connect_args={
            "auth_token": TURSO_AUTH_TOKEN,
        },
    )
    return engine
