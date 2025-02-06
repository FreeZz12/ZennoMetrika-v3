""""""
import time
from pprint import pprint

"""
Задание 1 - easy
Создайте класс Chain, который будет иметь 3 атрибута: 
name
okx_name
binance_name

Создайте класс Chains, который будет хранить в себе список объектов класса Chain.
Создайте объекты сетей для сетей:
- Binance Smart Chain
- Ethereum
- Polygon
- Arbitrum One
- Optimism
- Avalanche
- Solana

Укажите корректные названия для сетей на биржах Binance и OKX.

"""

class Chain:

    def __init__(self, name: str, okx_name: str, binance_name: str):
        self.name = name
        self.okx_name = okx_name
        self.binance_name = binance_name

class Chains:

    Binance_Smart_Chain = Chain('Binance Smart Chain', 'BSC', 'BSC')
    Ethereum = Chain('Ethereum', 'ERC20', 'ETH')
    Polygon = Chain('Polygon', 'Polygon', 'MATIC')
    Arbitrum_One = Chain('Arbitrum One', 'Arbitrum One', 'ARBITRUM')
    Optimism = Chain('Optimism', 'Optimism', 'OPTIMISM')
    Avalanche = Chain('Avalanche', 'Avalanche C-Chain', 'AVAX')
    Solana = Chain('Solana', 'Solana', 'SOL')

"""
Задание 2 - medium

Скрипт вывода токенов с биржи OKX.
Напишите скрипт, который берет кошельки из файла wallets.txt и с паузой в 60-1200 секунд
пополняет их токеном ETH в сети Arbitrum на сумму от 0.01 до 0.1 ETH, округляя до 3 знаков после запятой.
Кошельки должны пополниться по 1 разу, но в рандомном порядке.
Можете использовать любой способ работы с api: запросы, SDK, ccxt.
"""


