import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy.exc import OperationalError

from app.config import uses_ephemeral_render_mysql
from app.database import get_engine
from app.init_db import initialize_database
from app.seed_demo import seed_demo_data

MYSQL_DATA_DIRECTORY = Path("/tmp/garagetrack-mysql")
MYSQL_SOCKET_PATH = MYSQL_DATA_DIRECTORY / "mysql.sock"


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


def wait_for_ephemeral_mysql(mysql_process: subprocess.Popen[bytes]) -> None:
    for attempt in range(60):
        if mysql_process.poll() is not None:
            raise RuntimeError("The temporary MySQL server stopped during startup.")
        result = subprocess.run(
            [
                "mysqladmin",
                "--protocol=socket",
                f"--socket={MYSQL_SOCKET_PATH}",
                "--user=root",
                "ping",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return
        if attempt < 59:
            time.sleep(1)
    raise RuntimeError("The temporary MySQL server did not become available.")


def start_ephemeral_mysql() -> subprocess.Popen[bytes]:
    MYSQL_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    shutil.chown(MYSQL_DATA_DIRECTORY, user="mysql", group="mysql")
    if not (MYSQL_DATA_DIRECTORY / "mysql").exists():
        subprocess.run(
            [
                "mysqld",
                "--initialize-insecure",
                "--user=mysql",
                f"--datadir={MYSQL_DATA_DIRECTORY}",
            ],
            check=True,
        )
    mysql_process = subprocess.Popen(
        [
            "mysqld",
            "--user=mysql",
            f"--datadir={MYSQL_DATA_DIRECTORY}",
            f"--socket={MYSQL_SOCKET_PATH}",
            f"--pid-file={MYSQL_DATA_DIRECTORY / 'mysqld.pid'}",
            "--skip-networking",
            "--innodb-buffer-pool-size=32M",
            "--innodb-log-buffer-size=4M",
            "--max-connections=10",
            "--performance-schema=OFF",
            "--skip-log-bin",
            "--table-open-cache=64",
            "--thread-cache-size=2",
        ]
    )
    try:
        wait_for_ephemeral_mysql(mysql_process)
        configure_ephemeral_database()
    except BaseException:
        stop_process(mysql_process)
        raise
    return mysql_process


def configure_ephemeral_database() -> None:
    app_password = secrets.token_hex(32)
    sql_statements = (
        "CREATE DATABASE IF NOT EXISTS garagetrack "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci; "
        "CREATE USER IF NOT EXISTS 'garagetrack_app'@'localhost' "
        f"IDENTIFIED BY '{app_password}'; "
        f"ALTER USER 'garagetrack_app'@'localhost' IDENTIFIED BY '{app_password}'; "
        "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, REFERENCES "
        "ON garagetrack.* "
        "TO 'garagetrack_app'@'localhost';"
    )
    subprocess.run(
        [
            "mysql",
            "--protocol=socket",
            f"--socket={MYSQL_SOCKET_PATH}",
            "--user=root",
        ],
        input=sql_statements,
        text=True,
        check=True,
    )
    os.environ["DATABASE_URL"] = (
        f"mysql+pymysql://garagetrack_app:{app_password}@localhost/garagetrack"
        f"?unix_socket={MYSQL_SOCKET_PATH}"
    )


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def prepare_database() -> None:
    wait_for_database()
    initialize_database()
    seed_demo_data()


def start_application() -> None:
    port = os.getenv("PORT", "8000")
    server_command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        port,
    ]
    if not uses_ephemeral_render_mysql():
        prepare_database()
        os.execv(sys.executable, server_command)
    mysql_process = start_ephemeral_mysql()
    try:
        prepare_database()
        server_process = subprocess.Popen(server_command)
        while server_process.poll() is None:
            if mysql_process.poll() is not None:
                stop_process(server_process)
                raise RuntimeError("The temporary MySQL server stopped unexpectedly.")
            time.sleep(1)
        raise SystemExit(server_process.returncode)
    finally:
        stop_process(mysql_process)


if __name__ == "__main__":
    start_application()
