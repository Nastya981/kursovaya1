import json
import re
from typing import Any, Dict, List

from src.logger_config import setup_logger

logger = setup_logger('services')


def simple_search(transactions: List[Dict[str, Any]], search_query: str) -> str:
    """Простой поиск транзакций по описанию или категории."""
    logger.info(f"Поиск транзакций по запросу: '{search_query}'")

    if not transactions or not search_query:
        return json.dumps([], ensure_ascii=False)

    search_lower = search_query.lower()
    results = []

    for transaction in transactions:
        description = str(transaction.get('Описание', ''))
        category = str(transaction.get('Категория', ''))

        if search_lower in description.lower() or search_lower in category.lower():
            results.append(transaction)

    logger.info(f"Найдено {len(results)} транзакций")
    return json.dumps(results, ensure_ascii=False, indent=2)


def search_by_phone_numbers(transactions: List[Dict[str, Any]]) -> str:
    """
    Поиск транзакций, содержащих номера телефонов в описании.
    """
    logger.info("Поиск транзакций с номерами телефонов")

    patterns = [
        r'\+7\s\d{3}\s\d{2}-\d{2}-\d{2}',
        r'\+7\s\d{3}\s\d{2}\s\d{2}\s\d{2}',
        r'\+7\d{10}',
        r'8\s\d{3}\s\d{3}\s\d{2}\s\d{2}',
        r'8\d{10}',
        r'\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    ]

    results = []

    for transaction in transactions:
        description = str(transaction.get('Описание', ''))
        for pattern in patterns:
            if re.search(pattern, description):
                results.append(transaction)
                logger.debug(f"Найдена транзакция с телефоном: {description[:100]}")
                break

    logger.info(f"Найдено {len(results)} транзакций с номерами телефонов")
    return json.dumps(results, ensure_ascii=False, indent=2)


def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> str:
    """
    Поиск переводов физическим лицам.
    """
    logger.info("Поиск переводов физическим лицам")

    name_pattern = re.compile(r'[А-Я][а-я]+\s[А-Я]\.')

    results = []

    for transaction in transactions:
        category = str(transaction.get('Категория', ''))
        description = str(transaction.get('Описание', ''))

        if category == 'Переводы' and name_pattern.search(description):
            results.append(transaction)
            logger.debug(f"Найден перевод физлицу: {description[:100]}")

    logger.info(f"Найдено {len(results)} переводов физическим лицам")
    return json.dumps(results, ensure_ascii=False, indent=2)