class OkxClient:

    def __init__(self):
        self.endpoint = 'https://www.okx.com'
        self.proxies = {
            'http': config.PROXY.get_secret_value(),  # 'http://user:pass@ip:port'
            'https': config.PROXY.get_secret_value()  # 'http://user:pass@ip:port'
        }

    def get_headers(self, method: str, request_path: str, body: dict | None = None) -> dict:
        """
        Собирает заголовки для запроса к бирже OKX, с подписью
        :param method: метод
        :param request_path: путь запроса
        :param body: тело запроса
        :return: словарь с подписью
        """
        body = json.dumps(body) if body else ''
        # подготовка данных для подписи
        date = datetime.now(UTC)
        ms = str(date.microsecond).zfill(6)[:3]
        timestamp = f'{date:%Y-%m-%dT%H:%M:%S}.{ms}Z'

        # подпись
        message = timestamp + method.upper() + request_path + body
        mac = hmac.new(
            bytes(config.OKX_SECRET_KEY.get_secret_value(), encoding="utf-8"),
            bytes(message, encoding="utf-8"),
            digestmod="sha256",
        )
        signature = base64.b64encode(mac.digest()).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": config.OKX_API_KEY.get_secret_value(),
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": config.OKX_PASSPHRASE.get_secret_value(),
            'x-simulated-trading': '0'
        }
        return headers

    def get_info(self) -> list[dict]:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        path = '/api/v5/asset/currencies'
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        print(response.text)
        print(response.status_code)
        response.raise_for_status()
        data = response.json()
        pprint(data)
        return data

    def withdraw(self, token: str, amount: float, network: str, address: str) -> None:
        """
        Отправляет запрос на вывод токена с биржи
        :param token: название токена
        :param amount: сумма вывода
        :param network: название сети в соответствии с биржей
        :param address: адрес кошелька получателя
        :return: None
        """
        path = '/api/v5/asset/withdrawal'
        chain_with_network = f'{token}-{network}'
        body = dict(
            ccy=token,
            amt=amount,
            dest=4,
            toAddr=address,
            chain=chain_with_network,
        )
        url = self.endpoint + path
        headers = self.get_headers('POST', path, body)
        response = requests.post(url, headers=headers, proxies=self.proxies, json=body)
        print(response.text)
        response.raise_for_status()
        data = response.json()
        if data.get('code') != '0':
            raise Exception(f'Withdraw fail: {data.get("msg")}')
        withdraw_id = data.get('data')[0].get('wdId')
        for _ in range(60):
            status = self.get_withdraw_status(withdraw_id)
            if str(status) == "2":
                print('Withdraw success')
                return
            time.sleep(5)

    def get_sub_accs(self) -> list[dict]:
        """
        Получает информацию о субаккаунтах
        :return: список словарей с информацией о субаккаунтах
        """
        path = '/api/v5/users/subaccount/list'
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        response.raise_for_status()
        data = response.json()
        sub_names = [sub.get('subAcct') for sub in data.get('data', [])]
        pprint(sub_names)
        return sub_names

    def get_sub_acc_trading_balance(self, sub_acc_name: str) -> list[dict]:
        """
        Получает информацию о балансе торгового счета субаккаунта
        :param sub_acc_name: название субаккаунта
        :return: список словарей с информацией о балансе
        """
        path = f'/api/v5/account/subaccount/balances?subAcct={sub_acc_name}'
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        response.raise_for_status()
        data = response.json()
        pprint(data)
        return data.get('data', [{}])[0].get('details', [{}])

    def get_sub_acc_funding_balance(self, sub_acc_name: str) -> list[dict]:
        """
        Получает информацию о балансе торгового счета субаккаунта
        :param sub_acc_name: название субаккаунта
        :return: список словарей с информацией о балансе
        """
        path = f'/api/v5/asset/subaccount/balances?subAcct={sub_acc_name}'
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        response.raise_for_status()
        data = response.json()
        pprint(data)
        return data.get('data', [{}])

    def transfer_sub_to_main(self):
        """
        Переводит средства с торгового счета на финансовый
        :return: None
        """
        sub_names = self.get_sub_accs()
        tasks = [
            dict(func=self.get_sub_acc_trading_balance, type_id=18),
            dict(func=self.get_sub_acc_funding_balance, type_id=6)
        ]
        for task in tasks:
            func = task.get('func')
            type_id = task.get('type_id')
            for sub_name in sub_names:
                sub_balances = func(sub_name)
                for balance in sub_balances:
                    if float(balance.get('availBal', 0)) <= 0:
                        continue
                    path = '/api/v5/asset/transfer'
                    body = {
                        'type': 2,
                        'ccy': balance.get('ccy'),
                        'amt': balance.get('availBal'),
                        'from': type_id,
                        'to': 6,
                        'subAcct': sub_name,
                    }
                    url = self.endpoint + path
                    headers = self.get_headers('POST', path, body)
                    response = requests.post(url, headers=headers, proxies=self.proxies, json=body)
                    response.raise_for_status()
                    data = response.json()
                    if data.get('code') != '0':
                        raise Exception(f'Withdraw fail: {data.get("msg")}')
                    pprint(data)

    def get_balance_funding(self) -> list[dict]:
        """
        Получает информацию о балансе финансового счета
        :return:  список словарей с информацией о балансе
        """
        path = '/api/v5/asset/balance'
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [{}])

    def get_balance_trading(self) -> list[dict]:
        """
        Получает информацию о балансе торгового счета
        :return:  список словарей с информацией о балансе
        """
        path = '/api/v5/account/balance'  # trading
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        response.raise_for_status()
        data = response.json()
        pprint(data)
        return data.get('data', [{}])[0].get('details', [{}])

    def transfer_trading_to_funding(self):
        """
        Переводит средства с торгового счета на финансовый
        :return: None
        """
        path = '/api/v5/asset/transfer'

        trading_balances = self.get_balance_trading()
        for balance_data in trading_balances:
            balance = float(balance_data.get('availBal', 0))
            if balance <= 0:
                continue
            body = {
                'type': 0,
                'ccy': balance_data.get('ccy'),
                'amt': balance_data.get('availBal'),
                'from': 18,
                'to': 6
            }
            url = self.endpoint + path
            headers = self.get_headers('POST', path, body)
            response = requests.post(url, headers=headers, proxies=self.proxies, json=body)
            response.raise_for_status()
            data = response.json()
            if data.get('code') != '0':
                raise Exception(f'Withdraw fail: {data.get("msg")}')

    def get_withdraw_status(self, withdraw_id: str) -> str:
        """
        Получает статус вывода.
        -4: не найдено в истории выводов

        Стадия 1: Ожидание вывода средств
        17: Ожидание ответа от поставщика Правил путешествий
        10: Ожидание перевода
        0: Ожидание снятия
        4/5/6/8/9/12: Ожидание проверки вручную
        7: Утверждено\n

        Стадия 2: Вывод средств в процессе (применимо к выводу средств в блокчейн,
        внутренние переводы не имеют этой стадии)
        1: Трансляция вашей транзакции в блокчейн
        15: Ожидание подтверждения транзакции
        16: В связи с местными законами и правилами, ваш вывод может занять до 24 часов
        -3: Отмена

        Заключительный этап
        -2: Отменено
        -1: Неудача
        2: Успех

        10 - ожидание перевода, 0 - ожидание вывода,
        :param withdraw_id: идентификатор вывода
        :return: статус вывода
        """
        path = f'/api/v5/asset/withdrawal-history?wdId={withdraw_id}'
        url = self.endpoint + path
        headers = self.get_headers('GET', path)
        response = requests.get(url, headers=headers, proxies=self.proxies)
        response.raise_for_status()
        data = response.json()
        status = data.get('data', [{}])[0].get('state', -4)
        return status


