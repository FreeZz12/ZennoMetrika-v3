""""""


"""
Задание 1 - easy
Напишите скрипт, который отправляет запрос на Binance при помощи requests и
выводит в консоль баланс токена ETH на spot аккаунте биржи.

"""
import random
import requests
import hashlib
import hmac
import time
from pprint import pprint

class BinanceClient:

    def __init__(self):
        self.endpoint = 'https://api.binance.com'
        self.proxies = {
            'http': config.PROXY.get_secret_value(),
            'https': config.PROXY.get_secret_value()
        }
        self.headers = {
            'X-MBX-APIKEY': config.BINANCE_API_KEY.get_secret_value()
        }

    def sign_params(self, params: dict):
        """
        Подписывает запрос к binance в исходном словаре
        :param params: словарь параметров
        :return: None
        """
        params['timestamp'] = int(time.time() * 1000)

        payload = '&'.join(f'{param}={value}' for param, value in params.items())

        signature = hmac.new(
            config.BINANCE_SECRET_KEY.get_secret_value().encode('utf-8'),
            payload.encode('utf-8'), hashlib.sha256).hexdigest()

        params['signature'] = signature

    def get_balance(self, token: str) -> float:
        """
        Получает баланс токена на бирже, если токен найден
        :param token: тикер токена
        :return: баланс токена
        """
        path = '/api/v3/account'
        params = dict()
        self.sign_params(params)
        url = self.endpoint + path
        response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
        data = response.json()
        for balance in data['balances']:
            if balance['asset'] == token:
                print(f'Баланс {token}: {balance["free"]}')
                return balance['free']
        print(f'Токен {token} не найден')
        return 0

def main():
    binance = BinanceClient()
    binance.get_balance('ETH')


"""
Задание 2  - medium

Напишите скрипт, который берет кошельки из файла wallets.txt и с паузой в 60-1200 секунд
пополняет их токеном ETH в сети Arbitrum на сумму от 0.01 до 0.1 ETH, округляя до 3 знаков после запятой.
Кошельки должны пополниться по 1 разу, но в рандомном порядке.
Можете использовать любой способ работы с api: запросы, SDK, ccxt.
"""

class BinanceClient:

    def __init__(self):
        self.endpoint = 'https://api.binance.com'
        self.proxies = {
            'http': config.PROXY.get_secret_value(),
            'https': config.PROXY.get_secret_value()
        }
        self.headers = {
            'X-MBX-APIKEY': config.BINANCE_API_KEY.get_secret_value()
        }

    def sign_params(self, params: dict):
        """
        Подписывает запрос к binance в исходном словаре
        :param params: словарь параметров
        :return: None
        """
        params['timestamp'] = int(time.time() * 1000)

        payload = '&'.join(f'{param}={value}' for param, value in params.items())

        signature = hmac.new(
            config.BINANCE_SECRET_KEY.get_secret_value().encode('utf-8'),
            payload.encode('utf-8'), hashlib.sha256).hexdigest()

        params['signature'] = signature

    def get_info(self) -> list[dict]:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        path = '/sapi/v1/capital/config/getall'
        params = dict()
        self.sign_params(params)
        url = self.endpoint + path
        response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
        data = response.json()
        pprint(data)
        return data

    def get_status_withdraw(self, withdraw_id: str):
        path = '/sapi/v1/capital/withdraw/history'
        params = dict()
        self.sign_params(params)
        url = self.endpoint + path
        response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
        withdraws = response.json()
        for withdraw_info in withdraws:
            if withdraw_info.get('id') == withdraw_id:
                return withdraw_info.get('status')
        return -1

    def withdraw(self, token: str, amount: float, network: str, address: str) -> None:
        """
        Отправляет запрос на вывод токена с биржи
        :param token: название токена
        :param amount: сумма вывода
        :param network: название сети в соответствии с биржей
        :param address: адрес кошелька получателя
        :return: None
        """
        path = '/sapi/v1/capital/withdraw/apply'

        params = dict(
            coin=token,
            amount=amount,
            network=network,
            address=address,
        )
        self.sign_params(params)

        url = self.endpoint + path
        response = requests.post(url, proxies=self.proxies, params=params, headers=self.headers)
        try:
            response.raise_for_status()
            withdraw_id = response.json().get('id')
            for _ in range(60):
                status = self.get_status_withdraw(withdraw_id)
                if status == 6:
                    print('Withdraw success')
                    return
                time.sleep(5)
            else:
                print('Withdraw fail')
        except Exception as ex:
            print(ex)
            print(response.json())

def main():
    with open('wallets.txt') as f:
        wallets = f.read().splitlines()

    binance = BinanceClient()

    random.shuffle(wallets)

    for wallet in wallets:
        amount = round(random.uniform(0.01, 0.1), 3)
        binance.withdraw('ETH', amount, 'Arbitrum', wallet)
        print(f'Пополнение кошелька {wallet} на {amount} ETH')
        time.sleep(random.randint(60, 1200))

