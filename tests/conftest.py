import os

import pytest

# Важно: выставляем ДО импорта src.api.main, потому что Limiter в main.py
# читает settings.rate_limit на уровне модуля. Без этого CI мог бы иногда
# ловить 429 от собственного же rate limiter при быстром прогоне тестов API.
os.environ.setdefault("DOCFORGE_ENVIRONMENT", "testing")
os.environ.setdefault("DOCFORGE_RATE_LIMIT", "1000/minute")

from src.engine.generator import DocumentGenerator  # noqa: E402
from src.extractor.extractor import EntityExtractor  # noqa: E402


@pytest.fixture
def generator() -> DocumentGenerator:
    return DocumentGenerator()


@pytest.fixture
def extractor() -> EntityExtractor:
    return EntityExtractor()


@pytest.fixture
def sample_ruling_text() -> str:
    return (
        "Арбитражный суд города Москвы в составе судьи Петровой А.С. "
        'рассмотрел дело № А40-12345/2024 по иску ООО "Ромашка" '
        "к Иванову Ивану Ивановичу о взыскании задолженности "
        "в размере 500 000 рублей."
    )
