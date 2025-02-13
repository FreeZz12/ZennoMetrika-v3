""""""

"""
Задание 1 - easy

Напишите функцию get_balance, которая принимает адрес кошелька и
возвращает баланс нативного токена в человекочитаемом виде.
rpc_url для выбора сети должен браться из глобальной переменной.

"""
from web3 import Web3
rpc_url = 'https://1rpc.io/eth'

def get_balance(address: str) -> float:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    address = w3.to_checksum_address(address)
    balance_wei = w3.eth.get_balance(address)
    return float(w3.from_wei(balance_wei, 'ether'))

# код пишем тут

"""
Задание 2  - medium

Напишите функцию get_balances, которая принимает список адресов кошельков
проверяет балансы при помощи функции get_balance и
возвращает словарь с балансами нативного токена в человекочитаемом виде.
Где ключ - адрес кошелька, значение - баланс.
rpc_url для выбора сети должен браться из глобальной переменной.

"""

# код пишем тут

def get_balances(addresses: list[str]) -> dict:
    return {address: get_balance(address) for address in addresses}

"""
Задание 3 - hard
Создайте класс Onchain, который принимает в себя объект Chain
в котором содержится информация о сети и нативном токене.
В init создайте объект Web3 с rpc_url из Chain.
Создайте метод get_balance, который принимает адрес кошелька, проверяет
нативный баланс и возвращает объект Amount.
Метод должен так же печатать в терминале информацию о балансе в формате
"Баланс кошелька {адрес} на сети {имя сети} составляет {баланс в ether} {имя токена}".
При смене сети в выводе должна меняться информация о сети и токене.
"""
from decimal import Decimal

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


class Chain:
    def __init__(self, name: str, rpc_url: str, native_token: str):
        self.name = name
        self.rpc_url = rpc_url
        self.native_token = native_token

class Chains:
    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH')

class Onchain:
    def __init__(self, chain: Chain):
        self.chain = chain
        self.w3 = Web3(Web3.HTTPProvider(chain.rpc_url))

    def get_balance(self, address: str) -> Amount:
        """
        Получение баланса нативного токена
        :param address: адрес кошелька
        :return: объект Amount с балансом в разных форматах
        """
        address = self.w3.to_checksum_address(address)
        balance_wei = self.w3.eth.get_balance(address)
        balance = Amount(balance_wei, is_wei=True)
        print(f'Баланс кошелька {address} на сети {self.chain.name} составляет {balance} {self.chain.native_token}')
        return balance
# код пишем тут

