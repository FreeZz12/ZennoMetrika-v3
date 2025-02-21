""""""

"""
Задание 1 - easy

Напишите самостоятельно функцию
allowance(owner: str, spender: str, token: str, w3: Web3) -> int,
которая принимает:
- owner: str - адрес владельца токена
- spender: str - адрес того, кому разрешено тратить токены
- token: str  - адрес контракта токена
- w3: Web3 - объект w3

функция должна возвращать количество токенов, которое spender может потратить от owner.


"""
import json

from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider('https://1rpc.io/arb'))

def allowance(owner: str, spender: str, token: str, w3: Web3) -> int:
    token = w3.to_checksum_address(token)
    owner = w3.to_checksum_address(owner)
    spender = w3.to_checksum_address(spender)
    with open('erc20.json') as f:
        abi = json.loads(f.read())
    contract = w3.eth.contract(address=token, abi=abi)
    return contract.functions.allowance(owner, spender).call()

# код пишем тут

"""
Задание 2  - medium

Напишите самостоятельно функцию approve(amount: float, spender: str, token: str, pk: str, w3: Web3) -> str,
которая принимает:
- amount: float - количество токенов для разрешения траты
- spender: str - адрес того, кому разрешено тратить токены
- token: str  - адрес контракта токена
- pk: str - приватный ключ
- w3: Web3 - объект w3

Функция должна разрешить spender тратить amount токенов от вашего адреса.

"""
import json

from web3 import Web3


def get_fee(tx_params: dict, w3: Web3) -> dict:
    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    return tx_params


def approve(amount: float, spender: str, token: str, pk: str, w3: Web3) -> str:
    address = w3.eth.account.from_key(pk).address
    token = w3.to_checksum_address(token)
    spender = w3.to_checksum_address(spender)
    with open('erc20.json') as f:
        abi = json.loads(f.read())
    contract = w3.eth.contract(address=token, abi=abi)

    tx_params = {
        'chainId': w3.eth.chain_id,
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
    }

    tx = contract.functions.approve(spender, amount).build_transaction(tx_params)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f'Апрув {tx_hash.hex()} отправлен, в блокчейне {w3.eth.chain_id}, токен {contract.functions.symbol().call()} amount: {amount}')
    return tx_hash.hex()

# код пишем тут


"""
Задание 3 - HARD - нужно будет попотеть.

Напишите скрипт, который очищает все выданные апрувы по всем токенам в любой EVM сети.
Как получить список апрувов, которые были выданы?
Можно использовать 2 конечных точки etherscan API:

1. Get a list of 'Normal' Transactions By Address - https://docs.etherscan.io/etherscan-v2/api-endpoints/accounts
Запрос на получение всех транзакций по адресу отправителя.
Делаете запрос из полученных данных можно найти все транзакции с методом approve, у данных
транзакций можно получить to - это адрес токена, а в input (data) - можно извлечь spender.
Например input: 0x095ea7b30000000000000000000000007b3579c8bffe6c8c19ff06de9e54fd1da8cebfb600000000000019ac878c348b192174a2349667d4591dfc51f408a9f3b79347dd
7b3579c8bffe6c8c19ff06de9e54fd1da8cebfb6 - это адрес spender (вспоминайте ABI кодирование поля data в транзакции)
Собрав все адреса spender и адреса токенов, можно сделать запрос к контрактам токенов и получить allowance(owner, spender) 

2. Get Event Logs by Topics - https://docs.etherscan.io/etherscan-v2/api-endpoints/logs
При выполнении транзакции апрува, генерируется событие Approval(address indexed owner, address indexed spender, uint256 value)
в системе логирования блокчейна.
Пример лога: https://etherscan.io/tx/0xdd5a3240fa4bd34cb8475a16b071d48672536b7f5e51b961a23ba025573fbc02#eventlog
В логах есть параметры для будущей фильтрации, которые называются топиками.
Address - это адрес контракта токена
Topics 0 - это хэш функции keccak256 от строки "Approval(address,address,uint256)" 0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925
Topics 1 - это адрес владельца токена дополненный нулями слева до 64 символов
Topics 2 - это адрес spender дополненный нулями слева до 64 символов
Можно получить все логи событий Approval(address,address,uint256), отфильтрованные
по адресу отправителя транзакции.
Для этого нужно отправить запрос в etherscan API с параметрами:
topic0= 0xХеш функции keccak256 от строки "Approval(address,address,uint256)"
topic0_1= and # указание что будет дополнительный параметр фильтрации
topic1= 0xАдрес владельца токена дополненный нулями слева до 64 символов
!!! поле address в запросе это адрес контракта токена, если вы хотите получить все логи по всем токенам, то
параметр address можно не указывать.
Из полученных данных можно извлечь адреса токенов и адреса spender, кому давали апрувы.
После получения всех адресов токенов и spender, можно сделать запрос к контрактам токенов и получить allowance(owner, spender)

После сбора всех данных, нужно сделать запрос к контрактам токенов кому выданы апрувы и 
отправить транзакцию approve(0, spender, token)


Напишите скрипт, который берет приватные из текстового файла, ищет для каждого адреса все апрувы и отменяет их.
Скрипт должен работать сетях Arbitrum, Optimism и Binance Smart Chain,
скрипт должен удалять апрувы всех ERC20 токенов, которые генерируют событие Approval(address,address,uint256)

"""
import os

