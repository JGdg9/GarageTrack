import os
from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("mysql://"):
        return f"mysql+pymysql://{database_url.removeprefix('mysql://')}"
    return database_url


@lru_cache
def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")
    return create_engine(normalize_database_url(database_url), pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
