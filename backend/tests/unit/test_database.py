import pytest

from app.database import normalize_database_url


@pytest.mark.parametrize(
    ("database_url", "expected_url"),
    [
        (
            "mysql://garage_user:sample-password@mysql.internal:3306/garagetrack",
            "mysql+pymysql://garage_user:sample-password@mysql.internal:3306/garagetrack",
        ),
        (
            "mysql+pymysql://garage_user:sample-password@127.0.0.1:3307/garagetrack",
            "mysql+pymysql://garage_user:sample-password@127.0.0.1:3307/garagetrack",
        ),
    ],
)
def test_normalize_database_url_for_pymysql(
    database_url: str, expected_url: str
) -> None:
    assert normalize_database_url(database_url) == expected_url
