"""Аутентификация по API-ключу и вспомогательная функция для rate limiter.

Живёт в api/, а не в core/, потому что завязана на HTTP (заголовки запроса,
исключения FastAPI) — в отличие от core, который не должен знать про HTTP.
"""

import hmac
import logging

from fastapi import Header, HTTPException, Request, status

from src.core.config import settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = "X-API-Key"


def _matches_any_key(candidate: str, valid_keys: list[str]) -> bool:
    """Сравнивает candidate с каждым валидным ключом constant-time способом.

    Обычное `candidate not in valid_keys` использует `==` на строках, а
    сравнение строк в CPython останавливается на первом несовпадающем
    символе — то есть занимает тем больше времени, чем длиннее верный
    префикс. На проде, доступном по сети, это в теории позволяет подбирать
    ключ по замерам времени ответа символ за символом. `hmac.compare_digest`
    всегда сравнивает за одинаковое время независимо от того, где произошло
    расхождение.
    """
    return any(hmac.compare_digest(candidate, key) for key in valid_keys)


async def verify_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER)) -> None:
    """Dependency для защищённых эндпоинтов.

    Если DOCFORGE_API_KEYS не задан — аутентификация выключена (используется
    для демо/портфолио-деплоя без своего слоя авторизации перед API).
    Если задан — заголовок X-API-Key обязателен и должен совпадать с одним
    из настроенных ключей.
    """
    if not settings.auth_enabled:
        return
    if x_api_key is None or not _matches_any_key(x_api_key, settings.api_keys_list):
        logger.warning("Отклонён запрос без валидного API-ключа")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")


def rate_limit_key(request: Request) -> str:
    """Ключ для rate limiter: API-ключ, если он есть, иначе IP клиента.

    Так лимит считается per-API-key для авторизованных клиентов и per-IP —
    для анонимных, вместо единого лимита на весь сервис.
    """
    api_key = request.headers.get(API_KEY_HEADER)
    if api_key:
        return f"key:{api_key}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"
