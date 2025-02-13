from __future__ import annotations

from decimal import Decimal

from web3 import Web3, HTTPProvider
from web3.types import Wei


class Blockchain:
    accounts = {
        '0x00...01': {                                  # * EOA (обычный кошелёк) 	Externally Owned Account
            'balance': 1000000000000000000,             # * нативный баланс в Wei
            'nonce': 0,                                 # * количество транзакций отправленных с адреса
        },
        '0x00...02': {                                  # * контракт (адрес контракта) Contract Account
            'balance': 1000000000000000000,             # * нативный баланс в Wei
            'nonce': 0,                                 # * количество транзакций отправленных с адреса
            'code': '0x00...00',                        # * байт-код контракта
            'storage': {                                # * хранилище контракта
                '0x00...00': 1000000000000000000,       # * ключ: значение
                '0x00...01': 1000000000000000000,       # * ключ: значение
                'decimals': 6                           # * ключ: значение
            },
            'storageRoot': '0x00...00',                 # * хэш хранилища
            'codeHash': '0x00...00',                    # * хэш байт-кода
        },
        '0x00...03': {},
    }

    def get_balance(self, address: str) -> int:
        return self.accounts.get(address, {}).get('balance', 0)

    def transfer(self, from_address: str, to_address: str, value: float):
        if self.get_balance(from_address) < value:
            raise ValueError('Not enough balance')
        self.accounts[from_address]['balance'] -= value
        self.accounts[to_address]['balance'] += value


class Contract:

    def hack(self):
        total = 1 # 200 gas
        while True: # 100 gas =
            total += 1 # 500 gas
            print()





# нативный токен и все остальные токены ERC20
# балансы нативных токенов в storage
# единая система исчисления нативных токенов у всех EVM сетей
# ETHER, WEI, GWEI
# Decimals
# Конвертация в Ether, математически или при помощи методов
# Неточность float, хранение в Decimal
# Получение баланса методом
# где и зачем применять запросы балансов
# Конвертация баланса через методы и математически

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
    Linea = Chain('Linea', 'https://1rpc.io/linea', 'ETH')
    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH')
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH')
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH')
    BSC = Chain('BSC', 'https://1rpc.io/bnb', 'BNB')


class Onchain:
    def __init__(self, chain: Chain):
        self.chain = chain
        self.w3 = Web3(HTTPProvider(chain.rpc_url))


    def get_native_balance(self, address: str) -> Amount:
        """
        Получение баланса нативного токена
        :param address: адрес кошелька
        :return: баланс в Amount
        """
        address = self.w3.to_checksum_address(address)
        balance_wei = self.w3.eth.get_balance(address)
        return Amount(balance_wei, is_wei=True)



def main():
    onchain = Onchain(Chains.Linea)
    balance = onchain.get_native_balance('0x624c222fEd7f88500Afa5021cC760B3106fe34be')
    print(balance)



    # decimals = 18
    # print(balance_wei / 10 ** decimals) # float +
    # print(w3.from_wei(balance_wei, 'ether'))














if __name__ == '__main__':
    main()
