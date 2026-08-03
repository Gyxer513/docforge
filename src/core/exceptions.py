"""Доменные исключения DocForge.

Живут в core, а не в api, потому что на них завязаны engine и extractor —
нижние слои не должны зависеть от api. api импортирует их отсюда же.
"""


class DocForgeError(Exception):
    """Базовое исключение DocForge."""


class TemplateNotFoundError(DocForgeError):
    """Шаблон не найден."""


class TemplateRenderError(DocForgeError):
    """В шаблоне используется переменная, которая не была передана."""


class GenerationError(DocForgeError):
    """Ошибка генерации документа."""


class ExtractionError(DocForgeError):
    """Ошибка извлечения данных."""
