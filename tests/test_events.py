import pytest
import pandas as pd
import json
from unittest.mock import patch, Mock
from src.views import (
    get_expenses_by_category, get_income_by_category,
    get_top_cashback_categories, events_page
)


def test_get_expenses_by_category():
    """Тест анализа расходов по категориям"""
    df = pd.DataFrame({
        'Категория': ['Супермаркеты', 'Рестораны', 'Супермаркеты', 'Переводы', 'Наличные'],
        'Сумма операции': [-100, -200, -50, -300, -150]
    })
    result = get_expenses_by_category(df)
    assert 'total_amount' in result
    assert 'main' in result
    assert 'transfers_and_cash' in result
    assert result['total_amount'] == 800


def test_get_income_by_category():
    """Тест анализа поступлений по категориям"""
    df = pd.DataFrame({
        'Категория': ['Зарплата', 'Кешбэк', 'Зарплата'],
        'Сумма операции': [50000, 500, 10000]
    })
    result = get_income_by_category(df)
    assert result['total_amount'] == 60500
    assert len(result['main']) == 2


def test_get_top_cashback_categories():
    """Тест топ-3 категорий кешбэка"""
    df = pd.DataFrame({
        'Категория': ['Супермаркеты', 'Рестораны', 'Супермаркеты', 'Аптека', 'Рестораны'],
        'Сумма операции': [-1000, -5000, -2000, -300, -3000]
    })
    result = get_top_cashback_categories(df)
    assert len(result) == 3
    # Рестораны: 5000+3000=8000, кешбэк = 8000/100 = 80
    assert result[0]['cashback'] == 80.0
    # Супермаркеты: 1000+2000=3000, кешбэк = 3000/100 = 30
    assert result[1]['cashback'] == 30.0
    # Аптека: 300, кешбэк = 300/100 = 3
    assert result[2]['cashback'] == 3.0


@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
def test_events_page(mock_stocks, mock_currency):
    """Тест страницы событий"""
    mock_currency.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 175.0}]

    result = events_page('2024-01-20 12:00:00', 'M')
    data = json.loads(result)

    assert 'expenses' in data
    assert 'income' in data
    assert 'currency_rates' in data
    assert 'stock_prices' in data
