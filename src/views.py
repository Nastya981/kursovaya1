import json
from datetime import datetime
from typing import Dict, Any, List

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


def filter_transactions_by_date_range(transactions: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Фильтрует транзакции по диапазону дат
    """
    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        mask = (transactions['Дата операции'] >= start) & (transactions['Дата операции'] <= end)
        return transactions[mask]
    except Exception as e:
        logger.error(f"Ошибка фильтрации по дате: {e}")
        return transactions


def get_expenses_by_category(transactions: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализирует расходы по категориям
    Возвращает топ-7 категорий, остальное, переводы и наличные
    """
    # Фильтруем только расходы (отрицательные суммы)
    expenses = transactions[transactions['Сумма операции'] < 0].copy()
    expenses['Сумма операции'] = expenses['Сумма операции'].abs()

    # Группируем по категориям
    category_totals = expenses.groupby('Категория')['Сумма операции'].sum().round().astype(int)

    # Категории "Наличные" и "Переводы" для отдельного блока
    transfers_and_cash_categories = ['Наличные', 'Переводы']
    transfers_and_cash = {}
    main_categories = {}

    for cat, amount in category_totals.items():
        if cat in transfers_and_cash_categories:
            transfers_and_cash[cat] = int(amount)
        else:
            main_categories[cat] = int(amount)

    # Сортируем основные категории по убыванию
    sorted_main = sorted(main_categories.items(), key=lambda x: x[1], reverse=True)

    # Берём топ-7
    top_7 = [{"category": cat, "amount": amount} for cat, amount in sorted_main[:7]]

    # Остальное
    other_amount = sum(amount for _, amount in sorted_main[7:])
    if other_amount > 0:
        top_7.append({"category": "Остальное", "amount": other_amount})

    # Переводы и наличные
    transfers_cash_list = [{"category": cat, "amount": amount} for cat, amount in sorted(transfers_and_cash.items(), key=lambda x: x[1], reverse=True)]

    total_expenses = int(expenses['Сумма операции'].sum())

    return {
        "total_amount": total_expenses,
        "main": top_7,
        "transfers_and_cash": transfers_cash_list
    }


def get_income_by_category(transactions: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализирует поступления по категориям
    """
    # Фильтруем только поступления (положительные суммы)
    income = transactions[transactions['Сумма операции'] > 0].copy()

    # Группируем по категориям
    category_totals = income.groupby('Категория')['Сумма операции'].sum().round().astype(int)

    # Сортируем по убыванию
    sorted_income = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    main_income = [{"category": cat, "amount": amount} for cat, amount in sorted_income]

    total_income = int(income['Сумма операции'].sum())

    return {
        "total_amount": total_income,
        "main": main_income
    }


def get_top_cashback_categories(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Возвращает топ-3 категории с наибольшим кешбэком
    Кешбэк = траты / 100
    """
    # Фильтруем расходы
    expenses = transactions[transactions['Сумма операции'] < 0].copy()
    expenses['Сумма операции'] = expenses['Сумма операции'].abs()

    # Группируем по категориям и считаем кешбэк
    category_cashback = expenses.groupby('Категория')['Сумма операции'].sum().apply(lambda x: round(x / 100, 2))

    # Сортируем по убыванию и берём топ-3
    top_3 = category_cashback.nlargest(3)

    result = [{"category": cat, "cashback": amount} for cat, amount in top_3.items()]

    return result


def events_page(date_time_str: str, period: str = 'M') -> str:
    """
    Страница "События"
    Принимает дату и время в формате 'YYYY-MM-DD HH:MM:SS' и период (W, M, Y, ALL)
    Возвращает JSON-ответ с расходами, поступлениями, курсами валют и акциями
    """
    logger.info(f"Запрос страницы событий для даты: {date_time_str}, период: {period}")

    try:
        df = pd.read_excel('data/operations.xlsx')
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')
    except Exception as e:
        logger.error(f"Ошибка загрузки Excel: {e}")
        return json.dumps({"error": "Не удалось загрузить данные"}, ensure_ascii=False)

    target_datetime = pd.to_datetime(date_time_str)

    # Определяем диапазон дат в зависимости от периода
    if period == 'W':
        start_date = target_datetime - pd.Timedelta(days=target_datetime.weekday())
        end_date = target_datetime
    elif period == 'M':
        start_date = target_datetime.replace(day=1)
        end_date = target_datetime
    elif period == 'Y':
        start_date = target_datetime.replace(month=1, day=1)
        end_date = target_datetime
    elif period == 'ALL':
        start_date = pd.to_datetime('2000-01-01')
        end_date = target_datetime
    else:
        start_date = target_datetime.replace(day=1)
        end_date = target_datetime

    # Фильтруем транзакции по диапазону
    filtered_df = filter_transactions_by_date_range(df, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    # Получаем расходы и поступления
    expenses_data = get_expenses_by_category(filtered_df)
    income_data = get_income_by_category(filtered_df)

    # Получаем топ-3 категории кешбэка
    top_cashback = get_top_cashback_categories(filtered_df)

    # Загружаем настройки пользователя
    settings = load_user_settings()

    # Получаем курсы валют
    currency_rates = get_currency_rates(settings.get('user_currencies', ['USD', 'EUR']))

    # Получаем цены акций
    stock_prices = get_stock_prices(settings.get('user_stocks', ['AAPL', 'AMZN', 'GOOGL']))

    # Формируем JSON-ответ
    result = {
        "expenses": expenses_data,
        "income": income_data,
        "top_cashback_categories": top_cashback,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    logger.info("JSON-ответ для страницы событий успешно сформирован")
    return json.dumps(result, ensure_ascii=False, indent=2)


def filter_transactions_by_date(transactions: pd.DataFrame, target_date: str) -> pd.DataFrame:
    """Фильтрует транзакции с начала месяца target_date по target_date"""
    try:
        target_datetime = pd.to_datetime(target_date)
        start_of_month = target_datetime.replace(day=1)
        mask = (transactions['Дата операции'] >= start_of_month) & (transactions['Дата операции'] <= target_datetime)
        return transactions[mask]
    except Exception as e:
        logger.error(f"Ошибка фильтрации по дате: {e}")
        return transactions


def main_page(date_time_str: str) -> str:
    """Главная страница"""
    logger.info(f"Запрос главной страницы для даты: {date_time_str}")

    try:
        df = pd.read_excel('data/operations.xlsx')
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
