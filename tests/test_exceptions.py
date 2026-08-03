import pytest

from src.core.exceptions import (
    DocForgeError,
    ExtractionError,
    GenerationError,
    TemplateNotFoundError,
    TemplateRenderError,
)


@pytest.mark.parametrize(
    "exc_cls",
    [TemplateNotFoundError, TemplateRenderError, GenerationError, ExtractionError],
)
def test_all_domain_exceptions_inherit_from_docforge_error(exc_cls):
    assert issubclass(exc_cls, DocForgeError)


def test_docforge_error_carries_message():
    exc = GenerationError("boom")
    assert str(exc) == "boom"