def main():
    with open('wallets.txt') as f:
        wallets = f.read().splitlines()

    binance = OkxClient()

    random.shuffle(wallets)

    for wallet in wallets:
        amount = round(random.uniform(0.01, 0.1), 3)
        binance.withdraw('ETH', amount, 'Arbitrum One', wallet)
        print(f'Пополнение кошелька {wallet} на {amount} ETH')
        time.sleep(random.randint(60, 1200))


"""
Задание 3 - hard

Выберите одну из бирж, которая вас интересует (например Bybit, Mexc и т.д.) и создайте 
класс клиента на примере классов для OKX и Binance.

Должны быть реализованы методы:
- получения информации о токенах и сетях
- вывода токена с биржи
- получения статуса вывода

Для реализации можете использовать любой способ работы с api: запросы, SDK, ccxt.
"""

import pybit
from pybit.unified_trading import HTTP


class BybitClient:

    def __init__(self):
        self.client = HTTP(
            testnet=False,
            api_key="...",
            api_secret="...",
        )

    def get_info(self) -> list[dict]:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        tokens_info = self.client.get_coin_info()
        pprint(tokens_info)
        return tokens_info

    def get_status_withdraw(self, withdraw_id: str) -> str:
        """
        Получает статус вывода.
        SecurityCheck, Pending, success, CancelByUser,
        Reject, Fail, BlockchainConfirmed,
        MoreInformationRequired, Unknown a rare status,
        :param withdraw_id:
        :return: статус вывода
        """
        withdraw_history = self.client.get_withdrawal_records()
        for withdraw_info in withdraw_history:
            if withdraw_info.get('withdrawId') == withdraw_id:
                return withdraw_info.get('status')
        return 'not found'

    def withdraw(self, token: str, amount: float, network: str, address: str) -> None:
        """
        Отправляет запрос на вывод токена с биржи
        :param token: название токена
        :param amount: сумма вывода
        :param network: название сети в соответствии с биржей
        :param address: адрес кошелька получателя
        :return: None
        """
        response = self.client.withdraw(
            coin=token,
            amount=amount,
            chain=network,
            address=address,
            timestamp=int(time.time() * 1000),
        )
        withdraw_id = response.get('result', {}).get('id')
        for _ in range(60):
            status = self.get_status_withdraw(withdraw_id)
            if status == 'success':
                print('Withdraw success')
                return
            time.sleep(5)
        else:
            print('Withdraw fail')

