import time
from pprint import pprint
from datetime import datetime
from dataclasses import dataclass
import requests
from eth_abi import decode
import config as config


url = 'https://api.etherscan.io/v2/api'

event = 'Permit(address,address,address,uint160,uint48,uint48)'
from eth_utils.crypto import keccak
print(keccak(text=event).hex())



def get_block_by_timestamp(timestamp: int, chainid: int) -> str:
    """
    Возвращает номер блока по timestamp метке в указанном блокчейне
    Args:
        timestamp: int - timestamp метка
        chainid: int - id блокчейна
    Returns:
        str - номер блока
    """

    params = {
        'chainid': chainid,
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': timestamp,
        'closest': 'before',
        'apikey': config.config.ETHERSCAN_API_KEY,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()['result']


def get_balance(address: str, chainid: int) -> float:
    """
    Возвращает баланс указанного адреса в указанном блокчейне
    Args:
        address: str - адрес
        chainid: int - id блокчейна
    Returns:
        str - баланс
    """

    params = {
        'chainid': chainid,
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': config.ETHERSCAN_API_KEY,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return int(r.json()['result']) / 1e18


def get_balances(addresses: list[str], chainid: int) -> dict[str, float]:
    """
    Возвращает балансы указанных адресов в указанном блокчейне
    Args:
        addresses: list[str] - список адресов
        chainid: int - id блокчейна
    Returns:
        dict[str, float] - словарь с балансами, где ключ - адрес, значение - баланс
    """
    str_addresses = ','.join(addresses)
    params = {
        'chainid': chainid,
        'module': 'account',
        'action': 'balancemulti',
        'address': str_addresses,
        'tag': 'latest',
        'apikey': config.ETHERSCAN_API_KEY,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    balances = {}
    for balance_info in r.json()['result']:
        address = balance_info['account']
        balance = balance_info['balance']
        balances[address] = int(balance) / 1e18
    return balances


def get_transactions(address: str, chainid: int, startblock: str, endblock: str = 'latest') -> list[dict]:
    """
    Возвращает список транзакций указанного адреса в указанном блокчейне
    Args:
        address: str - адрес
        chainid: int - id блокчейна
        from_block: str - номер блока начала
        to_block: str - номер блока конца
    Returns:
        list[dict] - список транзакций
    """
    all_txs = []
    while True:
        params = {
            'chainid': chainid,
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': startblock,
            'endblock': endblock,
            'apikey': config.ETHERSCAN_API_KEY,
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        txs = r.json()['result']

        if not txs:
            return all_txs

        current_len = len(txs)

        if current_len == 10000:
            deleted_number_block = txs[-1]['blockNumber']
            for i in range(len(txs) - 1, -1, -1):
                if txs[i]['blockNumber'] != deleted_number_block:
                    txs = txs[:i + 1]
                    break
            startblock = int(txs[-1]['blockNumber']) + 1

        all_txs.extend(txs)

        print(len(all_txs))

        if current_len < 10000:
            return all_txs


def get_uniswap_stats(txs: list[dict]) -> dict:

    commands_stats = {}
    for tx in txs:
        if tx['methodId'] != '0x3593564c':
            continue
        calldata = bytes.fromhex(tx['input'][10:])
        commands, inputs, deadline = decode(['bytes', 'bytes[]', 'uint256'], calldata)
        commands = commands.hex()
        commands_stats[commands] = commands_stats.get(commands, 0) + 1
    commands_stats = sorted(commands_stats.items(), key=lambda x: x[1], reverse=True)
    print(*commands_stats, sep='\n')
    

def get_uniswap_tx_count(txs: list[dict]) -> int:
    result_txs =  [tx for tx in txs if tx['to'].lower() == '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD'.lower()]
    print(result_txs)
    timestamp = int(time.time()) - 60 * 60 * 24
    last_tx_timestamp = int(result_txs[-1]['timeStamp'])
    print(f'дата последней транзакции: {datetime.fromtimestamp(last_tx_timestamp)}')
 

    return len(result_txs)

def main():
    address = '0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7'
    addresses = ['0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7',
                 '0xAC8ce8fbC81115a22a9a69e42F50713AAe9ef2F7', '0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F8']
    timestamp = int(time.time()) - 60 * 60 * 10
    chainid = 1

    block = get_block_by_timestamp(timestamp, chainid)
    print(block)

    # balance = get_balance(address, chainid)
    # print(balance)

    # balances = get_balances(addresses, chainid)
    # print(balances)

    # contract_address = '0x66a9893cc07d91d95644aedd05d03f95e1dba8af'
    # transactions = get_transactions(contract_address, chainid, block)

    # print(len(transactions))
    # get_uniswap_stats(transactions)
    
    transactions = get_transactions(address, chainid, 0)
    
    print(get_uniswap_tx_count(transactions))


if __name__ == '__main__':
    main()