"""
Задание 3 - hard

Напишите скрипт, который берет кошельки из файла wallets.txt и с рандомной паузой 
пополняет на 10-30$ в нативном токене одну из сетей: Binance Smart Chain, Ethereum, Polygon, Arbitrum,
Optimism, Avalanche. Цену нужно получить с бинанса.
Кошельки должны пополниться по 1 разу за день, но в рандомном порядке.
Пауза между ними должна высчитываться из учета количества кошельков, чтобы они пополнялись
равномерно в течении дня, но с рандомными интервалами.
Можете использовать любой способ работы с api: запросы, SDK, ccxt.

"""


class BinanceClient:

    def __init__(self):
        self.endpoint = 'https://api.binance.com'
        self.proxies = {
            'http': config.PROXY.get_secret_value(),
            'https': config.PROXY.get_secret_value()
        }
        self.headers = {
            'X-MBX-APIKEY': config.BINANCE_API_KEY.get_secret_value()
        }

    def sign_params(self, params: dict):
        """
        Подписывает запрос к binance в исходном словаре
        :param params: словарь параметров
        :return: None
        """
        params['timestamp'] = int(time.time() * 1000)

        payload = '&'.join(f'{param}={value}' for param, value in params.items())

        signature = hmac.new(
            config.BINANCE_SECRET_KEY.get_secret_value().encode('utf-8'),
            payload.encode('utf-8'), hashlib.sha256).hexdigest()

        params['signature'] = signature

    def get_info(self) -> list[dict]:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        path = '/sapi/v1/capital/config/getall'
        params = dict()
        self.sign_params(params)
        url = self.endpoint + path
        response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
        data = response.json()
        pprint(data)
        return data

    def get_status_withdraw(self, withdraw_id: str):
        path = '/sapi/v1/capital/withdraw/history'
        params = dict()
        self.sign_params(params)
        url = self.endpoint + path
        response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
        withdraws = response.json()
        for withdraw_info in withdraws:
            if withdraw_info.get('id') == withdraw_id:
                return withdraw_info.get('status')
        return -1

    def get_price(self, token: str) -> float:
        """
        Получает цену токена на бирже
        :param token: название токена
        :return: цена токена
        """
        path = '/api/v3/trades'
        params = dict(symbol=token + 'USDT', limit=1)
        url = self.endpoint + path
        response = requests.get(url, params=params, headers=self.headers, proxies=self.proxies)
        data = response.json()
        return float(data[0]['price'])

    def withdraw(self, token: str, amount: float, network: str, address: str) -> None:
        """
        Отправляет запрос на вывод токена с биржи
        :param token: название токена
        :param amount: сумма вывода
        :param network: название сети в соответствии с биржей
        :param address: адрес кошелька получателя
        :return: None
        """
        path = '/sapi/v1/capital/withdraw/apply'

        params = dict(
            coin=token,
            amount=amount,
            network=network,
            address=address,
        )
        self.sign_params(params)

        url = self.endpoint + path
        response = requests.post(url, proxies=self.proxies, params=params, headers=self.headers)
        try:
            response.raise_for_status()
            withdraw_id = response.json().get('id')
            for _ in range(60):
                status = self.get_status_withdraw(withdraw_id)
                if status == 6:
                    print('Withdraw success')
                    return
                time.sleep(5)
            else:
                print('Withdraw fail')
        except Exception as ex:
            print(ex)
            print(response.json())

def main():
    with open('wallets.txt') as f:
        wallets = f.read().splitlines()

    binance = BinanceClient()
    token_chains = {
        'BSC': 'BNB',
        'ETH': 'ETH',
        'MATIC': 'MATIC',
        'ARBITRUM': 'ETH',
        'OPTIMISM': 'ETH',
        'AVAX': 'AVAX'
    }
    token_prices = {}



    while True:
        random.shuffle(wallets)
        length = len(wallets)
        delay = 24 * 60 * 60 / length
        for wallet in wallets:
            # выбираем случайную сеть и токен
            chain = random.choice(list(token_chains.keys()))
            token = token_chains[chain]
            # сумма в $ от 10 до 30
            amount_in_usd = round(random.uniform(10, 30), 2)
            # получаем цену токена

            # ленивая проверка на наличие цены в кеше
            token_price = token_prices.get(token)
            if not token_price:
                token_price = binance.get_price(token)
                token_prices[token] = token_price

            amount = round(amount_in_usd / token_price, 3)
            binance.withdraw(token, amount, chain, wallet)
            print(f'Пополнение кошелька {wallet} на {amount} USDT')
            time.sleep(delay + random.randint(-300, 300))



