#!/usr/bin/env python3
"""Проверяет, что pyproject.toml и requirements*.txt описывают один и тот же
набор пакетов с одинаковыми версиями — как для основных, так и для dev-
зависимостей.

Зачем: requirements.txt используется для рантайм-образа (см. комментарий в
Dockerfile — пакет намеренно не ставится через `pip install .`, чтобы не
тащить build-инструменты в финальный слой), а requirements-dev.txt дублирует
[project.optional-dependencies].dev по той же причине для CI/локальной
разработки. Версии продублированы в файлах руками — ничего не мешало
обновить пакет в одном месте и забыть про другое, и они разъехались бы без
единого предупреждения. Раньше проверялась только пара
pyproject.toml/requirements.txt — dev-зависимости оставались открытой дырой
того же класса.

Использование: python3 scripts/check_deps_sync.py
Код возврата: 0 — всё совпадает, 1 — есть расхождение (печатает diff).
"""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _parse_requirement_lines(lines: list[str]) -> dict[str, str]:
    """Общий парсер для списков зависимостей вида 'pkg[extra]==1.2.3'."""
    deps: dict[str, str] = {}
    for line in lines:
        name, _, version = line.partition("==")
        # normalize extras away, e.g. "uvicorn[standard]" -> "uvicorn"
        name = re.sub(r"\[.*\]", "", name).strip()
        deps[name] = version.strip()
    return deps


def parse_pyproject_dependencies() -> dict[str, str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return _parse_requirement_lines(data["project"]["dependencies"])


def parse_pyproject_dev_dependencies() -> dict[str, str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return _parse_requirement_lines(data["project"]["optional-dependencies"]["dev"])


def _parse_requirements_file(filename: str) -> dict[str, str]:
    raw_lines = []
    for raw_line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        # Пропускаем пустые строки, комментарии и `-r other.txt` — это не
        # пакет, а ссылка на другой requirements-файл (requirements-dev.txt
        # начинается с "-r requirements.txt").
        if not line or line.startswith("#") or line.startswith("-r "):
            continue
        raw_lines.append(line)
    return _parse_requirement_lines(raw_lines)


def parse_requirements_txt() -> dict[str, str]:
    return _parse_requirements_file("requirements.txt")


def parse_requirements_dev_txt() -> dict[str, str]:
    return _parse_requirements_file("requirements-dev.txt")


def _report_mismatch(label: str, left_name: str, left: dict[str, str], right_name: str, right: dict[str, str]) -> bool:
    """Печатает построчный diff, если left != right. Возвращает True, если всё совпало."""
    if left == right:
        print(f"OK: {label} синхронизированы.")
        return True

    print(f"MISMATCH between {label}:")
    all_names = sorted(set(left) | set(right))
    for name in all_names:
        lv = left.get(name, "<отсутствует>")
        rv = right.get(name, "<отсутствует>")
        if lv != rv:
            print(f"  {name}: {left_name}={lv}  {right_name}={rv}")
    return False


def main() -> int:
    main_ok = _report_mismatch(
        "pyproject.toml [project.dependencies] и requirements.txt",
        "pyproject.toml",
        parse_pyproject_dependencies(),
        "requirements.txt",
        parse_requirements_txt(),
    )
    dev_ok = _report_mismatch(
        "pyproject.toml [project.optional-dependencies].dev и requirements-dev.txt",
        "pyproject.toml",
        parse_pyproject_dev_dependencies(),
        "requirements-dev.txt",
        parse_requirements_dev_txt(),
    )
    return 0 if (main_ok and dev_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
