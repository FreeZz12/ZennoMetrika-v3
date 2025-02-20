""""""

"""
Задание 1 - easy

Напишите самостоятельно функцию send_token(amount: float, to_address:str, token: str | None = None) -> str, 
которая принимает:
- amount: float - количество токенов для отправки
- to_address: str - адрес получателя
- token: str | None - адрес контракта токена, по умолчанию None

Функция должна отправлять токены на адрес to_address.
Если не передан адрес контракта токена, то отправляются нативные токены.
Если передан адрес контракта токена, то отправляются токены этого контракта с учетом decimals.

"""
from web3 import Web3


def prepare_native_tx_params(from_address: str, to_address: str, amount_wei: int, w3: Web3) -> dict:
    return {
        'nonce': w3.eth.get_transaction_count(from_address),
        'from': from_address,
        'to': to_address,
        'value': amount_wei,
        'chainId': w3.eth.chain_id,
    }


def prepare_erc20_tx_params(from_address: str, to_address: str, amount: float, w3: Web3,
                            token_contract_address: str) -> dict:
    token_contract_address = w3.to_checksum_address(token_contract_address)
    to_address = w3.to_checksum_address(to_address)
    abi = [{
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }, ]
    contract = w3.eth.contract(address=token_contract_address, abi=abi)
    decimals = contract.functions.decimals().call()
    amount_wei = int(amount * 10 ** decimals)
    tx_params = {
        'nonce': w3.eth.get_transaction_count(from_address),
        'from': from_address,
        'chainId': w3.eth.chain_id,
    }
    tx_params = contract.functions.transfer(to_address, amount_wei).build_transaction(tx_params)
    return tx_params


def get_fee(tx_params: dict, w3: Web3) -> dict:
    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    return tx_params


def send_token(amount: float, to_address: str, w3: Web3, token: str | None = None) -> str:
    from_address = w3.eth.account.from_key('private_key').address
    to_address = w3.to_checksum_address(to_address)

    if token is None:
        amount_wei = int(amount * 10 ** 18)
        tx_params = prepare_native_tx_params(from_address, to_address, amount_wei, w3)
    else:
        tx_params = prepare_erc20_tx_params(from_address, to_address, amount, w3, token)

    tx_params = get_fee(tx_params, w3)

    if tx_params.get('gas') is None:
        tx_params['gas'] = w3.eth.estimate_gas(tx_params)

    signed_tx = w3.eth.account.sign_transaction(tx_params, 'private_key')
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()


# код пишем тут


"""
Задание 2  - medium

Напишите скрипт, который берет из текстового файла private_keys.txt приватные ключи адресов.
Скрипт должен в сети арбитрум проверить наличие баланса токена USDT, если баланс больше 1$,
то вывести на указанный адрес.

"""


def get_balance(address: str, w3: Web3, token: str | None = None) -> int:
    if token is None:
        return w3.eth.get_balance(address) / 10 ** 18

    token_contract_address = w3.to_checksum_address(token)
    abi = [{
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }]
    contract = w3.eth.contract(address=token_contract_address, abi=abi)
    decimals = contract.functions.decimals().call()
    return contract.functions.balanceOf(address).call() / 10 ** decimals


w3 = Web3(Web3.HTTPProvider('url rpc'))
with open('private_keys.txt') as f:
    private_keys = f.read().splitlines()

target_address = '0xAddress'

for private_key in private_keys:
    address = w3.eth.account.from_key(private_key).address
    usdt_balance = get_balance(address, w3, '0xUSDTContractAdressInArbitrum')
    if usdt_balance > 1:
        send_token(usdt_balance, target_address, w3, '0xUSDTContractAdressInArbitrum')

"""
Задание 3  - hard

Напишите сборщик токенов, который будет собирать токены на адреса суб аккаунтов биржи.
Напишите скрипт, который:
- берет из текстового файла private_keys.txt приватные ключи адресов.
- берет из текстового файла sub_addresses.txt адреса суб аккаунтов биржи.
Должно быть соответствие 1 к 1 между приватным ключом и адресом суб аккаунта.

Скрипт должен по очереди брать приватный ключ и:
- извлекать адрес 
- проверять баланс USDT и USDC в сети Arbitrum, Optimism
- если какой-то из балансов больше 1$, то запускаем вывод на адрес суб аккаунта биржи
- если на кошельке недостаточно нативного токена для вывода, то выводим с биржи нативку 
(можно сделать псевдо функцию withdraw)
- после выводов стейблкоинов, скрипт должен отправить на адрес суб аккаунта биржи 
нативные токены, не забудьте оставить нативку на комиссию

Результат работы скрипта, со всех адресов должны быть выведены все стейблкоины и нативные токены в двух сетях.


Попробуйте реализовать на классах Onchain, Chain, Chains, Token, Tokens для удобства работы.
"""

import json


class Chain:
    def __init__(self, name: str, rpc: str, native_token: str, multiplier: float = 1.0):
        self.name = name
        self.rpc = rpc
        self.native_token = native_token
        self.multiplier = multiplier


class Chains:
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH')
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH')


