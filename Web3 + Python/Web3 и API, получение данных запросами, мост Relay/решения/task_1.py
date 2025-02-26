"""
Задание 1 - medium

Напишите функцию:
bridge_relay(
    to_chain: Chain,
    amount: float,
    from_token: Token | None = None,
    to_token: Token | None = None
    ) -> str

Функция должна отправлять токены из сети указанной в объекте w3 в сеть to_chain.
Должна минимально работать в сети Arbitrum и Optimism с токенами ETH, USDT, USDC.

1. Если from_token и to_token не указаны, то отправляются и получаются нативные токены
2. Если from_token не указан, а to_token указан, то отправляются нативные токены,
а получаются токены указанные в to_token
3. Если from_token указан, а to_token не указан, то отправляются токены указанные в from_token,
а получаются нативные токены
4. Если from_token и to_token указаны указаны, то отправляются токены указанные в from_token,
а получаются токены указанные в to_token

Функция должна возвращать хеш транзакции.
Выясните как нужно изменить логику скрипта, чтобы можно было отправлять ERC20 токены через Bridge,
для этого изучите запросы на https://api.relay.link/quote, ответ от сервера и то что лежит в data, а так же
транзакцию в кошельке, которая отправляется если from_token это адрес ERC20 токен.

Используйте объекты Chain и Token для передачи параметров в функцию.

@dataclass
class Chain:
    name: str
    rpc: str
    native_token: str
    chain_id: int
    multiplier: int = 1


class Chains:
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH', 42161)
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH', 10)

@dataclass
class Token:
    name: str
    address: ChecksumAddress | str
    decimals: int
    chain: Chain

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)

class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6, Chains.Optimism)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6, Chains.Optimism)
    ETH_ARBITRUM = Token('ETH', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 18, Chains.Arbitrum)
    WETH_ARBITRUM = Token('WETH', '0x82af49447d8a07e3bd95bd0d56f35241523fbab1', 18, Chains.Arbitrum)
    USDT_ARBITRUM = Token('USDT', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', 6, Chains.Arbitrum)
    USDC_ARBITRUM = Token('USDC', '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', 6, Chains.Arbitrum)

!ПОДСКАЗКА!

Сравните транзакции, которые формируются в кошельке если исходящие токены разные USDT / USDC и т.д.
Обратите внимание на получателя токенов.
Обратите внимание на data в транзакции.
Обратите внимание на последний аргумент в data в транзакции.
Все данные можно получить из запроса к https://api.relay.link/quote.
Для нативного токена и для ERC20 токенов нужно отправить разные транзакции на разные адреса.

"""
import os
from dataclasses import dataclass

from eth_typing import ChecksumAddress
from web3 import Web3
import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Chain:
    name: str
    rpc: str
    native_token: str
    chain_id: int
    multiplier: float = 1

    def __hash__(self):
        return hash((self.name, self.rpc, self.native_token, self.chain_id, self.multiplier))


class Chains:
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH', 42161)
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH', 10)
    Base = Chain('Base', 'https://1rpc.io/base', 'ETH', 8453)
    Linea = Chain('Linea', 'https://1rpc.io/linea', 'ETH', 59144, 1.5)


@dataclass
class Token:
    name: str
    address: ChecksumAddress | str
    decimals: int
    chain: Chain

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)

    def __hash__(self):
        return hash((self.name, self.address, self.decimals, self.chain))


