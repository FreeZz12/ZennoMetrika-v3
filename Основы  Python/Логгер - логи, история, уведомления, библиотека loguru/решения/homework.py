""""""
import datetime
import os

"""
Задание 1 - easy
Напишите настройку логера, чтобы он писал логи в файл,
каждый день создавал новый файл, и хранил историю логов за 7 дней.

"""
import sys

from loguru import logger

logger.remove()
logger.add(
    'logs.log',
    level='DEBUG',
    rotation=datetime.timedelta(days=1),
    format="<light-cyan>{time:DD-MM HH:mm:ss}</light-cyan> | <level> {level: <8} </level><white> {file}:{function}: {line}</white> - <light-white>{message}</light-white>",
    retention='7 days'
)
# код пишем тут

"""
Задание 2  - medium

Напишите конфигурацию логера, чтобы он писал разноцветные логи в терминале в формате:
"01.01.2025 15:00:00 - main.py: main: 47 - [INFO] 
У разных частей сообщения разный цвет.

"""
# logger.remove() - ставить один раз перед настройкой логера
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<light-cyan>{time:DD-MM HH:mm:ss}</light-cyan> | <level> {level: <8} </level><white> {file}:{function}: {line}</white> - <light-white>{message}</light-white>",
)

logger.info("Логгер инициализирован")

