import os

from src.core.config import Settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("DOCFORGE_ENVIRONMENT", raising=False)
    s = Settings()
    assert s.environment == "development"
    assert s.is_production is False
    assert s.max_extraction_text_length > 0
    assert s.max_request_body_bytes > 0



def test_settings_reads_env_prefix(monkeypatch):
    monkeypatch.setenv("DOCFORGE_ENVIRONMENT", "production")
    monkeypatch.setenv("DOCFORGE_LOG_LEVEL", "WARNING")
    s = Settings()
    assert s.environment == "production"
    assert s.is_production is True
    assert s.log_level == "WARNING"
    # чистим за собой, чтобы не влиять на другие тесты в процессе
    os.environ.pop("DOCFORGE_ENVIRONMENT", None)
    os.environ.pop("DOCFORGE_LOG_LEVEL", None)
