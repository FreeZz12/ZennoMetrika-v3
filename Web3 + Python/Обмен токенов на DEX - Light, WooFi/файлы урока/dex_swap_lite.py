""""""
import json
import os
import random
from decimal import Decimal

from web3 import Web3, HTTPProvider
from dotenv import load_dotenv

load_dotenv()


# w3 = Web3(Web3.HTTPProvider('https://1rpc.io/arb'))
#
# """
# 0xe94803f4
# 00000000000000000000000082af49447d8a07e3bd95bd0d56f35241523fbab1
# 000000000000000000000000fd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9
# 0000000000000000000000000000000000000000000000004563918244f40000
# """
#
# contract_address = w3.to_checksum_address('0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7')
#
# with open('woofi_router_abi.json') as f:
#     abi = json.loads(f.read())
#
# contract = w3.eth.contract(address=contract_address, abi=abi)
#
# private_key = os.getenv('PK')
# address = w3.eth.account.from_key(private_key).address
#
# amount = 0.00001
# amount_wei = w3.to_wei(amount, 'ether')
#
# tx_params = {
#     'from': address,
#     'nonce': w3.eth.get_transaction_count(address),
#     'chainId': w3.eth.chain_id,
#     'value': amount_wei,
# }
# eth_token = w3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
# weth_token = w3.to_checksum_address('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1')
#
# from_token = w3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
# to_token = w3.to_checksum_address('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
#
# min_to_amount = contract.functions.querySwap(
#     fromToken=weth_token if from_token == eth_token else from_token,
#     toToken=to_token,
#     fromAmount=amount_wei
# ).call()
#
# slippage = 5
# min_to_amount = int(min_to_amount * (1 - slippage / 100))  # * 0.95
#
# tx_params = contract.functions.swap(
#     fromToken=from_token,
#     toToken=to_token,
#     fromAmount=amount_wei,
#     minToAmount=min_to_amount,
#     to=address,
#     rebateTo=address
# ).build_transaction(tx_params)
#
# signed_tx = w3.eth.account.sign_transaction(tx_params, private_key=private_key)
# tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
# print(tx_hash.hex())

#
w3 = Web3(Web3.HTTPProvider('https://1rpc.io/arb'))

"""
0xe94803f4
00000000000000000000000082af49447d8a07e3bd95bd0d56f35241523fbab1
000000000000000000000000fd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9
0000000000000000000000000000000000000000000000004563918244f40000
"""

contract_address = w3.to_checksum_address('0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7')

with open('woofi_router_abi.json') as f:
    abi = json.loads(f.read())

contract = w3.eth.contract(address=contract_address, abi=abi)

private_key = os.getenv('PK')
address = w3.eth.account.from_key(private_key).address

amount = 1
amount_wei = amount * 10 ** 6

tx_params = {
    'from': address,
    'nonce': w3.eth.get_transaction_count(address),
    'chainId': w3.eth.chain_id,
}
eth_token = w3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
weth_token = w3.to_checksum_address('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1')

