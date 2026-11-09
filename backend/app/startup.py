import os
import sys
import time

from sqlalchemy.exc import OperationalError

from app.database import get_engine
from app.init_db import initialize_database
from app.seed_demo import seed_demo_data


def wait_for_database() -> None:
    for attempt in range(30):
        try:
            with get_engine().connect():
                return
        except OperationalError:
            if attempt == 29:
                raise RuntimeError(
                    "The configured MySQL database is unavailable."
                ) from None
            time.sleep(2)


def prepare_database() -> None:
    wait_for_database()
    initialize_database()
    seed_demo_data()


def start_application() -> None:
    prepare_database()
    port = os.getenv("PORT", "8000")
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ],
    )


if __name__ == "__main__":
    start_application()