from dotenv import load_dotenv
import requests

load_dotenv()

ETHERSCAN_API = os.getenv('ETHERSCAN_API')

class ApproveTx:
    """
    Класс для хранения информации о транзакции апрува
    """
    def __init__(self, spender: str, token: str):
        self.spender = spender
        self.token = token

    def __hash__(self):
        """
        Переопределение метода для хеширования объекта, чтобы можно было использовать его в множестве
        """
        return hash((self.spender, self.token))

def get_approve_logs(address: str, chain_id: int) -> list:
    """
    Получение логов Approval(address,address,uint256) по адресу отправителя
    :param address: адрес отправителя
    :param chain_id: id сети
    :return: список логов
    """
    url = f'https://api.etherscan.io/v2/api'
    params = {
        'chainid': chain_id,
        'module': 'logs',
        'action': 'getLogs',
        'fromBlock': 0,
        'toBlock': 'latest',
        'topic0': '0x' + w3.keccak(text='Approval(address,address,uint256)').hex(), # хеш функции keccak256 от строки "Approval(address,address,uint256)"
        'topic0_1': 'and', # указание что будет дополнительный параметр фильтрации
        'topic1': '0x' + address[2:].rjust(64, '0'), # адрес владельца токена дополненный нулями слева до 64 символов
        'apikey': ETHERSCAN_API,
    }
    response = requests.get(url, params=params)
    return response.json()['result']


def remove_approve(pk: str,  w3: Web3):
    """
    Отмена апрува
    :param pk: приватный ключ
    :param w3: объект w3
    """
    address = w3.eth.account.from_key(pk).address
    approve_logs = get_approve_logs(address, w3.eth.chain_id)
    approved = set()

    # получение всех апрувов для адреса
    for log in approve_logs:
        token = log.get('address')
        spender = '0x' + log.get('topics')[2][26:]  # адрес spender
        approve_tx = ApproveTx(spender, token)
        approved.add(approve_tx)

    for approve_tx in approved:

        # получение суммы апрува на токены
        allowances_amount = allowance(address, approve_tx.spender, approve_tx.token, w3)
        # если апрува нет, то пропускаем
        if not allowances_amount:
            continue

        print(
            f'Owner: {address}, Spender: {approve_tx.spender}, Token: {approve_tx.token}, Allowance: {allowances_amount}')
        # отправка транзакции апрува c 0 токенов (обнуляем)
        approve(0, approve_tx.spender, approve_tx.token, pk, w3)


chains = ['arb' , 'op', 'bnb']

with open('private_keys.txt') as f:
    private_keys = f.read().splitlines()

for pk in private_keys:
    for chain in chains:
        # инициализация объекта w3 для каждой сети
        w3 = Web3(Web3.HTTPProvider(f'https://1rpc.io/{chain}'))
        remove_approve(pk, w3)


# код пишем тут

