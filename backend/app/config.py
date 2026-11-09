import os

from fastapi import HTTPException, status


def is_demo_read_only() -> bool:
    return os.getenv("DEMO_READ_ONLY", "false").strip().lower() == "true"


def require_writable_mode() -> None:
    if is_demo_read_only():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The public demo is read-only.",
        )
