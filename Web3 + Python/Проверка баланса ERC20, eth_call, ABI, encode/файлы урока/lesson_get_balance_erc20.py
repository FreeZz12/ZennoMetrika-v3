# запрос баланса ERC20 токена
# как делать запрос к контракту
# формирование запроса
# через requests.post запрос
# через библиотеку web3
# отправка сырого запроса через eth_call
# кодирование данных для запроса в ABI, 3 способа
# ABI, правила, типы данных
# получение ABI контрактов
# создание объекта контракта
# функции контракта web3py
# запрос баланса ERC20 токена
# запрос decimal, symbol, name токена
# реализация get_balance

import os
from dotenv import load_dotenv

from main import Amount

load_dotenv()

from eth_typing import HexStr
from web3.types import TxParams


class Blockchain:
    accounts = {
        '0x00...01': {  # * EOA (обычный кошелёк) 	Externally Owned Account
            'balance': 1000000000000000000,  # * нативный баланс в Wei
            'nonce': 0,  # * количество транзакций отправленных с адреса
        },
        '0x00...02': {  # * контракт (адрес контракта) Contract Account
            'balance': 1000000000000000000,  # * нативный баланс в Wei
            'nonce': 0,  # * количество транзакций отправленных с адреса
            'code': '0x00...00',  # * байт-код контракта
            'storage': {  # * хранилище контракта
                '_balanceOf': {'address': 1000000000000000000},  # * ключ: значение
                'decimals': 6,  # * ключ: значение
                # ...
            },
            'storageRoot': '0x00...00',  # * хэш хранилища
            'codeHash': '0x00...00',  # * хэш байт-кода
        },
        '0x00...03': {},
    }


import requests
from web3 import Web3


def get_erc20_balance_request(contract_address: str, user_address: str) -> int:
    function_signature = '0x70a08231'
    address_data = user_address[2:].rjust(64, '0')
    data = function_signature + address_data  # contract.balanceOf(user_address)
    url = 'https://1rpc.io/op'
    body = {
        'id': 1,
        'jsonrpc': '2.0',
        'method': 'eth_call',
        'params': [{
            'to': contract_address,
            'data': data
        }, 'latest']
    }
    response = requests.post(url, json=body)
    return int(response.json()['result'], 16) / 10 ** 6


from eth_abi import encode


def get_erc20_balance_web3_1():
    contract_address = '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85'  # USDC OP
    user_address = '0x624c222fed7f88500afa5021cc760b3106fe34be'  # my address

    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/op'))

    # function_signature = '0x70a08231'
    function_signature = w3.keccak(text='balanceOf(address)').hex()[:8]
    # address_data = user_address[2:].rjust(64, '0')

    address_data = encode(['address'], [user_address]).hex()
    # print(encode(['address'], [user_address]).hex())
    # print(encode(['uint256'], [777]).hex())
    # print(encode(['bool'], [True]).hex())

    # print(address_data)
    """
    - сначала сигнатура функции 8 знаков
    - потом передаваемые аргументы функции (64 знака)
    - статичные типы данных и динамичные типы данных
    - пустота заполняется нулями
    - порядок важен
    """

    data = function_signature + address_data  # contract.balanceOf(user_address)
    params = {
        'to': contract_address,
        'data': data
    }
    result = w3.eth.call(params)
    print(result.hex())


def get_erc20_balance_web3_2(contract_address: str, user_address: str) -> int:
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/op'))

    function_signature = w3.keccak(text='balanceOf(address)').hex()[:8]
    address_data = encode(['address'], [user_address]).hex()
    params = {
        'to': contract_address,
        'data': function_signature + address_data
    }
    result = w3.eth.call(params)
    return int(result.hex(), 16)


import json


def get_abi(contract_address: str) -> list[dict]:
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
    url = 'https://api.etherscan.io/api'
    params = {
        'chain': 1,
        'module': 'contract',
        'action': 'getabi',
        'address': contract_address,
        'apikey': ETHERSCAN_API_KEY
    }
    response = requests.get(url, params=params)
    print(response.json())
    return json.loads(response.json()['result'])[0]



def get_erc20_balance_web3_3(contract_address: str, user_address: str) -> int:
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/op'))

    with open('erc20.json') as file:
        abi = json.loads(file.read())

    contract_address = w3.to_checksum_address(contract_address)
    user_address = w3.to_checksum_address(user_address)
    contract = w3.eth.contract(address=contract_address, abi=abi)
    # print(contract.all_functions())
    data = contract.encode_abi('balanceOf', [user_address])

    result = w3.eth.call({
        'to': contract_address,
        'data': data
    })

    return int(result.hex(), 16)


def get_erc20_balance_web3_4(contract_address: str, user_address: str) -> Amount:
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/op'))

    with open('erc20.json') as file:
        abi = json.loads(file.read())

    contract_address = w3.to_checksum_address(contract_address)
    user_address = w3.to_checksum_address(user_address)
    contract = w3.eth.contract(address=contract_address, abi=abi)
    # result = contract.functions.balanceOf(user_address).call()
    # result = contract.functions['balanceOf'](user_address).call()
    # balanceOf = contract.get_function_by_name('balanceOf')
    # print(balanceOf(user_address).call())

    balance = contract.functions.balanceOf(user_address).call()
    decimals = contract.functions.decimals.call()

    return Amount(balance, decimals, is_wei=True)


def get_balance(address: str, contract: str | None = None) -> Amount:
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/op'))

    address = w3.to_checksum_address(address)

    if not contract:
        return Amount(w3.eth.get_balance(address), is_wei=True)

    contract = w3.to_checksum_address(contract)

    with open('erc20.json') as file:
        abi = json.loads(file.read())

    contract = w3.eth.contract(address=contract, abi=abi)

    balance = contract.functions.balanceOf(address).call()
    decimals = contract.functions.decimals.call()

    return Amount(balance, decimals, is_wei=True)



usdc_op = '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85'  # USDC OP
address = '0x624c222fed7f88500afa5021cc760b3106fe34be'  # my address
print(get_balance(address, usdc_op).ether)
print(get_balance(address).ether)



"""
post https://sepolia.infura.io/v3/b6bf7d3508c941499b10025c0776eaf8


{
  "id": "737d33b9-c005-4eeb-8c4a-5122cb6326d7",
  "jsonrpc": "2.0",
  "method": "eth_call",
  "params": [
    {
      "to": "0x3aFa7A286bF61B9A59ce4A5ebc856F7333788B6d",
      "data": "function 70a08231
      address = 624c222fed7f88500afa5021cc760b3106fe34be" 
    },
    "0x7591b6"
  ]
}

response
{
  "jsonrpc": "2.0",
  "id": "737d33b9-c005-4eeb-8c4a-5122cb6326d7",
  "result": "0x00000000000000000000000000000000000000000000d38be6051f27c260000000000000000000000000000000000000000000000000d38be6051f27c260000000000000000000000000000000000000000000000000d38be6051f27c260000000000000000000000000000000000000000000000000d38be6051f27c260000000000000000000000000000000000000000000000000d38be6051f27c2600000"
}


"""


def main():
    pass


if __name__ == '__main__':
    main()
