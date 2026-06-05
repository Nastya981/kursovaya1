import pytest
import pandas as pd
import json
from unittest.mock import patch, Mock
from src.services import search_transfers_to_individuals
from src.reports import spending_by_category, report_decorator
from src.views import get_card_info, get_top_transactions, load_user_settings, get_currency_rates, get_stock_prices


def test_search_transfers_to_individuals():
    """Тест поиска переводов физическим лицам"""
    transactions = [
        {"Категория": "Переводы", "Описание": "Перевод Валерий А."},
        {"Категория": "Переводы", "Описание": "Перевод организации"},
        {"Категория": "Супермаркеты", "Описание": "Покупка"},
    ]
    result = json.loads(search_transfers_to_individuals(transactions))
    assert len(result) == 1


def test_load_user_settings():
    """Тест загрузки настроек пользователя"""
    settings = load_user_settings()
    assert "user_currencies" in settings
    assert "user_stocks" in settings


def test_get_card_info():
    """Тест получения информации о картах"""
    df = pd.DataFrame({
        'Номер карты': [1234567812345678, 1234567812345678],
        'Сумма операции': [-100.50, -200.00]
    })
    result = get_card_info(df)
    assert len(result) == 1
    assert result[0]['total_spent'] == 300.50
    # Кешбэк: 1 рубль на каждые 100 рублей -> 300.50 / 100 = 3.005, округляется до 3.0
    assert result[0]['cashback'] == 3.0


def test_get_top_transactions():
    """Тест получения топ транзакций"""
    df = pd.DataFrame({
        'Дата операции': ['2024-01-15', '2024-01-20'],
        'Сумма платежа': [1000.00, 500.00],
        'Категория': ['Супермаркеты', 'Рестораны'],
        'Описание': ['Покупка 1', 'Покупка 2']
    })
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    result = get_top_transactions(df, limit=2)
    assert len(result) == 2
    assert result[0]['amount'] == 1000.00


@patch('src.views.requests.get')
def test_get_currency_rates(mock_get):
    """Тест получения курсов валют с моком"""
    mock_response = Mock()
    mock_response.json.return_value = {'rates': {'USD': 1.0, 'EUR': 0.92}}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = get_currency_rates(['USD', 'EUR'])
    assert len(result) == 2


def test_get_stock_prices():
    """Тест получения цен акций"""
    result = get_stock_prices(['AAPL', 'AMZN'])
    assert len(result) == 2
    assert 'stock' in result[0]
    assert 'price' in result[0]
