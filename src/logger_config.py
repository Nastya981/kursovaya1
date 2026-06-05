import logging
import os


def setup_logger(module_name: str, log_level: int = logging.DEBUG) -> logging.Logger:
    """
    Настраивает логгер для указанного модуля.

    Args:
        module_name: Имя модуля (будет использовано в имени файла лога)
        log_level: Уровень логирования (по умолчанию DEBUG)

    Returns:
        Настроенный логгер
    """
    # Создаём папку logs если её нет
    os.makedirs('logs', exist_ok=True)

    # Создаём логгер
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)

    # Очищаем старые обработчики, чтобы логи не дублировались
    if logger.handlers:
        logger.handlers.clear()

    # Создаём обработчик для записи в файл - mode='a' для дозаписи
    log_file = f'logs/{module_name}.log'
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(log_level)

    # Формат лога: время | модуль | уровень | сообщение
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    return logger
