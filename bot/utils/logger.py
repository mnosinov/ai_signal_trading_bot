import logging
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = "trading_bot.log",
    level: int = logging.INFO,
    console: bool = True,
) -> logging.Logger:
    """
    Настройка логгера с выводом в файл и/или консоль.

    Args:
        name: Имя логгера
        log_file: Путь к файлу логов (None - не писать в файл)
        level: Уровень логирования
        console: Выводить логи в консоль
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_file:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(logs_dir / log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
