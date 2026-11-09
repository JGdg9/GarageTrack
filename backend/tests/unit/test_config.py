from app.config import is_demo_read_only


def test_demo_mode_is_writable_by_default(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_READ_ONLY", raising=False)

    assert is_demo_read_only() is False


def test_demo_mode_can_be_set_to_read_only(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")

    assert is_demo_read_only() is True
