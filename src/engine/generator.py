"""Генератор документов через Jinja2 + python-docx."""

from __future__ import annotations

import io
import logging
from datetime import date
from pathlib import Path
from typing import Any

from docx import Document
from jinja2 import StrictUndefined, Template, UndefinedError

from src.core.config import TEMPLATES_DIR
from src.core.exceptions import GenerationError, TemplateNotFoundError, TemplateRenderError

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Абстрактный генератор документов."""

    def __init__(self, templates_dir: str | Path | None = None) -> None:
        self.templates_dir = Path(templates_dir) if templates_dir else TEMPLATES_DIR

    def _render_template(self, template_name: str, data: dict[str, Any]) -> str:
        """Рендерит Jinja2 шаблон. StrictUndefined гарантирует явную ошибку,
        если в данных не хватает переменной, которую ждёт шаблон, вместо
        молчаливой подстановки пустой строки."""
        # Защита от path traversal: сейчас template_name всегда приходит из
        # захардкоженного набора в api/main.py, но метод публичный, поэтому
        # защищаемся и на этом уровне, а не только по соглашению вызывающей стороны.
        safe_name = Path(template_name).name
        if safe_name != template_name or ".." in template_name:
            logger.warning("Отклонено подозрительное имя шаблона: %r", template_name)
            raise TemplateNotFoundError(f"Недопустимое имя шаблона: {template_name!r}")

        template_path = (self.templates_dir / safe_name).resolve()
        if self.templates_dir.resolve() not in template_path.parents and template_path != self.templates_dir.resolve():
            logger.warning("Путь шаблона вышел за пределы templates_dir: %s", template_path)
            raise TemplateNotFoundError(f"Недопустимое имя шаблона: {template_name!r}")

        try:
            content = template_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            # Полный путь на файловой системе сервера — только в лог. Раньше
            # он попадал прямо в исключение, а DocForgeError-обработчик в
            # api/main.py возвращает str(exc) клиенту без гейта по
            # environment — то есть путь утекал бы и в "production".
            logger.warning("Шаблон не найден: %s", template_path)
            raise TemplateNotFoundError(f"Шаблон {template_name!r} не найден") from exc

        template = Template(content, undefined=StrictUndefined)
        try:
            return template.render(**data)
        except UndefinedError as exc:
            logger.warning("В шаблоне %s не хватает переменной: %s", template_name, exc)
            raise TemplateRenderError(
                f"Шаблону {template_name} не хватает переменной: {exc}"
            ) from exc

    def _render_to_docx(self, rendered_text: str) -> bytes:
        """Конвертирует отрендеренный текст в .docx (в памяти, без временных файлов)."""
        doc = Document()
        for paragraph in rendered_text.split("\n"):
            if paragraph.strip():
                doc.add_paragraph(paragraph.strip())
        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    def generate(self, template_name: str, data: dict[str, Any]) -> bytes:
        """Генерирует документ по шаблону и данным."""
        logger.info("Генерация документа по шаблону %s", template_name)
        try:
            data = dict(data)
            data.setdefault("date", date.today().strftime("%d.%m.%Y"))
            rendered = self._render_template(template_name, data)
            result = self._render_to_docx(rendered)
            logger.info("Документ %s сгенерирован, %d байт", template_name, len(result))
            return result
        except (TemplateNotFoundError, TemplateRenderError):
            raise
        except Exception as exc:
            # str(exc) раньше уходил клиенту как есть (через DocForgeError-
            # обработчик в api/main.py, который не проверяет environment) —
            # текст внутреннего исключения python-docx/jinja2 мог содержать
            # детали окружения. Полная информация остаётся в логе через
            # logger.exception, наружу — только безопасное сообщение.
            logger.exception("Неожиданная ошибка генерации документа %s", template_name)
            raise GenerationError(f"Не удалось сгенерировать документ по шаблону {template_name}") from exc


generator = DocumentGenerator()
