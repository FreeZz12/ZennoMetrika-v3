""""""
import random

"""
Задание 1 - easy
Напишите скрипт для отправки нативного токена BNB в сети BSC.
В начале скрипта определяются переменные:
- приватный ключ кошелька отправителя
- адрес кошелька получателя
- сумма перевода в BNB

Скрипт должен отправлять транзакцию с указанными параметрами и 
выводить в консоль хеш транзакции.

"""
from web3 import Web3

pk = '0x...'
from_address = Web3.eth.account.from_key(pk).address
to_address = Web3.to_checksum_address('0x...')
amount = 0.1

rpc_url = 'https://bsc-dataseed.binance.org/'
w3 = Web3(Web3.HTTPProvider(rpc_url))

tx_data = {
    'from': from_address,
    'to': to_address,
    'value': w3.to_wei(amount, 'ether'),
    'gas': 21000,
    'gasPrice': w3.eth.gas_price
}

signed_tx = w3.eth.account.sign_transaction(tx_data, pk)
tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
w3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Транзакция отправлена: {tx_hash.hex()}')

# код пишем тут

"""
Задание 2  - medium

Напишите функцию sent_native_token, которая принимает параметры:
- приватный ключ кошелька отправителя
- адрес кошелька получателя
- сумма перевода
- rpc_url сети

Функция должна отправлять транзакцию с указанными параметрами и
возвращать хеш транзакции.

"""


def get_multiplayer(min_mult: float = 1.02, max_mult: float = 1.05) -> float:
    """
    Получает множитель для рандомизации чисел. 1.00 =100%, 1.05 = 105%, 0.05 = 5%
    :return: множитель
    """
    return random.uniform(min_mult, max_mult)

def get_fee(w3: Web3, tx: dict) -> dict:
    fee_history = w3.eth.fee_history(10, 'latest', [20])

    if any(fee_history.get('baseFeePerGas', [0])):
        base_fee = fee_history.get('baseFeePerGas', [0])[-1]
        priority_fees = [priority_fee[0] for priority_fee in
                         fee_history.get('reward', [[0]])]  # находим индекс медианы
        median_index = len(priority_fees) // 2
        # сортируем список, чтобы найти медиану
        priority_fees.sort()
        # получаем медиану (среднее без искажений)
        median_priority_fee = priority_fees[median_index]

        # вычисляем итоговую комиссию
        priority_fee = int(median_priority_fee * get_multiplayer())
        max_fee = int((base_fee + priority_fee) * get_multiplayer())

        # добавляем параметры в транзакцию
        tx['type'] = 2
        tx['maxFeePerGas'] = max_fee
        tx['maxPriorityFeePerGas'] = priority_fee
    else:
        tx['gasPrice'] = int(w3.eth.gas_price * get_multiplayer())

    return tx




def sent_native_token(pk: str, to_address: str, amount: float, rpc_url: str) -> str:
    """
    Отправляет нативный токен в переданную в rpc_url сеть
    :param pk: приватный ключ кошелька отправителя
    :param to_address: адрес кошелька получателя
    :param amount: сумма перевода
    :param rpc_url: rpc_url сети
    :return: хеш транзакции
    """
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    from_address = w3.eth.account.from_key(pk).address
    to_address = w3.to_checksum_address(to_address)

    tx = {
        'from': from_address,
        'to': to_address,
        'value': w3.to_wei(amount, 'ether'),
    }

    tx = get_fee(w3, tx)
    tx['gas'] = w3.eth.estimate_gas(tx)

    signed_tx = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f'Транзакция отправлена: {tx_hash.hex()}')
    return tx_hash.hex()
# код пишем тут

"""
Задание 3 - hard

Напишите дрейнер кошельков, который берет из файла список приватных ключей,
проверяет наличие балансов нативных токенов и отправляет все имеющиеся
нативные токены в сетях ETH, BSC, ARBITRUM, OPTIMISM, LINEA на указанный
адрес кошелька.

Не забывайте оставлять нативные токены на оплату газа.
"""


class Chain:
    def __init__(self, name: str, rpc: str, native_token: str) -> None:
        self.name = name
        self.rpc = rpc
        self.native_token = native_token

class Chains:
    ETHEREUM = Chain(
        name='ethereum',
        rpc='https://1rpc.io/eth',
        native_token='ETH',
    )

    LINEA = Chain(
        name='linea',
        rpc='https://1rpc.io/linea',
        native_token='ETH',
    )

    ARBITRUM_ONE = Chain(
        name='arbitrum_one',
        rpc='https://1rpc.io/arb',
        native_token='ETH',
    )

    BSC = Chain(
        name='bsc',
        rpc='https://1rpc.io/bnb',
        native_token='BNB',
    )

    OP = Chain(
        name='op',
        rpc='https://1rpc.io/op',
        native_token='ETH',
    )
# код пишем тут

chains = [Chains.ETHEREUM, Chains.LINEA, Chains.ARBITRUM_ONE, Chains.BSC, Chains.OP]

target_address = Web3.to_checksum_address('0x...')

with open('keys.txt') as f:
    keys = f.read().splitlines()


for chain in chains:
    w3 = Web3(Web3.HTTPProvider(chain.rpc))
    print(f'Запуск в сети  {chain.name}')
    for key in keys:
        from_address = w3.eth.account.from_key(key).address
        balance_wei = w3.eth.get_balance(from_address)
        # получаeм расход газа в сети и цену газа
        gas = w3.eth.estimate_gas({'from': from_address, 'to': target_address, 'value': 1}) * get_multiplayer()
        gas_price = get_fee(w3, {}).get('maxFeePerGas', w3.eth.gas_price) * get_multiplayer()
        # вычисляем сумму для отправки c учетом оплаты газа
        amount = (balance_wei - (gas * gas_price)) / 10 ** 18
        if amount > 0:
            sent_native_token(key, target_address, amount , chain.rpc)
        else:
            print(f'На кошельке {from_address} нет средств')


