# %% Импорты 
from time import time
import json

import requests
import pandas as pd

from config import config
from main import get_block_by_timestamp

# %% Получение блока по времени
timestamp = int(time() - 60 * 60 * 3)
block = get_block_by_timestamp(timestamp, 1)
print(f'{block = }')

# %% Получение логов

def get_logs(address: str, from_block: str, chainid: int) -> list[dict]:
    url = 'https://api.etherscan.io/v2/api'
    all_logs = []
    
    while True:
        params = {
            'chainid': chainid,
            'module': 'logs',
            'action': 'getLogs',
            'address': address,
            'fromBlock': from_block,
            'toBlock': 'latest',
            'apikey': config.ETHERSCAN_API_KEY
        }

        response = requests.get(url, params=params)
        logs = response.json()['result']
        
        if not logs:
            return all_logs
            
        current_len = len(logs)
        
        if current_len == 1000:
            deleted_block = int(logs[-1]['blockNumber'], 16)
            for i in range(len(logs) - 1, -1, -1):
                if int(logs[i]['blockNumber'], 16) != deleted_block:
                    logs = logs[:i + 1]
                    break
            from_block = int(logs[-1]['blockNumber'], 16) + 1
            
        all_logs.extend(logs)
        print(f'{len(all_logs) = }')
        
        if current_len < 1000:
            return all_logs

address = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
logs = get_logs(address, block, 1)
print(json.dumps(logs, indent=4))

# %% создание датафрейма
logs_df = pd.DataFrame(logs)
logs_df.head()

# %% весь датафрейм
logs_df

# %% сохранение в excel
logs_df.to_excel('logs.xlsx', index=False)

# %% добавление столбца с селектором события
def get_selector(topics: list[str]) -> str:
    return topics[0]

logs_df['selector'] = logs_df['topics'].apply(get_selector)
logs_df

# %% Фильтруем события по селектору апрув
approve_logs_df = logs_df[logs_df['selector'] == '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']
approve_logs_df.to_excel('апрувы.xlsx', index=False)

# %% Фильтруем события по селектору трансфер
transfer_logs_df = logs_df[logs_df['selector'] == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']
transfer_logs_df

# %% добавляем столбец сумма перевода
def get_amount(data: str) -> float:
    return int(data, 16) / 10 ** 6

transfer_logs_df['amount'] = transfer_logs_df['data'].apply(get_amount)
transfer_logs_df

# %% сумма переводов
transfer_logs_df['amount'].sum()

### Получение апрувов
# %% Получение апрувов всех токенов по топику

def get_logs_by_topic(topic: str, from_block: str, chainid: int) -> list[dict]:
    url = 'https://api.etherscan.io/v2/api'
    params = {
        'chainid': chainid,
        'module': 'logs',
        'action': 'getLogs',
        'fromBlock': from_block,
        'toBlock': 'latest',
        'topic0': topic,
        'apikey': config.ETHERSCAN_API_KEY
    }

    response = requests.get(url, params=params)
    return response.json()['result']

approve_selector = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'

all_approve_logs = get_logs_by_topic(approve_selector, block, 1)
all_approve_df = pd.DataFrame(all_approve_logs)
all_approve_df


# %% получение апрувов всех токенов для конкретного адреса

def get_logs_by_topics(topics: dict[str, str], from_block: str, chainid: int) -> pd.DataFrame:
    url = 'https://api.etherscan.io/v2/api'
    params = {
        'chainid': chainid,
        'module': 'logs',
        'action': 'getLogs',
        'fromBlock': from_block,
        'toBlock': 'latest',
        'apikey': config.ETHERSCAN_API_KEY
    }
    params.update(topics)

    response = requests.get(url, params=params)
    print(response.json())
    response.raise_for_status()
    return response.json()['result']

approve_selector = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'
owner = '0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7'[2:].zfill(64)
topics = {
    'topic0': approve_selector,
    'topic0_1_opr': 'and',
    'topic1': '0x' + owner,
}

approve_logs = get_logs_by_topics(topics, 0, 1)
approve_logs_df = pd.DataFrame(approve_logs)

# %% уникальные адреса токенов
tokens = approve_logs_df.address.unique()

# %% добавление столбца с адресом спендера
def get_spender(topics: list[str]) -> str:
    return '0x' + topics[2][-40:]

approve_logs_df['spender'] = approve_logs_df['topics'].apply(get_spender)

# %% проверка апрувов

from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://1rpc.io/eth'))
address = w3.to_checksum_address('0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7')

abi = [{
    'name': 'allowance',
    'inputs': [
        {'name': 'owner', 'type': 'address'},
        {'name': 'spender', 'type': 'address'},
    ],
    'outputs': [
        {'name': 'allowance', 'type': 'uint256'},
    ],
    'stateMutability': 'view',
    'type': 'function',
},
{
    'name': 'symbol',
    'inputs': [],
    'outputs': [{'name': 'symbol', 'type': 'string'}],
    'stateMutability': 'view',
    'type': 'function',
}]

token_approvals = []

for token in tokens:
    spenders = approve_logs_df[approve_logs_df['address'] == token]['spender'].unique()
    for spender in spenders:
        spender = w3.to_checksum_address(spender)
        token = w3.to_checksum_address(token)
        contract = w3.eth.contract(address=token, abi=abi)
        token_name = contract.functions.symbol().call()
        allowance = contract.functions.allowance(address, spender).call()
        token_approvals.append({
            'token': token_name,
            'token_address': token,
            'spender': spender,
            'allowance': allowance,
        })
        

token_approvals_df = pd.DataFrame(token_approvals)


# %%
