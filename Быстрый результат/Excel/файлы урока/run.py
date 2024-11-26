import datetime
import random
import time

from eth_account import Account
from loguru import logger

from config import config, Chains, Tokens
from core.bot import Bot
from core.onchain import Onchain
from core.excel import Excel
from utils.logging import init_logger
from utils.utils import random_sleep, get_accounts, generate_password, get_price_token


def main():
    """ Основная функция """
    # Инициализация консоли и логгера
    init_logger()
    # Получаем список аккаунтов из файлов
    accounts = get_accounts()

    for i in range(config.cycle):
        # Перебираем аккаунты
        for account in accounts:
            # передаем аккаунт в функцию worker
            # здесь можно добавить логику получения данных из Excel и пропуска профиля, если он уже был обработан
            worker(account)

    logger.success("Все аккаунты обработаны")


def worker(account: Account) -> None:
    """
    Функция для работы с аккаунтом, создает бота и передает его в функцию activity
    :param account: аккаунт
    :return: None
    """

    # if not schedule(account):
    #     return

    # Создаем бота, если в конфиге включен is_browser_run, то будет запущен браузер
    with Bot(account) as bot:
        # Вызываем функцию activity и передаем в нее бота
        activity(bot)

    random_sleep(*config.pause_between_profile)


def schedule_and_filter(account: Account) -> bool:
    """
    Функция для фильтрации аккаунтов по времени и дополнительной логике, чтобы пропускать те аккаунты, которые не нужно обрабатывать.
    :param account: аккаунт
    :return: bool, если True, то аккаунт будет обработан, иначе пропущен
    """
    excel = Excel(account)
    # date = excel.get_date('Последн. транз')
    # if date < 20/11/2024:
    #     return True
    return False


def activity(bot: Bot):
    """
    Функция для работы с ботом, описываем логику активности бота.
    :param bot: бот
    :return: None
    """
    print(bot.excel.acc_row)

    excel_report = Excel(bot.account, 'report.xlsx')

    excel_report.set_date('Date')

    #
    # seeds = bot.excel.get_column('Seed')
    # for seed in seeds:
    #     print(seed)
    #
    # account_data = bot.excel.get_row()
    # for value in account_data:
    #     print(value)
    #
    # bot.excel.get_cell('Password')
    #
    # bot.excel.set_cell('Password1', 'value')
    #
    # bot.excel.get_counter('Swap')
    # bot.excel.increase_counter('Swap')
    # bot.excel.set_date('Последн. транз')
    # last_trans_date = bot.excel.get_date('Последн. транз')
    #


if __name__ == '__main__':
    main()