from_token = w3.to_checksum_address('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
to_token = w3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')

with open('erc20.json') as f:
    abi_erc20 = json.loads(f.read())

contract_token = w3.eth.contract(address=from_token, abi=abi_erc20)

decimals = contract_token.functions.decimals().call()
allowances = contract_token.functions.allowance(address, contract_address).call()
if allowances < amount_wei:
    tx_params = contract_token.functions.approve(contract_address, amount_wei).build_transaction(tx_params)
    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    # нужно доджаться обновления allowances и nonce
    w3.eth.wait_for_transaction_receipt(tx_hash)


min_to_amount = contract.functions.querySwap(
    fromToken=from_token,
    toToken=weth_token if to_token == eth_token else to_token,
    fromAmount=amount_wei
).call()


slippage = 5
min_to_amount = int(min_to_amount * (1 - slippage / 100))  # * 0.95
print(from_token, to_token, amount_wei, min_to_amount)
tx_params = contract.functions.swap(
    fromToken=from_token,
    toToken=to_token,
    fromAmount=amount_wei,
    minToAmount=min_to_amount,
    to=address,
    rebateTo=address
).build_transaction(tx_params)

signed_tx = w3.eth.account.sign_transaction(tx_params, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
print(tx_hash.hex())


class Chain:
    def __init__(self, name: str, rpc: str, native_token: str, multiplier: float = 1.0):
        self.name = name
        self.rpc = rpc
        self.native_token = native_token
        self.multiplier = multiplier

    def __eq__(self, other):
        return self.name == other.name and self.rpc == other.rpc and self.native_token == other.native_token and self.multiplier == other.multiplier


class Chains:
    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH')
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH')
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH')
    BSC = Chain('BSC', 'https://1rpc.io/bnb', 'BNB')
    LINEA = Chain('LINEA', 'https://1rpc.io/linea', 'ETH', 1.3)


class Token:
    def __init__(self, name: str, address: str, decimals: int, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.decimals = decimals
        self.chain = chain

    def __eq__(self, other):
        return self.name == other.name and self.address == other.address and self.decimals == other.decimals and self.chain == other.chain


class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6, Chains.Optimism)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6, Chains.Optimism)
    ETH_ARBITRUM = Token('ETH', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 18, Chains.Arbitrum)
    WETH_ARBITRUM = Token('WETH', '0x82af49447d8a07e3bd95bd0d56f35241523fbab1', 18, Chains.Arbitrum)
    USDT_ARBITRUM = Token('USDT', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', 6, Chains.Arbitrum)
    USDC_ARBITRUM = Token('USDC', '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', 6, Chains.Arbitrum)

    @classmethod
    def get_token_by_name(cls, name: str, chain: Chain) -> Token | None:
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.name == name and token.chain == chain:
                    return token
        return None


class ContractData:
    def __init__(self, name: str, address: str, abi: str):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.abi = abi


class ContractsData:
    WOOFI_ROUTER = ContractData('Woofi Router', '0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7',
                                'woofi_router_abi.json')


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

    def allowance(self, token: Token, spender: str) -> int:
        """
        Получение суммы имеющегося апрува на токены
        :param token: объект токена с адресом контракта
        :param spender: адрес кошелька, на который разрешено переводить токены
        :return: сумма апрува в wei
        """
        spender = self.w3.to_checksum_address(spender)
        abi = self._get_abi('erc20.json')
        contract = self.w3.eth.contract(address=token.address, abi=abi)
        return contract.functions.allowance(self.address, spender).call()

    def approve(self, token: Token, spender: str, amount: float) -> str:
        """
        Отправка транзакции апрува на токены
        :param token: объект токена с адресом контракта
        :param spender: адрес кошелька, на который разрешено переводить токены
        :param amount: сумма апрува в токенах (не в wei)
        :return: хэш транзакции
        """
        spender = self.w3.to_checksum_address(spender)
        amount = int(amount * 10 ** token.decimals)
        abi = self._get_abi('erc20.json')
        contract = self.w3.eth.contract(address=token.address, abi=abi)

        allowance = contract.functions.allowance(self.address, spender).call()
        if amount != 0 and allowance >= amount:
            print(f'Транзакция апрув не требуется, т.к. разрешение уже есть')
            return '0x'

        tx_params = contract.functions.approve(spender, amount).build_transaction(self._prepare_tx_params())
        tx_params = self.get_fee(tx_params)
        tx_params['gas'] = int(
            self.w3.eth.estimate_gas(tx_params) * self._get_multiplier() * self.chain.multiplier)

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Транзакция апрув {tx_hash.hex()} отправлена, в блокчейне {self.chain.name},\n'
              f'токен {token.name} на сумму {amount / 10 ** token.decimals} кошельку {spender}')
        return tx_hash.hex()

    def swap_woofi(self, from_token: Token, to_token: Token, amount: float) -> None:
        """
        Своп токенов через Woofi
        :param from_token: объект Token, токен, который отправляем
        :param to_token: объект Token, токен, который получаем
        :param amount: сумма токенов в человеческом формате
        """

        weth_token = Tokens.get_token_by_name('WETH', self.chain)
        eth_token = Tokens.get_token_by_name('ETH', self.chain)

        if from_token != eth_token:
            self.approve(from_token, ContractsData.WOOFI_ROUTER.address, amount)

        abi = self._get_abi(ContractsData.WOOFI_ROUTER.abi)
        contract = self.w3.eth.contract(
            address=ContractsData.WOOFI_ROUTER.address,
            abi=abi
        )

        min_to_amount = contract.functions.querySwap(
            fromToken=weth_token.address if from_token == eth_token else from_token.address,
            toToken=weth_token.address if to_token == eth_token else to_token.address,
            fromAmount=int(amount * 10 ** from_token.decimals)
        ).call()

        min_to_amount = int(min_to_amount * 0.95)

        amount_wei = int(amount * 10 ** from_token.decimals)

        value = amount_wei if from_token == eth_token else 0

        tx_params = self._prepare_tx_params(value=value)

        tx_params = contract.functions.swap(
            fromToken=from_token.address,
            toToken=to_token.address,
            fromAmount=amount_wei,
            minToAmount=min_to_amount,
            to=self.address,
            rebateTo=self.address
        ).build_transaction(tx_params)

        tx_params = self.get_fee(tx_params)

        if tx_params.get('gas') is None:
            tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * self._get_multiplier())

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f'Транзакция {tx_hash.hex()} отправлена, в блокчейне {self.chain.name}, своп {from_token.name} -> {to_token.name}')
        return tx_hash.hex()


onchain = Onchain(Chains.Arbitrum, os.getenv('PK'))
onchain.swap_woofi(Tokens.USDC_ARBITRUM, Tokens.USDT_ARBITRUM, 0.1)