class Token:
    def __init__(self, name: str, address: str, decimals: int, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.decimals = decimals
        self.chain = chain


class Tokens:
    USDT_OP = Token(
        'USDT',
        '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58',
        6,
        Chains.Optimism
    )
    USDC_OP = Token(
        'USDC',
        '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
        6,
        Chains.Optimism
    )
    USDT_ARBITRUM = Token(
        'USDT',
        '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9',
        6,
        Chains.Arbitrum
    )
    USDC_ARBITRUM = Token(
        'USDC',
        '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8',
        6,
        Chains.Arbitrum
    )


class Onchain:

    def __init__(self, chain: Chain, private_key: str):
        self.chain = chain
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(chain.rpc))
        self.address = self.w3.eth.account.from_key(private_key).address

    def _get_abi(self, path: str):
        """
        Получение ABI из файла
        :param path: полный путь к файлу с указанием расширения файла
        :return: список словарей json пригодный для передачи в объект контракта
        """
        with open(path) as f:
            return json.loads(f.read())

    def _get_multiplier(self, min_mult: float = 1.03, max_mult: float = 1.1) -> float:
        """
        Генерация случайного множителя комиссии
        """
        return random.uniform(min_mult, max_mult)

    def get_fee(self, tx_params: dict) -> dict:
        """
        Получение комиссий для legacy и EIP-1559 транзакций, редактирует переданный словарь tx_params
        """
        fee_history = self.w3.eth.fee_history(20, 'latest', [20])

        if not any(fee_history.get('baseFeePerGas', [0])):
            tx_params['gasPrice'] = self.w3.eth.gas_price * self._get_multiplier() * self.chain.multiplier
            return tx_params

        base_fee = fee_history['baseFeePerGas'][-1]
        priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
        max_priority_fee = max(priority_fees) * self._get_multiplier() * self.chain.multiplier
        max_fee = (base_fee + max_priority_fee) * self._get_multiplier() * self.chain.multiplier

        tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
        tx_params['maxFeePerGas'] = int(max_fee)

        return tx_params

    def send_token(self, amount: float, to_address: str, token: Token | str | None = None) -> str:
        """
        Отправка любых токенов (ERC20 или нативного токена) на адрес to_address, если
        не указан token, то отправляется нативный токен сети.
        :param amount: сумма токенов в человеческом формате
        :param to_address: адрес получателя
        :param token:  объект Token или адрес контракта ERC20
        :return: hash транзакции в формате hex
        """

        to_address = self.w3.to_checksum_address(to_address)

        token_name = None

        if token is None:
            token_name = self.chain.native_token
            amount_wei = int(amount * 10 ** 18)
            tx_params = self._prepare_tx_params(to_address, amount_wei)
        else:
            if isinstance(token, Token):
                contract_address = token.address
                token_name = token.name
            else:
                contract_address = token

            token_contract_address = self.w3.to_checksum_address(contract_address)
            abi = self._get_abi('erc20.json')
            contract = self.w3.eth.contract(address=token_contract_address, abi=abi)

            if isinstance(token, Token):
                decimals = token.decimals
            else:
                decimals = contract.functions.decimals().call()

            if token_name is None:
                token_name = contract.functions.symbol().call()

            amount_wei = int(amount * 10 ** decimals)
            tx_params = self._prepare_tx_params()
            tx_params = contract.functions.transfer(to_address, amount_wei).build_transaction(tx_params)

        # получаем историю комиссий
        tx_params = self.get_fee(tx_params)

        if tx_params.get('gas') is None:
            tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * self._get_multiplier())

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f'Транзакция {tx_hash.hex()} отправлена, в блокчейне {self.chain.name}, токен {token_name}')
        return tx_hash.hex()

    def _prepare_tx_params(self, to_address: str | None = None, value: int | None = None) -> dict:
        """
        Подготовка стандартных параметров транзакции, по необходимости добавляются to и value
        :param to_address: адрес получателя, в случае отправки нативного токена, при работе с ERC20 - None
        :param value: сумма нативных токенов в wei, в случае отправки нативного токена, при работе с ERC20 - None
        :return: словарь параметров транзакции
        """
        tx_params = {
            'chainId': self.w3.eth.chain_id,
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
        }

        if to_address:
            tx_params['to'] = self.w3.to_checksum_address(to_address)
        if value:
            tx_params['value'] = value

        return tx_params

    def get_balance(self, token: Token | None = None) -> float:

        if token is None:
            return self.w3.eth.get_balance(self.address) / 10 ** 18


        with open('erc20.json') as file:
            abi = json.loads(file.read())

        contract = w3.eth.contract(address=token.address, abi=abi)

        balance = contract.functions.balanceOf(address).call()
        decimals = contract.functions.decimals.call()

        return balance / 10 ** decimals

def withdraw():
    pass

def main():
    chains = [Chains.Arbitrum, Chains.Optimism]
    tokens = [Tokens.USDT_OP, Tokens.USDC_OP, Tokens.USDT_ARBITRUM, Tokens.USDC_ARBITRUM]
    with open('private_keys.txt') as f:
        private_keys = f.read().splitlines()

    with open('sub_addresses.txt') as f:
        sub_addresses = f.read().splitlines()

    MIN_NATIVE_BALANCE = 0.0001
    MIN_STABLE_BALANCE = 1

    for chain in chains:
        for private_key, sub_address in zip(private_keys, sub_addresses):
            onchain = Onchain(chain, private_key)

            for token in tokens:
                if token.chain.name != chain.name:
                    continue
                stable_balance = onchain.get_balance(token)
                if stable_balance < MIN_STABLE_BALANCE:
                    continue
                if onchain.get_balance() < MIN_NATIVE_BALANCE:
                    withdraw() # псевдо функция вывода с биржи
                onchain.send_token(stable_balance, sub_address, token)

            native_balance = onchain.get_balance()
            if native_balance < MIN_NATIVE_BALANCE:
                continue
            amount = native_balance - MIN_NATIVE_BALANCE
            onchain.send_token(amount, sub_address)



