from __future__ import annotations

import base64
from datetime import datetime, UTC
import hashlib
import hmac
import json
import time
from pprint import pprint

from config.settings import config
from config.chains import Chains

from binance.spot import Spot
from okx.Funding import FundingAPI
from okx.Account import AccountAPI
from okx.SubAccount import SubAccountAPI
import requests
import ccxt


class BinanceCcxtClient:

    def __init__(self):
        self.client = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY.get_secret_value(),
            'secret': config.BINANCE_SECRET_KEY.get_secret_value(),
            'proxies': {
                'https': config.PROXY.get_secret_value()
            },
            'options': {
                'defaultType': 'spot',  # spot, margin, future, delivery
            },

        })

    def get_info(self) -> dict:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        tokens_info = self.client.fetch_currencies()
        pprint(tokens_info)
        return tokens_info

    def get_status_withdraw(self, withdraw_id: str) -> str:
        withdraw_history = self.client.fetch_withdrawals()
        for transaction in withdraw_history:
            if transaction.get('id') == withdraw_id:
                return transaction.get('status')
        return 'error'

    def withdraw(self, token: str, amount: float, network: str, address: str) -> None:

        try:
            response = self.client.withdraw(
                code=token,
                amount=amount,
                address=address,
                params={'network': network}
            )
            withdraw_id = response.get('id')
            for _ in range(60):
                status = self.get_status_withdraw(withdraw_id)
                if status == 'ok':
                    print('Withdraw success')
                    return
                time.sleep(5)
            else:
                print('Withdraw fail')
        except Exception as ex:
            print(ex)


class BinanceSdkClient:

    def __init__(self):
        self.client = Spot(
            config.BINANCE_API_KEY.get_secret_value(),
            config.BINANCE_SECRET_KEY.get_secret_value(),
            proxies={'https': config.PROXY.get_secret_value()}
            # proxies={'https': 'http://user:pass@ip:port'}
        )

    def get_info(self) -> list[dict]:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        tokens_info = self.client.coin_info()
        pprint(tokens_info)
        return tokens_info

    def get_status_withdraw(self, withdraw_id: str) -> int:

        withdraw_history = self.client.withdraw_history()
        for withdraw_info in withdraw_history:
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

        try:
            response = self.client.withdraw(
                coin=token,
                amount=amount,
                network=network,
                address=address
            )
            withdraw_id = response.get('id')
            for _ in range(60):
                status = self.get_status_withdraw(withdraw_id)
                if status == 4:
                    print('Withdraw success')
                    return
                time.sleep(5)
            else:
                print('Withdraw fail')
        except Exception as ex:
            print(ex)


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


