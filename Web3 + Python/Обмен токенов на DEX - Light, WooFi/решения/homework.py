""""""
import time

"""
Задание 1 - easy

Создайте скрипт для обмена ETH на USDT через биржу WooFi в сети Arbitrum. Скрипт должен выполнить следующие действия:

- Подключиться к сети Arbitrum
- Выполнить обмен ETH на USDT через WooFi DEX
- Вывести результат операции

Адрес контракта получите из запросов сайта при обмене или из кошелька при предложении подписания транзакции.
"""

import json
import os

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


def task_1():
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/arb'))

    contract_address = w3.to_checksum_address('0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7')

    with open('woofi_router.json') as f:
        abi = json.loads(f.read())

    contract = w3.eth.contract(address=contract_address, abi=abi)

    private_key = os.getenv('PK')
    address = w3.eth.account.from_key(private_key).address

    amount = 0.00001
    amount_wei = w3.to_wei(amount, 'ether')

    tx_params = {
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
        'chainId': w3.eth.chain_id,
        'value': amount_wei,
    }
    eth_token = w3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
    weth_token = w3.to_checksum_address('0x82aF49447D8a07e3bd95BD0d56f35241523fBab1')

    from_token = w3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
    to_token = w3.to_checksum_address('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')

    min_to_amount = contract.functions.querySwap(
        fromToken=weth_token if from_token == eth_token else from_token,
        toToken=to_token,
        fromAmount=amount_wei
    ).call()

    slippage = 5
    min_to_amount = int(min_to_amount * (1 - slippage / 100))  # * 0.95

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


"""
Задание 2 - medium.

Написать скрипт для работы с токенами в сети Arbitrum, который выполняет следующие действия:

1. Считывает приватные ключи из файла private_keys.txt
2. Генерирует адреса кошельков из приватных ключей
3. Проверяет балансы следующих токенов в сети Arbitrum (контракты необходимо найти самостоятельно):
    - USDT
    - USDC
    - Bridged USDC
4. При обнаружении баланса любого из токенов более 1$:
    - Выполнить approve токена на контракт WooFi (если требуется)
    - Обменять токен на ETH через WooFi DEX

Требования к реализации:

- Добавить случайные задержки между операциями и кошельками для обеспечения безопасности
- Реализовать подробное логирование:.
    - Адрес кошелька
    - Токен
    - Сумма обмена
    - Хеш транзакции
    
"""

import json
import random
from decimal import Decimal


class Chain:
    """
    Контейнер для хранения данных сети
    """

    def __init__(self, name: str, rpc: str, native_token: str, chain_id: int,  multiplier: float = 1.0):
        self.name = name
        self.rpc = rpc
        self.native_token = native_token
        self.chain_id = chain_id
        self.multiplier = multiplier

    def __eq__(self, other) -> bool:
        """
        Переопределение сравнения для двух сетей, сверяя по атрибутам сети.
        """
        return self.name == other.name and self.rpc == other.rpc and self.native_token == other.native_token and \
               self.chain_id == other.chain_id and self.multiplier == other.multiplier

class Chains:
    """
    Класс для хранения объектов сетей
    """
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH', 42161)
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH', 10)


