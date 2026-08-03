"""Тонкая точка входа в корне репозитория.

Существует для платформ и инструментов, которые по умолчанию ищут
`main:app` в корне (некоторые PaaS-автодетекторы, `python main.py`
для локальной отладки). Вся реальная логика — в src/api/main.py.
Не дублируй код здесь, только реэкспорт.
"""

from src.api.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
