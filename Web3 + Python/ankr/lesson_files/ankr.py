# %% импорты и настройка
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from config import settings
from web3 import Web3


# %% использования как rpc
w3 = Web3(Web3.HTTPProvider(
    f'https://rpc.ankr.com/eth/{settings.ankr_api_key}'))
print(w3.is_connected())


# %% запрос логов


url = 'https://rpc.ankr.com/multichain/'
timestamp = int((datetime.now() - timedelta(days=1000)).timestamp())
all_logs = []

body = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "ankr_getLogs",
    "params": {
        "blockchain": ['eth'],
        "address": ["0xdAC17F958D2ee523a2206206994597C13D831ec7", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"],
        "decodeLogs": True,
        "topics": [
            '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925',
            '0x' + 'AC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7'.zfill(64)
        ],
        'pageSize': 100,
        'fromTimestamp': timestamp
    }
}
headers = {
    'Content-Type': 'application/json',
}

response = requests.post(url + settings.ankr_api_key,
                         json=body, headers=headers)

all_logs = response.json()['result']['logs']
print(json.dumps(response.json(), indent=4))
print(len(response.json()['result']['logs']))
# %% Запрос нескольких страниц логов

while 'nextPageToken' in response.json()['result']:
    body['params']['pageToken'] = response.json()['result']['nextPageToken']
    response = requests.post(url + settings.ankr_api_key,
                             json=body, headers=headers)
    data = response.json()
    all_logs.extend(data['result']['logs'])
    print(len(all_logs))

# %% Запрос транзакций

body = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "ankr_getTransactionsByAddress",
    "params": {
        "blockchain": ['eth', 'arbitrum', 'base', 'optimism', 'polygon'],
        "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "includeLogs": True,
        "fromTimestamp": timestamp
    }
}


response = requests.post(url + settings.ankr_api_key,
                         json=body, headers=headers)
data = response.json().get('result', {}).get('transactions', [])

df = pd.DataFrame(data)
# %% Запрос балансов токенов

body = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "ankr_getAccountBalance",
    "params": {
        "blockchain": ['eth', 'arbitrum', 'base', 'optimism', 'polygon'],
        "onlyWhitelisted": True,
        "walletAddress": "0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7"
    }
}

response = requests.post(url + settings.ankr_api_key,
                         json=body, headers=headers)
data = response.json().get('result', {})
print(json.dumps(response.json(), indent=4))