class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6, Chains.Optimism)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6, Chains.Optimism)
    USDT_ARBITRUM = Token('USDT', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', 6, Chains.Arbitrum)
    USDC_ARBITRUM = Token('USDC', '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', 6, Chains.Arbitrum)
    USDT_BASE = Token('USDT', '0xfde4c96c8593536e31f229ea8f37b2ada2699bb2', 6, Chains.Base)
    USDC_BASE = Token('USDC', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', 6, Chains.Base)
    USDT_LINEA = Token('USDT', '0xA219439258ca9da29E9Cc4cE5596924745e12B93', 6, Chains.Linea)
    USDC_LINEA = Token('USDC', '0x176211869cA2b568f2A7D4EE941E073a821EE1ff', 6, Chains.Linea)

    @classmethod
    def get_token_by_name(cls, name: str, chain: Chain) -> Token | None:
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.name == name and token.chain == chain:
                    return token
        return None


chain = Chains.Arbitrum
w3 = Web3(Web3.HTTPProvider(chain.rpc))
private_key = os.getenv('PK')
address = w3.eth.account.from_key(private_key).address


def get_fee(tx_params: dict, w3: Web3) -> dict:
    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    return tx_params


def relay_request_api(to_chain: Chain, amount: float, from_token: Token, to_token: Token) -> dict:
    """
    Делает запрос к API relay.link для получения информации о транзакции
    """
    url = 'https://api.relay.link/quote'
    body = {
        "user": address,
        "originChainId": w3.eth.chain_id,
        "destinationChainId": to_chain.chain_id,
        "originCurrency": from_token.address,
        "destinationCurrency": to_token.address,
        "recipient": address,
        "tradeType": "EXACT_INPUT",
        "amount": int(amount * 10 ** from_token.decimals),
        "referrer": "relay.link/swap",
        "useExternalLiquidity": False,
        "useDepositAddress": False
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Origin': 'https://relay.link',
    }

    response = requests.post(url, json=body, headers=headers)

    return response.json()


def get_request_id(to_chain: Chain, amount: float, from_token: Token, to_token: Token) -> str:
    """
    Извлекает requestId из ответа к API relay.link
    """

    response = relay_request_api(to_chain, amount, from_token, to_token)
    return response['steps'][0]['requestId']


def get_call_data(to_chain: Chain, amount: float, from_token: Token, to_token: Token) -> str:
    """
    Извлекает data из ответа к API relay.link
    """
    response = relay_request_api(to_chain, amount, from_token, to_token)
    return response['steps'][0]['items'][0]['data']['data']


def bridge_relay(
        to_chain: Chain,
        amount: float,
        from_token: Token | None = None,
        to_token: Token | None = None
) -> str:
    # создаем объект токена для нативной валюты
    native_token = Token(
        chain.native_token,
        '0x0000000000000000000000000000000000000000',
        18,
        chain
    )

    # если не указан токен, то используем нативный токен
    from_token = from_token or native_token
    to_token = to_token or native_token

    # переводим сумму в wei
    amount_wei = int(amount * 10 ** from_token.decimals)

    if from_token == native_token:  # если отправляем нативный токен
        # получаем requestId для отправки нативного токена
        request_id = get_request_id(to_chain, amount, from_token, to_token)
        # адрес контракта моста
        contract_address = w3.to_checksum_address('0xa5f565650890fba1824ee0f21ebbbf660a179934')

        # параметры транзакции
        tx_params = {
            'from': address,
            'nonce': w3.eth.get_transaction_count(address),
            'chainId': w3.eth.chain_id,
            'to': contract_address,
            'value': amount_wei,
            'data': request_id
        }
    else:  # если отправляем ERC20 токен
        # получаем data для отправки ERC20 токена (data + requestId)
        data = get_call_data(to_chain, amount, from_token, to_token)
        # упаковываем транзакцию (erc20.transfer + requestId)
        tx_params = {
            'from': address,
            'nonce': w3.eth.get_transaction_count(address),
            'chainId': w3.eth.chain_id,
            'to': from_token.address,
            'data': data
        }

    # готовим и отправляем транзакцию
    tx_params = get_fee(tx_params, w3)
    tx_params['gas'] = w3.eth.estimate_gas(tx_params)
    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Tx hash: {tx_hash.hex()}")
    return tx_hash.hex()

#
# bridge_relay(Chains.Optimism, 0.1, Tokens.USDT_ARBITRUM, Tokens.USDT_OP)
# bridge_relay(Chains.Optimism, 0.1, Tokens.USDT_ARBITRUM)

# код пишем тут