""""""

"""
Задание 1 - easy
Напишите скрипт, который позволяет берет из файла сид фразы,
и сохраняет в 2 отдельных файла приватный ключ и адрес в том же порядке, как они идут в файле сид фраз.

"""
from eth_account import Account

with open('seed.txt', 'r') as file:
    seeds = file.read().split()

Account.enable_unaudited_hdwallet_features()

for seed in seeds:
    account = Account.from_mnemonic(seed)
    private_key = account.key.hex()
    address = account.address
    with open('private_keys.txt', 'a') as file:
        file.write(private_key + '\n')
    with open('addresses.txt', 'a') as file:
        file.write(address + '\n')

# код пишем тут

"""
Задание 2  - medium
Напишите функцию, которая принимает на вход приватный ключ и возвращает адрес кошелька.

"""
from eth_account import Account

def get_address(private_key: str) -> str:
    account = Account.from_key(private_key)
    return account.address


# код пишем тут

"""
Задание 3 - hard

Напишите функцию create_pk_and_address, которая генерирует приватный ключ и адрес кошелька.
def create_pk_and_address() -> tuple[str, str]:
    Генерирует приватный ключ и адрес кошелька
    :return: приватный ключ, адрес кошелька


Генератор должен использовать дополнительную крипто-безопасную энтропию из библиотеки secrets.
Напишите функцию get_pk_and_address, которая принимает на вход seed фразу, номер счета и возвращает приватный ключ и адрес кошелька.
Приватный ключ должен быть извлечен из seed фразы по пути m/44'/60'/0'/0/account_number.

def get_pk_and_address(seed: str, account_number: int = 0) -> tuple[str, str]:
    Генерирует приватный ключ и адрес кошелька
    :param seed: seed фраза
    :param account_number: номер счета
    :return: приватный ключ, адрес кошелька
"""
from eth_account import Account
import secrets

def create_pk_and_address() -> tuple[str, str]:
    """
    Генерирует приватный ключ и адрес кошелька
    :return: приватный ключ, адрес кошелька
    """
    entropy = secrets.token_bytes(32)
    account = Account.create(entropy=entropy)
    return account.key.hex(), account.address

def get_pk_and_address(seed: str, account_number: int = 0) -> tuple[str, str]:
    """
    Генерирует приватный ключ и адрес кошелька
    :param seed: seed фраза
    :param account_number: номер счета
    :return: приватный ключ, адрес кошелька
    """
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(seed, f"m/44'/60'/0'/0/{account_number}")
    return account.key.hex(), account.address

# код пишем тут