class ContractData:
    """
    Класс для хранения данных контракта
    """

    def __init__(self, name: str, address: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.chain = chain

    def __eq__(self, other):
        return self.name == other.name and self.address == other.address and self.chain == other.chain


class ContractsData:
    """
    Класс для хранения адресов контрактов
    """
    WOOFI_ROUTER = ContractData('woofi_router', '0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7', Chains.Arbitrum)


class Token(ContractData):

    def __init__(self, name: str, address: str, chain: Chain, decimals: int = 18):
        super().__init__(name, address, chain)
        self.decimals = decimals


class Tokens:
    ETH_ARBITRUM = Token('ETH', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', Chains.Arbitrum)
    WETH_ARBITRUM = Token('WETH', '0x82af49447d8a07e3bd95bd0d56f35241523fbab1', Chains.Arbitrum)
    USDT_ARBITRUM = Token('USDT', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', Chains.Arbitrum, 6)
    USDC_ARBITRUM = Token('USDC', '0xaf88d065e77c8cc2239327c5edb3a432268e5831', Chains.Arbitrum, 6)
    USDC_E_ARBITRUM = Token('USDC_E', '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8', Chains.Arbitrum, 6)
    ETH_OP = Token('ETH', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', Chains.Optimism)
    WETH_OP = Token('WETH', '0x4200000000000000000000000000000000000006', Chains.Optimism)
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', Chains.Optimism, 6)

    @classmethod
    def get_token_by_name(cls, name: str, chain: Chain) -> Token | None:
        """
        Получение объекта токена по имени и сети
        :param name: Название токена из атрибута name
        :param chain: объект сети
        :return: объект токена с совпадающим именем и сетью
        """
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.name == name and token.chain == chain:
                    return token
        return None


class Amount:
    wei: int
    ether: float
    ether_decimals: Decimal

    def __init__(self, amount: int | float, decimals: int = 18, is_wei: bool = False):
        if is_wei:
            self.wei = int(amount)
            self.ether_decimals = Decimal(str(amount)) / 10 ** decimals
            self.ether = float(self.ether_decimals)
        else:
            self.wei = int(amount * 10 ** decimals)
            self.ether_decimals = Decimal(str(amount))
            self.ether = float(self.ether_decimals)

    def __str__(self):
        return f'{self.ether}'


class Utils:

    @staticmethod
    def get_list_from_file(file_name: str) -> list[str]:
        with open(file_name, 'r') as f:
            return f.read().splitlines()


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
        if not path.endswith('.json'):
            path += '.json'
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
        fee_history = self.w3.eth.fee_history(20, 'latest', [40])

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

    def send_token(self, amount: Amount, to_address: str, token: Token | str | None = None) -> str:
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
            tx_params = self._prepare_tx_params(to_address, amount.wei)
        else:
            if isinstance(token, Token):
                contract_address = token.address
                token_name = token.name
            else:
                contract_address = token

            token_contract_address = self.w3.to_checksum_address(contract_address)
            abi = self._get_abi('erc20.json')
            contract = self.w3.eth.contract(address=token_contract_address, abi=abi)

            if token_name is None:
                token_name = contract.functions.symbol().call()

            tx_params = self._prepare_tx_params()
            tx_params = contract.functions.transfer(to_address, amount.wei).build_transaction(tx_params)

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

    def get_balance(self, token: Token | None = None, address: str | None = None) -> Amount:
        """
        Получение баланса токена на адресе
        :param token: объект токена или None, если нужно получить баланс нативного токена
        :param address: адрес кошелька, если не указан, то берется адрес кошелька из объекта Onchain
        :return: объект Amount с балансом
        """

        if not address:
            address = self.address

        if token and token.chain != self.chain:
            raise ValueError('Передан токен из другой сети')

        address = self.w3.to_checksum_address(address)

        if not token:
            return Amount(self.w3.eth.get_balance(address), is_wei=True)

        with open('erc20.json') as file:
            abi = json.loads(file.read())

        contract = self.w3.eth.contract(address=token.address, abi=abi)
        balance = contract.functions.balanceOf(address).call()
        return Amount(balance, token.decimals, is_wei=True)

    def allowance(self, token: Token, spender: str) -> Amount:
        """
        Получение суммы имеющегося апрува на токены
        :param token: объект токена с адресом контракта
        :param spender: адрес кошелька, на который разрешено переводить токены
        :return: сумма апрува в wei
        """
        spender = self.w3.to_checksum_address(spender)
        abi = self._get_abi('erc20.json')
        contract = self.w3.eth.contract(address=token.address, abi=abi)
        allowance_wei = contract.functions.allowance(self.address, spender).call()
        return Amount(allowance_wei, token.decimals, is_wei=True)

    def approve(self, token: Token, spender: str, amount: Amount) -> str:
        """
        Отправка транзакции апрува на токены
        :param token: объект токена с адресом контракта
        :param spender: адрес кошелька, на который разрешено переводить токены
        :param amount: сумма апрува в токенах (не в wei)
        :return: хэш транзакции
        """
        spender = self.w3.to_checksum_address(spender)
        abi = self._get_abi('erc20.json')
        contract = self.w3.eth.contract(address=token.address, abi=abi)

        allowance = self.allowance(token, spender)
        if amount.wei != 0 and allowance.wei >= amount.wei:
            print(f'Транзакция апрув не требуется, т.к. разрешение уже есть')
            return '0x'

        tx_params = contract.functions.approve(spender, amount.wei).build_transaction(
            self._prepare_tx_params())
        tx_params = self.get_fee(tx_params)
        tx_params['gas'] = int(
            self.w3.eth.estimate_gas(tx_params) * self._get_multiplier() * self.chain.multiplier)

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Транзакция апрув {tx_hash.hex()} отправлена, в блокчейне {self.chain.name},\n'
              f'токен {token.name} на сумму {amount} кошельку {spender}')
        return tx_hash.hex()

    def swap_woofi(self, from_token: Token, to_token: Token, amount: Amount) -> None:
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

        abi = self._get_abi(ContractsData.WOOFI_ROUTER.name)
        contract = self.w3.eth.contract(
            address=ContractsData.WOOFI_ROUTER.address,
            abi=abi
        )

        min_to_amount = contract.functions.querySwap(
            fromToken=weth_token.address if from_token == eth_token else from_token.address,
            toToken=weth_token.address if to_token == eth_token else to_token.address,
            fromAmount=amount.wei
        ).call()

        min_to_amount = int(min_to_amount * 0.95)

        value = amount.wei if from_token == eth_token else 0

        tx_params = self._prepare_tx_params(value=value)

        tx_params = contract.functions.swap(
            fromToken=from_token.address,
            toToken=to_token.address,
            fromAmount=amount.wei,
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

        print(
            f'Транзакция {tx_hash.hex()} отправлена, в блокчейне {self.chain.name}, своп {from_token.name} -> {to_token.name}')
        return tx_hash.hex()


def task_2():
    private_keys = Utils.get_list_from_file('private_keys.txt')

    chain = Chains.Arbitrum

    for private_key in private_keys:
        onchain = Onchain(chain, private_key)
        eth_balance = onchain.get_balance()
        usdt_balance = onchain.get_balance(Tokens.USDT_ARBITRUM)
        usdc_balance = onchain.get_balance(Tokens.USDC_ARBITRUM)
        usdc_e_balance = onchain.get_balance(Tokens.USDC_E_ARBITRUM)

        print(f'ETH: {eth_balance}')
        print(f'USDT: {usdt_balance}')
        print(f'USDC: {usdc_balance}')
        print(f'USDC_E: {usdc_e_balance}')

        if usdt_balance.ether > 1:
            onchain.swap_woofi(Tokens.USDT_ARBITRUM, Tokens.ETH_ARBITRUM, usdt_balance)

        if usdc_balance.ether > 1:
            onchain.swap_woofi(Tokens.USDC_ARBITRUM, Tokens.ETH_ARBITRUM, usdc_balance)

        if usdc_e_balance.ether > 1:
            onchain.swap_woofi(Tokens.USDC_E_ARBITRUM, Tokens.ETH_ARBITRUM, usdc_e_balance)


# код пишем тут

"""
Задание 3 - hard

Написать бота, который набивает торговые объемы на кошельке на бирже WooFi.

1. Извлекает приватные ключи из файла private_keys.txt
2. Перемешивает ключи
3. В цикле перебирает ключи с рандомной паузой, чтобы за неделю отработали все кошельки.
4. Скрипт проверяет актуальные объемы в паре USDT/ETH у каждого кошелька, либо при помощи
запроса логов в etherscan и извлечением данных из Data или Topics, либо через запрос 
списка Normal Transaction в etherscan, с извлечением данных из data транзакций swap.
2. Если объемы меньше 1000$, то делается обмен на ~20-50$, при этом
должен продаваться тот токен, которого больше в $ эквиваленте.
5. Скрипт должен работать в бесконечном цикле, набивая рандомные объемы, но 
не больше 1000$ на кошелек

Усложнение: Сделайте чтобы скрипт можно было запускать в разных сетях (Arbitrum, Optimism)
меняя сеть в конфиге.
"""


from datetime import timedelta

import requests


class VolumeBot(Onchain):

    def __init__(self, chain: Chain, private_key: str):
        super().__init__(chain, private_key)

    def get_swap_price(self) -> float:
        """
        Получение цены свопа
        """
        abi = self._get_abi(ContractsData.WOOFI_ROUTER.name)
        contract = self.w3.eth.contract(address=ContractsData.WOOFI_ROUTER.address, abi=abi)
        token_usdt = Tokens.get_token_by_name('USDT', self.chain)
        weth_token = Tokens.get_token_by_name('WETH',  self.chain)
        price_wei = contract.functions.querySwap(
            fromToken=weth_token.address,
            toToken=token_usdt.address,
            fromAmount=1*10**18
        ).call()
        return Amount(price_wei, decimals=Tokens.USDT_ARBITRUM.decimals, is_wei=True).ether

    def get_swap_logs(self) -> list[dict]:
        """
        Получение логов Approval(address,address,uint256) по адресу отправителя
        :return: список логов
        """
        url = f'https://api.etherscan.io/v2/api'
        params = {
            'chainid': self.chain.chain_id,
            'module': 'logs',
            'action': 'getLogs',
            'fromBlock': 0,
            'toBlock': 'latest',
            'address': '0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7',
            'topic0': '0x' + Web3.keccak(text='WooRouterSwap(uint8,address,address,uint256,uint256,address,address,address)').hex(),
            # хеш функции keccak256 от строки "WooRouterSwap(uint8,address,address,uint256,uint256,address,address,address)"
            'topic0_3': 'and',  # указание что будет дополнительный параметр фильтрации
            'topic3': '0x' + self.address[2:].rjust(64, '0'),
            # адрес владельца токена дополненный нулями слева до 64 символов
            'apikey': os.getenv('ETHERSCAN_API_KEY'),
        }
        response = requests.get(url, params=params)
        return response.json()['result']


    def get_total_volume(self) -> float:
        """
        Получение общего объема торгов по адресу
        :return: общий объем торгов
        """
        logs = self.get_swap_logs()
        total = 0
        usdt_token = Tokens.get_token_by_name('USDT', self.chain)
        eth_token = Tokens.get_token_by_name('ETH', self.chain)

        for log in logs:
            from_token = Web3.to_checksum_address('0x' + log['topics'][1][26:])
            to_token =  Web3.to_checksum_address('0x' + log['topics'][2][26:])
            data = log['data'][2:]
            from_amount = int(data[64:64*2], 16)
            to_amount = int(data[64*2:64*3], 16)
            if from_token == usdt_token.address:
                if to_token == eth_token.address:
                    total += from_amount
            elif from_token == eth_token.address:
                if to_token == usdt_token.address:
                    total += to_amount

        return Amount(total, 6, is_wei=True).ether




def task_3():
    private_keys = Utils.get_list_from_file('private_keys.txt')


    chain = Chains.Arbitrum

    token_usdt = Tokens.get_token_by_name('USDT', chain)
    eth_token = Tokens.get_token_by_name('ETH', chain)
    fix_delay = timedelta(weeks=1).total_seconds()
    print()

    while True:
        random.shuffle(private_keys)
        for private_key in private_keys:
            volume_bot = VolumeBot(chain, private_key)
            volume = volume_bot.get_total_volume()
            print(f'Объем торгов: {volume}')
            if volume > 1000:
                continue
            eth_price = volume_bot.get_swap_price()
            eth_balance = volume_bot.get_balance()
            usdt_balance = volume_bot.get_balance(token_usdt)
            amount_usd = random.uniform(20, 50)
            if usdt_balance.ether > eth_balance.ether * eth_price:
                amount_usdt = Amount(amount_usd, decimals=token_usdt.decimals)
                volume_bot.swap_woofi(token_usdt, eth_token, amount_usdt)
            else:
                amount_eth = Amount(amount_usd / eth_price)
                volume_bot.swap_woofi(eth_token, token_usdt, amount_eth)
            random_delay = (random.uniform(-500, 500) + fix_delay) or 60
            time.sleep(random_delay)




task_3()