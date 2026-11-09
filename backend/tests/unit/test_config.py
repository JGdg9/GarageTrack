from app.config import is_demo_read_only, uses_ephemeral_render_mysql


def test_demo_mode_is_writable_by_default(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_READ_ONLY", raising=False)

    assert is_demo_read_only() is False


def test_demo_mode_can_be_set_to_read_only(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")

    assert is_demo_read_only() is True


def test_render_uses_external_mysql_by_default(monkeypatch) -> None:
    monkeypatch.delenv("RENDER_EPHEMERAL_MYSQL", raising=False)

    assert uses_ephemeral_render_mysql() is False


def test_render_can_use_ephemeral_mysql(monkeypatch) -> None:
    monkeypatch.setenv("RENDER_EPHEMERAL_MYSQL", "true")

    assert uses_ephemeral_render_mysql() is True
