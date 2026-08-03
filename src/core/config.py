"""Конфигурация приложения через переменные окружения (pydantic-settings).

Все переменные — с префиксом DOCFORGE_ (см. .env.example для полного списка).
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = ROOT_DIR / "templates"
DATA_DIR = ROOT_DIR / "data"

TEMPLATE_MAP = {
    "claim": "claim.j2",
    "appeal": "appeal.j2",
    "contract": "contract.j2",
}

Environment = Literal["development", "testing", "production"]


class Settings(BaseSettings):
    """Настройки приложения. Переопределяются переменными окружения или .env."""

    model_config = SettingsConfigDict(env_prefix="DOCFORGE_", env_file=".env", extra="ignore")

    environment: Environment = "development"
    log_level: str = "INFO"

    default_court: str = "Арбитражный суд г. Москвы"
    default_legal_articles: str = "309, 310, 395 ГК РФ"

    templates_dir: Path = TEMPLATES_DIR

    # Защита от чрезмерно больших запросов на /extract — без лимита
    # злоумышленник может прислать многомегабайтный текст и нагрузить NER-пайплайн.
    max_extraction_text_length: int = 50_000

    # Общий лимит тела запроса (байт) — проверяется middleware в api/main.py.
    max_request_body_bytes: int = 1_048_576  # 1 MiB

    # Rate limiting: формат "N/minute", "N/second" и т.п. (см. slowapi/limits).
    rate_limit: str = "60/minute"

    # Список API-ключей через запятую (DOCFORGE_API_KEYS=key1,key2). Пусто —
    # аутентификация выключена (подходит для демо/портфолио-деплоя), но
    # rate limit всё равно применяется по IP.
    api_keys: str = ""

    @property
    def api_keys_list(self) -> list[str]:
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_keys_list)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()

# Обратная совместимость для существующего кода/тестов.
DEFAULT_COURT = settings.default_court
DEFAULT_LEGAL_ARTICLES = settings.default_legal_articles
