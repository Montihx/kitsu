from app.core.settings import get_settings


def test_core_settings_smoke() -> None:
    settings = get_settings()
    assert settings.secret_key
    assert settings.database_url.startswith("postgresql+asyncpg://")
