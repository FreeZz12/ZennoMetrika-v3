def schedule_and_filter(accounts: list[Account]) -> list[Account]:
    """
    Функция для фильтрации аккаунтов по времени и дополнительной логике,
    чтобы пропускать те аккаунты, которые не нужно запускать.
    Перебирает аккаунты через фильтры и возвращает новый список аккаунтов для работы.
    :param accounts: список аккаунтов
    :return: список аккаунтов для работы
    """
    # если фильтрация аккаунтов не включена, возвращаем все аккаунты
    if not config.is_schedule:
        return accounts

    # список аккаунтов для работы
    accounts_for_work = []

    # подключение к таблице со статистикой, без аккаунта
    excel = Excel(file='report.xlsx')

    date_limit = datetime.datetime.now() - datetime.timedelta(days=3)

    # перебираем аккаунты
    for account in accounts:
        # подключаем аккаунт к таблице
        excel.connect_account(account)

        # проверяем статус профиля в таблице
        status = excel.get_counter('Status')
        # если статус не равен 'pause', пропускаем аккаунт
        if status != 'pause':
            continue

        # проверяем количество транзакций в таблице
        txs = excel.get_counter('Transactions')
        if txs >= 10:
            continue

        # проверяем баланс профиля в таблице
        balance = excel.get_counter('Balance')
        # если баланс меньше 0.05, пропускаем аккаунт
        if balance < 0.05:
            continue

        # проверяем дату из таблицы
        last_date = excel.get_date('Дата последнего запуска')
        # если дата была после лимита, пропускаем аккаунт
        if last_date > date_limit:
            continue

        # add account in list for work
        accounts_for_work.append(account)

    logger.info(f"Выбрано {len(accounts_for_work)} аккаунтов для работы")

    # возвращаем список аккаунтов для работы
    return accounts_for_work
