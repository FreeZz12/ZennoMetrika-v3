import hashlib
import hmac
import time
from pprint import pprint

from config.settings import config
from config.chains import Chains

from binance.spot import Spot
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
    binance_sdk_client = BinanceCcxtClient()
    binance_sdk_client.withdraw('BNB', 0.001, Chains.BSC.okx_name, config.address)
    # binance_sdk_client.get_info()
    # binance_sdk_client.withdraw('BNB', 0.001, 'BSC', config.address)



if __name__ == '__main__':
    main()
