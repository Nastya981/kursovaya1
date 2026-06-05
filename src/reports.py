import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

import pandas as pd

from src.logger_config import setup_logger

logger = setup_logger('reports')


def report_decorator(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения результатов отчёта в файл.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            output_filename = filename if filename else f"report_{func.__name__}.json"

            try:
                if isinstance(result, pd.DataFrame):
                    output_data = result.to_dict(orient='records')
                else:
                    output_data = result

                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)

                logger.info(f"Отчёт сохранён в файл: {output_filename}")
            except Exception as e:
                logger.error(f"Ошибка сохранения отчёта: {e}")

            return result
        return wrapper
    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца.
    """
    logger.info(f"Отчёт по категории: {category}, дата: {date}")

    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], errors='coerce')

    mask = (transactions['Дата операции'] >= start_date) & \
           (transactions['Дата операции'] <= end_date) & \
           (transactions['Категория'] == category)

    result = transactions[mask][['Дата операции', 'Сумма операции', 'Описание', 'Категория']]

    logger.info(f"Найдено {len(result)} транзакций по категории '{category}'")
    return result
