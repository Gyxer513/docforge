"""Конфигурация шаблонов и данные по умолчанию."""

from typing import TypedDict


class _BaseLitigationData(TypedDict, total=False):
    """Общие поля искового заявления и апелляционной жалобы.

    Оба документа описывают судебный спор между истцом и ответчиком и
    делят 8 из 9 полей — раньше эти 8 полей были дословно продублированы
    в ClaimData и AppealData; при добавлении общего поля (например,
    court_address) пришлось бы править оба класса и рисковать, что они
    разъедутся.
    """

    court_name: str
    plaintiff: str
    defendant: str
    claim_amount: float
    case_number: str
    legal_articles: str
    attachments: list[str]
    plaintiff_representative: str
    date: str


class ClaimData(_BaseLitigationData, total=False):
    """Данные искового заявления — не добавляет полей сверх базовых."""


class AppealData(_BaseLitigationData, total=False):
    appeal_arguments: str


class ContractData(TypedDict, total=False):
    customer: str
    contractor: str
    service_description: str
    contract_amount: float
    contract_number: str
    contract_date: str
    customer_representative: str
    contractor_representative: str
    date: str
