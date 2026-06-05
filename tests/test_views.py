import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.views import get_greeting, filter_transactions_by_date
from src.services import simple_search, search_by_phone_numbers
from src.reports import spending_by_category
import json


def test_get_greeting():
    """Тест приветствия"""
    greeting = get_greeting()
    assert greeting in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]


def test_simple_search():
    """Тест простого поиска"""
    transactions = [
        {"Описание": "Покупка в магазине", "Категория": "Супермаркеты"},
        {"Описание": "Оплата ЖКХ", "Категория": "Коммунальные"},
    ]
    result = json.loads(simple_search(transactions, "магазин"))
    assert len(result) == 1
    assert "магазин" in result[0]["Описание"].lower()


def test_simple_search_empty():
    """Тест поиска с пустым запросом"""
    transactions = [{"Описание": "Покупка"}]
    result = json.loads(simple_search(transactions, ""))
    assert result == []


def test_search_by_phone_numbers():
    """Тест поиска по телефонным номерам"""
    transactions = [
        {"Описание": "МТС +7 921 11-22-33"},
        {"Описание": "Покупка в магазине"},
    ]
    result = json.loads(search_by_phone_numbers(transactions))
    assert len(result) == 1


def test_filter_transactions_by_date():
    """Тест фильтрации по дате"""
    df = pd.DataFrame({
        'Дата операции': ['2024-01-15', '2024-01-20', '2024-02-01'],
        'Сумма': [100, 200, 300]
    })
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    result = filter_transactions_by_date(df, '2024-01-20')
    assert len(result) == 2
