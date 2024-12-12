"""API"""

"""
Задание 1 - easy

Напишите функцию для отправки post запросов, на входе принимает:
- url - адрес запроса
- params - параметры запроса (опционально)
- payload - полезная нагрузка (опционально)
- headers - заголовки (опционально)
- proxy - прокси (опционально)
- attempts - количество попыток отправить запрос (опционально, по умолчанию 3)

Функция должна возвращать ответ в виде json (dict или list[dict]) или бросать исключение, если не удалось 
получить ответ за attempts попыток.
"""

# код пишем тут
import requests
import time


def post_request(
        url: str,
        params: dict = None,
        payload: dict = None,
        headers: dict = None,
        proxy: dict = None,
        attempts: int = 3
) -> dict:
    for _ in range(attempts):
        try:
            response = requests.post(url=url, params=params, json=payload, headers=headers, proxies=proxy)
            response.raise_for_status()
            return response.json()
        except Exception:
            time.sleep(5)
    else:
        raise Exception('Не удалось получить данные')


"""
Задание 2 - medium
Напишите функцию, которая принимает список адресов кошельков, обратно возвращает словарь,
где ключи адреса кошельков, а значения - балансы кошельков:
- Для получения баланса используйте API https://api.etherscan.io/.
- Используйте endpoint для запроса балансов у пачки аккаунтов.
- функция должна запрашивать балансы сразу по 20 адресов (или меньше, если адресов меньше 20)
- балансы должны быть в человекочитаемом виде.
"""

def get_request(url: str, params: dict = None, attempts: int = 3) -> dict:
    """
    Функция для отправки get запросов
    :param url:  адрес запроса
    :param params: параметры запроса
    :param attempts: количество попыток отправить запрос
    :return: ответ в виде json
    """
    for _ in range(attempts):
        try:
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception:
            time.sleep(5)
    else:
        raise Exception('Не удалось получить данные')




def check_balances(addresses: list) -> dict:
    """
    Производит проверку балансов кошельков по списку адресов, используя API etherscan.io
    :param addresses: список адресов кошельков
    :return: словарь с балансами кошельков
    """
    url = 'https://api.etherscan.io/v2/api'
    api_key = 'key'

    balances = {}

    for i in range(0, len(addresses), 20):
        addresses_chunk = addresses[i:i + 20]
        params = dict(
            chainid=1,
            module='account',
            action='balancemulti',
            address=','.join(addresses_chunk),
            tag='latest',
            apikey=api_key
        )

        response = get_request(url=url, params=params)
        for item in response['result']:
            balances[item['account']] = int(item['balance']) / 10 ** 18

    return balances





# код пишем тут
"""
Задание 3 - hard
Изучите документацию https://docs.etherscan.io/etherscan-v2/getting-started/v2-quickstart

Доработайте скрипт из задания 2, чтобы балансы проверялись в блокчейнах:
- Ethereum
- Arbitrum
- Linea
- Base

Записывает в словарь суммарный баланс кошелька и балансы по каждому блокчейну.
Балансы должны проверяться пачками по 20 адресов.

Результирующий словарь должен быть в формате:
{'address': {Total: '2.0', 'Ethereum': '0.5', 'Arbitrum': '0.5', 'Linea': '0.5', 'Base': '0.5'}}

"""

# код пишем тут

def check_balances_multichain(addresses: list) -> dict:
    """
    Производит проверку балансов кошельков по списку адресов, используя API etherscan.io
    :param addresses: список адресов кошельков
    :return: словарь с балансами кошельков
    """
    url = 'https://api.etherscan.io/v2/api'
    api_key = 'key'
    chains = {
        'Ethereum': 1,
        'Arbitrum': 42161,
        'Linea': 59144,
        'Base': 8453
    }

    balances = {}

    for chain_name, chain_id in chains.items():
        for i in range(0, len(addresses), 20):
            addresses_chunk = addresses[i:i + 20]
            params = dict(
                chainid=chain_id,
                module='account',
                action='balancemulti',
                address=','.join(addresses_chunk),
                tag='latest',
                apikey=api_key
            )

            response = get_request(url=url, params=params)
            for item in response['result']:
                if item['account'] not in balances:
                    balances[item['account']] = {'Total': 0}
                balances[item['account']][chain_name] = int(item['balance']) / 10 ** 18
                balances[item['account']]['Total'] += int(item['balance']) / 10 ** 18



    return balances

balances = check_balances_multichain(['0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae', '0x8d12a197cb00d4747a1fe03395095ce2a5cc6819'])
print(balances)
