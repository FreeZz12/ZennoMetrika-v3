"""
API - как общаются роботы

REQUESTS - запросы, библиотека для отправки запросов
HEADERS - заголовки, метаданные
GET - запрос для получения данных
POST - запрос для отправки данных
RESPONSE - ответ на запрос
JSON - формат данных
URL - адрес сайта
PARAMS - параметры запроса
DATA - данные POST запроса
"""
import time

from better_proxy import Proxy

#          домен                   путь
debank_url = 'https://api.debank.com/chain/list'

debank_2 = 'https://api.debank.com/user/total_balance?addr=0xac8ce8fbc80115a22a9a69e42f50713aae9ef2f7'

etherscan = ('https://api.etherscan.io/v2/api'
             '?chainid=1'
             '&module=account'
             '&action=balance'
             '&address=0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae'
             '&tag=latest&'
             'apikey=R4P2M55NS69WWKBTADP1FQH6YIKTCCHI9D')

domain2 = 'https://192.168.0.1:50325/'
ads = 'http://local.adspower.com:50325'

import requests


#
# response = requests.get(url=debank_url)
# response = response.json()
# chains = response['data']['chains']
# for chain in chains:
#     print(chain['name'])


def get_request(url: str, params: dict = None, attempts: int = 3) -> dict:
    for _ in range(attempts):
        try:
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception:
            time.sleep(5)
    else:
        raise Exception('Не удалось получить данные')


ads_url = 'http://local.adspower.com:50325'
path = '/api/v1/browser/start'

params = dict(serial_number=949)
response = get_request(url=ads_url + path, params=params)



def get_balance(address: str) -> float:
        etherscan_url = 'https://api.etherscan.io/v2/api'
        params = dict(
            chainid=1,
            module='account',
            action='balance',
            address=address,
            tag='latest',
            apikey='R4P2M55NS69WWKBTADP1FQH6YIKTCCHI9D'
        )

        response = get_request(url=etherscan_url, params=params, attempts=5)
        return int(response['result']) / 10 ** 18




from fake_useragent import UserAgent
from better_proxy import Proxy

def check_ip() -> str:
    ua = UserAgent()
    ip_checker_url = 'https://api.ipify.org/'
    headers = {
        'User-Agent': ua.random,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive'}
    proxy = Proxy.from_str('http://siSyvDQu:eFaDTQaX@45.9.16.197:63888')
    response = requests.get(ip_checker_url, headers=headers, proxies=proxy.as_proxies_dict)
    return response.text





alchemy_api = 'https://base-mainnet.g.alchemy.com/v2'


payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "params": ["0xac8ce8fbc80115a22a9a69e42f50713aae9ef2f7", "latest"],
    "method": "eth_getBalance",
    'bearer': 'KywjZIUhfX3Y9P0JwQhmd_D8-fSfMET8'
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",

}

r = requests.post(alchemy_api, json=payload, headers=headers)
balance = int(r.json()['result'], 16) / 10 ** 18
print(balance)