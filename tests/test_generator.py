import pytest

from src.core.exceptions import GenerationError, TemplateNotFoundError, TemplateRenderError
from src.engine.generator import DocumentGenerator


def test_generate_claim(generator):
    data = {
        "court_name": "Тест",
        "plaintiff": "ООО Тест",
        "defendant": "Иванов",
        "claim_amount": 100000,
        "case_number": "А40-1",
        "legal_articles": "309 ГК",
        "attachments": ["Док"],
        "plaintiff_representative": "Петров",
    }
    result = generator.generate("claim.j2", data)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_appeal(generator):
    data = {
        "court_name": "Тест",
        "plaintiff": "ООО Тест",
        "defendant": "Иванов",
        "claim_amount": 100000,
        "case_number": "А40-1",
        "appeal_arguments": "Доводы",
        "legal_articles": "270 АПК",
        "attachments": ["Док"],
        "plaintiff_representative": "Петров",
    }
    result = generator.generate("appeal.j2", data)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_contract(generator):
    data = {
        "customer": "ООО Тест",
        "contractor": "Иванов",
        "service_description": "Услуги",
        "contract_amount": 100000,
        "contract_number": "1",
        "contract_date": "01.01.2024",
        "customer_representative": "Петров",
        "contractor_representative": "Иванов",
    }
    result = generator.generate("contract.j2", data)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_missing_template_raises(generator):
    with pytest.raises(TemplateNotFoundError):
        generator.generate("does_not_exist.j2", {})


def test_generate_missing_variable_raises(generator):
    # court_name отсутствует — StrictUndefined должен явно упасть,
    # а не молча подставить пустую строку.
    data = {
        "plaintiff": "ООО Тест",
        "defendant": "Иванов",
        "claim_amount": 100000,
        "case_number": "А40-1",
        "legal_articles": "309 ГК",
        "attachments": ["Док"],
        "plaintiff_representative": "Петров",
    }
    with pytest.raises(TemplateRenderError):
        generator.generate("claim.j2", data)


@pytest.mark.parametrize(
    "malicious_name",
    [
        "../requirements.txt",
        "../../etc/passwd",
        "sub/../../secrets.j2",
        "/etc/passwd",
    ],
)
def test_generate_blocks_path_traversal(generator, malicious_name):
    with pytest.raises(TemplateNotFoundError):
        generator.generate(malicious_name, {})


def test_missing_template_error_does_not_leak_filesystem_path(generator):
    # Регрессия: TemplateNotFoundError раньше включал полный абсолютный
    # путь на диске сервера, и он утекал клиенту через DocForgeError-
    # обработчик без гейта по environment.
    with pytest.raises(TemplateNotFoundError) as exc_info:
        generator.generate("does_not_exist.j2", {})

    message = str(exc_info.value)
    assert str(generator.templates_dir) not in message
    assert "does_not_exist.j2" in message  # имя шаблона — безопасно и полезно клиенту


def test_generation_error_does_not_leak_internal_exception_details(generator, monkeypatch):
    # Регрессия: GenerationError раньше оборачивал str(exc) внутреннего
    # исключения (python-docx/jinja2 и т.п.) и отдавал его клиенту как есть.
    secret_detail = "internal-connection-string-xyz-12345"

    def _boom(self, rendered_text: str) -> bytes:
        raise RuntimeError(secret_detail)

    monkeypatch.setattr(DocumentGenerator, "_render_to_docx", _boom)

    data = {
        "court_name": "Тест",
        "plaintiff": "ООО Тест",
        "defendant": "Иванов",
        "claim_amount": 100000,
        "case_number": "А40-1",
        "legal_articles": "309 ГК",
        "attachments": ["Док"],
        "plaintiff_representative": "Петров",
    }
    with pytest.raises(GenerationError) as exc_info:
        generator.generate("claim.j2", data)

    assert secret_detail not in str(exc_info.value)
