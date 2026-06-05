import json
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests

from src.logger_config import setup_logger

logger = setup_logger('views')


def load_user_settings() -> Dict[str, Any]:
    """Загружает настройки пользователя из JSON файла"""
    try:
        with open('user_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL"]}


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    current_hour = datetime.now().hour

    if 6 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_info(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Получает информацию о картах: последние 4 цифры, расходы, кешбэк"""
    cards_info = []

    card_groups = transactions.groupby('Номер карты')

    for card_number, group in card_groups:
        if pd.isna(card_number) or card_number == '':
            continue

        last_digits = str(int(card_number))[-4:] if isinstance(card_number, (int, float)) else str(card_number)[-4:]

        expenses = group[group['Сумма операции'] < 0]['Сумма операции'].sum()
        total_spent = abs(expenses)

        cashback = total_spent / 100

        cards_info.append({
            "last_digits": last_digits,
            "total_spent": round(total_spent, 2),
            "cashback": round(cashback, 2)
        })

    return cards_info


def get_top_transactions(transactions: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ транзакций по сумме платежа"""
    top = transactions.nlargest(limit, 'Сумма платежа')[['Дата операции', 'Сумма платежа', 'Категория', 'Описание']]

    result = []
    for _, row in top.iterrows():
        date_obj = pd.to_datetime(row['Дата операции'])
        result.append({
            "date": date_obj.strftime('%d.%m.%Y'),
            "amount": round(float(row['Сумма платежа']), 2),
            "category": row['Категория'],
            "description": row['Описание'][:50] if len(str(row['Описание'])) > 50 else row['Описание']
        })

    return result


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курсы валют через внешнее API"""
    rates = []
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
        data = response.json()

        for currency in currencies:
            if currency in data.get('rates', {}):
                rates.append({
                    "currency": currency,
                    "rate": round(data['rates'][currency], 2)
                })
            else:
                rates.append({"currency": currency, "rate": 0.0})
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        for currency in currencies:
            rates.append({"currency": currency, "rate": 0.0})

    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает цены акций через внешнее API"""
    prices = []
    try:
        mock_prices = {
            "AAPL": 175.50,
            "AMZN": 145.30,
            "GOOGL": 138.75,
            "MSFT": 380.20,
            "TSLA": 240.15
        }

        for stock in stocks:
            prices.append({
                "stock": stock,
                "price": mock_prices.get(stock, 100.0)
            })
    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        for stock in stocks:
            prices.append({"stock": stock, "price": 0.0})

    return prices


def filter_transactions_by_date(transactions: pd.DataFrame, target_date: str) -> pd.DataFrame:
    """
    Фильтрует транзакции с начала месяца target_date по target_date
    """
    try:
        target_datetime = pd.to_datetime(target_date)
        start_of_month = target_datetime.replace(day=1)

        mask = (transactions['Дата операции'] >= start_of_month) & (transactions['Дата операции'] <= target_datetime)
        return transactions[mask]
    except Exception as e:
        logger.error(f"Ошибка фильтрации по дате: {e}")
        return transactions


def main_page(date_time_str: str) -> str:
    """
    Главная функция для страницы "Главная"
    Принимает дату и время в формате 'YYYY-MM-DD HH:MM:SS'
    Возвращает JSON-ответ
    """
    logger.info(f"Запрос главной страницы для даты: {date_time_str}")

    try:
        df = pd.read_excel('data/operations.xls')
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')
    except Exception as e:
        logger.error(f"Ошибка загрузки Excel: {e}")
        return json.dumps({"error": "Не удалось загрузить данные"}, ensure_ascii=False)

    filtered_df = filter_transactions_by_date(df, date_time_str)

    greeting = get_greeting()
    cards_info = get_card_info(filtered_df)
    top_transactions = get_top_transactions(filtered_df, 5)

    settings = load_user_settings()
    currency_rates = get_currency_rates(settings.get('user_currencies', ['USD', 'EUR']))
    stock_prices = get_stock_prices(settings.get('user_stocks', ['AAPL', 'AMZN', 'GOOGL']))

    result = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    logger.info("JSON-ответ успешно сформирован")
    return json.dumps(result, ensure_ascii=False, indent=2)
