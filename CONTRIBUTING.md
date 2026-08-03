# Contributing

Спасибо за интерес к DocForge! Ниже — как быстро включиться в разработку.

## Локальная настройка

```bash
git clone https://github.com/legalops-toolkit/docforge.git
cd docforge
make dev      # ставит зависимости + pre-commit хуки
make test     # прогон тестов с покрытием
make lint     # ruff + mypy
```

## Процесс

1. Форкните репозиторий, создайте ветку от `main`: `feat/short-description`
   или `fix/short-description`.
2. Пишите тесты на новую логику — `pytest --cov` должен показывать не ниже
   90% покрытия (см. `pyproject.toml`).
3. Убедитесь, что `make lint` и `make test` проходят локально.
4. Откройте Pull Request, заполните шаблон PR, свяжите с issue, если есть.
5. CI (`ruff`, `mypy`, `pytest`, Docker build) должен быть зелёным.

## Стиль кода

- Форматирование и линт — `ruff` (конфигурация в `pyproject.toml`).
- Типизация — современный синтаксис (`str | None`, `list[str]`, `pathlib.Path`).
- Публичные функции и классы — с docstring на русском (проект и домен — RU).
- Коммиты — в свободной форме, но осмысленные (`fix: ...`, `feat: ...` приветствуются).

## Структура веток

- `main` — всегда деплоится.
- Фичи и фиксы — через Pull Request с ревью.
