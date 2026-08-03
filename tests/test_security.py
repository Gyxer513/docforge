import pytest
from fastapi import HTTPException

from src.api.security import rate_limit_key, verify_api_key
from src.core.config import Settings


class _FakeClient:
    def __init__(self, host: str) -> None:
        self.host = host


class _FakeRequest:
    def __init__(self, headers: dict[str, str], host: str = "203.0.113.1") -> None:
        self.headers = headers
        self.client = _FakeClient(host)


@pytest.mark.anyio
async def test_verify_api_key_disabled_by_default_allows_no_header():
    # DOCFORGE_API_KEYS не задан в тестовом окружении -> auth выключена.
    await verify_api_key(x_api_key=None)


@pytest.mark.anyio
async def test_verify_api_key_rejects_when_enabled_and_missing(monkeypatch):
    from src.api import security

    monkeypatch.setattr(security.settings, "api_keys", "expected-key")
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key=None)
    assert exc_info.value.status_code == 401


@pytest.mark.anyio
async def test_verify_api_key_accepts_valid_key(monkeypatch):
    from src.api import security

    monkeypatch.setattr(security.settings, "api_keys", "expected-key")
    await verify_api_key(x_api_key="expected-key")


@pytest.mark.anyio
async def test_verify_api_key_rejects_wrong_key(monkeypatch):
    from src.api import security

    monkeypatch.setattr(security.settings, "api_keys", "expected-key")
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key="wrong-key")
    assert exc_info.value.status_code == 401


@pytest.mark.anyio
async def test_verify_api_key_accepts_any_configured_key(monkeypatch):
    from src.api import security

    monkeypatch.setattr(security.settings, "api_keys", "key-one,key-two,key-three")
    await verify_api_key(x_api_key="key-two")


def test_rate_limit_key_prefers_api_key_header():
    request = _FakeRequest(headers={"X-API-Key": "secret"})
    assert rate_limit_key(request) == "key:secret"


def test_rate_limit_key_falls_back_to_ip():
    request = _FakeRequest(headers={})
    assert rate_limit_key(request) == "ip:203.0.113.1"


def test_settings_auth_enabled_reflects_api_keys():
    s = Settings(api_keys="")
    assert s.auth_enabled is False
    assert s.api_keys_list == []

    s2 = Settings(api_keys="key1, key2 ,key3")
    assert s2.auth_enabled is True
    assert s2.api_keys_list == ["key1", "key2", "key3"]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