class OkxClient:

    def __init__(self):
        self.endpoint = 'https://www.okx.com'
        self.proxies = {
            'http': config.PROXY.get_secret_value(), # 'http://user:pass@ip:port'
            'https': config.PROXY.get_secret_value() # 'http://user:pass@ip:port'
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
        path = '/api/v5/account/balance' # trading
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


class OkxSdkClient:

    def __init__(self):
        kwargs = {
            'api_key': config.OKX_API_KEY.get_secret_value(),
            'api_secret_key': config.OKX_SECRET_KEY.get_secret_value(),
            'passphrase': config.OKX_PASSPHRASE.get_secret_value(),
            'proxy': config.PROXY.get_secret_value(),
            'debug': False,
            'flag': '0'
        }

        self.trading = AccountAPI(**kwargs)
        self.funding = FundingAPI(**kwargs)
        self.sub_account = SubAccountAPI(**kwargs)

    def get_info(self) -> list[dict]:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        data = self.funding.get_currencies()
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
        chain_with_network = f'{token}-{network}'
        data = self.funding.withdrawal(
            ccy=token,
            amt=amount,
            dest=4,
            toAddr=address,
            chain=chain_with_network
        )
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
        data = self.sub_account.get_subaccount_list()
        sub_names = [sub.get('subAcct') for sub in data.get('data', [])]
        return sub_names

    def get_sub_acc_trading_balance(self, sub_acc_id: str) -> list[dict]:
        """
        Получает информацию о балансе торгового счета субаккаунта
        :param sub_acc_id: идентификатор субаккаунта
        :return: список словарей с информацией о балансе
        """
        data = self.sub_account.get_account_balance(sub_acc_id)
        return data.get('data', [{}])[0].get('details', [{}])

    def get_sub_acc_funding_balance(self, sub_acc_id: str) -> list[dict]:
        """
        Получает информацию о балансе торгового счета субаккаунта
        :param sub_acc_id: идентификатор субаккаунта
        :return: список словарей с информацией о балансе
        """
        data = self.sub_account.get_funding_balance(sub_acc_id)
        return data.get('data', [])

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
                    self.funding.funds_transfer(
                        type=2,
                        ccy=balance.get('ccy'),
                        amt=balance.get('availBal'),
                        from_=type_id,
                        to=6,
                        subAcct=sub_name
                    )

    def get_balance_funding(self) -> list[dict]:
        """
        Получает информацию о балансе финансового счета
        :return:  список словарей с информацией о балансе
        """
        data = self.funding.get_balances()
        return data.get('data', [])

    def get_balance_trading(self) -> list[dict]:
        """
        Получает информацию о балансе торгового счета
        :return:  список словарей с информацией о балансе
        """

        data = self.trading.get_account_balance()
        return data.get('data', [{}])[0].get('details', [{}])

    def transfer_trading_to_funding(self):
        """
        Переводит средства с торгового счета на финансовый
        :return: None
        """
        trading_balances = self.get_balance_trading()
        for balance_data in trading_balances:
            balance = float(balance_data.get('availBal', 0))
            if balance <= 0:
                continue
            self.funding.funds_transfer(
                type=0,
                ccy=balance_data.get('ccy'),
                amt=balance_data.get('availBal'),
                from_=18,
                to=6
            )

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
        data = self.funding.get_withdrawal_history(wdId=withdraw_id)
        status = data.get('data', [{}])[0].get('state', -4)
        return status


class OkxCcxtClient:

    def __init__(self):
        kwargs = {
            'apiKey': config.OKX_API_KEY.get_secret_value(),
            'secret': config.OKX_SECRET_KEY.get_secret_value(),
            'password': config.OKX_PASSPHRASE.get_secret_value(),
            'proxies': {
                'https': config.PROXY.get_secret_value()
            },
        }

        self.client = ccxt.okx(kwargs)

    def get_info(self) -> dict:
        """
        Получает информацию о токенах и сетях
        :return: список словарей с информацией о токенах и сетях
        """
        data = self.client.fetch_currencies()
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
        chain_with_network = f'{token}-{network}'
        data = self.client.withdraw(
            code=token,
            amount=amount,
            address=address,
            params={'chain': chain_with_network, 'dest': 4}
        )
        withdraw_id = data.get('id')
        for _ in range(60):
            status = self.get_withdraw_status(withdraw_id)
            if str(status) == "ok":
                print('Withdraw success')
                return
            time.sleep(5)

    def get_sub_accs(self) -> list[dict]:
        """
        Получает информацию о субаккаунтах
        :return: список словарей с информацией о субаккаунтах
        """
        data = self.client.private_get_users_subaccount_list()
        sub_names = [sub.get('subAcct') for sub in data.get('data', [])]
        return sub_names

    def get_sub_acc_trading_balance(self, sub_acc_id: str) -> list[dict]:
        """
        Получает информацию о балансе торгового счета субаккаунта
        :param sub_acc_id: идентификатор субаккаунта
        :return: список словарей с информацией о балансе
        """
        data = self.client.private_get_account_subaccount_balances(params={'subAcct': sub_acc_id})
        return data.get('data', [{}])[0].get('details', [{}])

    def get_sub_acc_funding_balance(self, sub_acc_id: str) -> list[dict]:
        """
        Получает информацию о балансе торгового счета субаккаунта
        :param sub_acc_id: идентификатор субаккаунта
        :return: список словарей с информацией о балансе
        """
        data = self.client.private_get_asset_subaccount_balances(params={'subAcct': sub_acc_id})
        return data.get('data', [])

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
                    self.client.transfer(
                        code=balance.get('ccy'),
                        amount=balance.get('availBal'),
                        fromAccount=str(type_id),
                        toAccount='6',
                        params={'subAcct': sub_name, 'type': '2'}
                    )

    def get_balance_funding(self) -> list[dict]:
        """
        Получает информацию о балансе финансового счета
        :return:  список словарей с информацией о балансе
        """
        data = self.client.private_get_asset_balances()
        return data.get('data', [])

    def get_balance_trading(self) -> list[dict]:
        """
        Получает информацию о балансе торгового счета
        :return:  список словарей с информацией о балансе
        """
        data = self.client.private_get_account_balance()
        return data.get('data', [{}])[0].get('details', [{}])

    def transfer_trading_to_funding(self):
        """
        Переводит средства с торгового счета на финансовый
        :return: None
        """
        trading_balances = self.get_balance_trading()
        for balance_data in trading_balances:
            balance = float(balance_data.get('availBal', 0))
            if balance <= 0:
                continue

            self.client.transfer(
                code=balance_data.get('ccy'),
                amount=balance_data.get('availBal'),
                fromAccount='18',
                toAccount='6',
                params={'type': '0'}
            )

    def get_withdraw_status(self, withdraw_id: str) -> str:
        """
        Получает статус вывода.
        pending: ожидание вывода
        ok: успешно
        cancel: отменено
        not found: не найдено в истории выводов

        :param withdraw_id: идентификатор вывода
        :return: статус вывода
        """
        data = self.client.fetch_withdrawals(params={'wdId': withdraw_id})
        status = data[0].get('status', 'not found')
        return status


if __name__ == '__main__':
    okx = OkxClient()
    okx.get_info()
