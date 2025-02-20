import os
import json
import random

from eth_utils import keccak
from web3 import Web3
from dotenv import load_dotenv
from web3.contract.contract import ContractFunctions

load_dotenv()

# метод send_raw_transaction
# упаковка и отправка транзакции перевода ERC20 токенов
# write функции контракта
# encode_abi, build_transaction
# объединение с функцией отправки нативного токена
# класс Onchain
# классы Amount, Chain, Chains, Token, Tokens


"""
0xa9059cbb
000000000000000000000000624c222fed7f88500afa5021cc760b3106fe34be
00000000000000000000000000000000000000000000000000000000000186a0

0xa9059cbb
000000000000000000000000624c222fEd7f88500Afa5021cC760B3106fe34be
00000000000000000000000000000000000000000000000000000000000186a0


"""


class Token:
    def __init__(self, name: str, address: str, decimals: int):
        self.name = name
        self.address = address
        self.decimals = decimals


class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6)


def send_erc20_token_manual():
    private_key = os.getenv('PK')

    # optimism
    rpc = 'https://1rpc.io/op'

    w3 = Web3(Web3.HTTPProvider(rpc))
    from_address = w3.eth.account.from_key(private_key).address
    to_address = from_address

    # usdt op
    token_contract_address = w3.to_checksum_address('0x94b008aA00579c1307B0EF2c499aD98a8ce58e58')

    function = keccak(b'transfer(address,uint256)').hex()[:8]
    to_address = to_address[2:].rjust(64, '0')
    amount_wei = int(0.1 * 10 ** 6)
    amount_hex = hex(amount_wei)[2:].rjust(64, '0')
    data = '0x' + function + to_address + amount_hex
    print(data)

    tx_params = {
        'nonce': w3.eth.get_transaction_count(from_address),
        'from': from_address,
        'to': token_contract_address,
        'data': data,
        'chainId': w3.eth.chain_id,
    }

    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    tx_params['gas'] = w3.eth.estimate_gas(tx_params)

    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    w3.eth.wait_for_transaction_receipt(tx_hash)

    print(tx_hash.hex())
    return tx_hash.hex()


def send_erc20_token_encode_abi():
    private_key = os.getenv('PK')

    # optimism
    rpc = 'https://1rpc.io/op'

    w3 = Web3(Web3.HTTPProvider(rpc))
    from_address = w3.eth.account.from_key(private_key).address
    to_address = from_address

    token_contract_address = w3.to_checksum_address('0x94b008aA00579c1307B0EF2c499aD98a8ce58e58')

    abi = [
        {
            "inputs": [
                {
                    "internalType": "address",
                    "name": "recipient",
                    "type": "address"
                },
                {
                    "internalType": "uint256",
                    "name": "amount",
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
        },
    ]

    contract = w3.eth.contract(address=token_contract_address, abi=abi)

    amount_wei = int(0.1 * 10 ** 6)

    data = contract.encode_abi('transfer', [to_address, amount_wei])

    tx_params = {
        'nonce': w3.eth.get_transaction_count(from_address),
        'from': from_address,
        'to': token_contract_address,
        'chainId': w3.eth.chain_id,
        'data': data,
    }

    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    tx_params['gas'] = w3.eth.estimate_gas(tx_params)

    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    w3.eth.wait_for_transaction_receipt(tx_hash)

    print(tx_hash.hex())
    return tx_hash.hex()


def get_abi(path: str):
    with open(path) as f:
        return json.loads(f.read())


def get_fee(tx_params: dict, w3: Web3) -> dict:
    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    return tx_params


def send_erc20_token(token: Token | str, amount: float, to_address: str) -> str:
    if isinstance(token, Token):
        contract_address = token.address
    else:
        contract_address = token

    # извлекаем приватный ключ из переменной окружения
    private_key = os.getenv('PK')

    # подключаемся к провайдеру
    rpc = 'https://1rpc.io/op'
    w3 = Web3(Web3.HTTPProvider(rpc))

    # извлекаем адрес кошелька из приватного ключа
    from_address = w3.eth.account.from_key(private_key).address
    # приводим адрес кошелька к формату checksum
    token_contract_address = w3.to_checksum_address(contract_address)
    # загружаем ABI ERC20 токена
    abi = get_abi('erc20.json')
    # создаем объект контракта ERC20 токена
    contract = w3.eth.contract(address=token_contract_address, abi=abi)
    contract.encode_abi()

    if isinstance(token, Token):
        decimals = token.decimals
    else:
        decimals = contract.functions.decimals().call()

    # переводим количество токенов в wei
    amount_wei = int(amount * 10 ** decimals)

    # подготавливаем транзакцию
    tx_params = {
        'nonce': w3.eth.get_transaction_count(from_address),
        'from': from_address,
        'chainId': w3.eth.chain_id,
    }
    # вызываем функцию и объединяем с параметрами
    tx_params = contract.functions.transfer(to_address, amount_wei).build_transaction(tx_params)

    # получаем историю комиссий
    tx_params = get_fee(tx_params, w3)

    if tx_params.get('gas') is None:
        tx_params['gas'] = w3.eth.estimate_gas(tx_params)

    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
    w3.eth.wait_for_transaction_receipt(tx_hash)

    print(tx_hash.hex())
    return tx_hash.hex()


def decode_and_print_raw_tx(raw_tx: str):
    import rlp
    from rlp.sedes import big_endian_int, Binary, binary, CountableList, List
    from eth_keys.datatypes import Signature
    from eth_utils import keccak, decode_hex

    # Класс для legacy транзакций (9 полей)
    class LegacyTransaction(rlp.Serializable):
        fields = [
            ('nonce', big_endian_int),
            ('gasPrice', big_endian_int),
            ('gas', big_endian_int),
            ('to', Binary.fixed_length(20, allow_empty=True)),  # может быть пустым (создание контракта)
            ('value', big_endian_int),
            ('data', binary),
            ('v', big_endian_int),
            ('r', big_endian_int),
            ('s', big_endian_int)
        ]

    # Класс для EIP-1559 транзакций (12 полей)
    class EIP1559Transaction(rlp.Serializable):
        fields = [
            ('chainId', big_endian_int),
            ('nonce', big_endian_int),
            ('maxPriorityFeePerGas', big_endian_int),
            ('maxFeePerGas', big_endian_int),
            ('gasLimit', big_endian_int),
            ('to', Binary.fixed_length(20, allow_empty=True)),
            ('value', big_endian_int),
            ('data', binary),
            # accessList – список, где каждый элемент: [address, [storageKey1, storageKey2, ...]]
            ('accessList', CountableList(List([binary, CountableList(binary)]))),
            ('v', big_endian_int),
            ('r', big_endian_int),
            ('s', big_endian_int)
        ]

    def decode_transaction(raw_tx):
        raw_tx_bytes = decode_hex(raw_tx)
        # Если первый байт равен 0x01 или 0x02, то это типизированная транзакция
        if raw_tx_bytes[0] in (1, 2):
            tx_type = raw_tx_bytes[0]
            payload = raw_tx_bytes[1:]
        else:
            tx_type = None
            payload = raw_tx_bytes

        # Декодируем RLP-полезную нагрузку, чтобы понять число элементов
        decoded_list = rlp.decode(payload, strict=False)
        if isinstance(decoded_list, list):
            if len(decoded_list) == 9:
                tx = rlp.decode(payload, LegacyTransaction)
                return tx, 'legacy', tx_type
            elif len(decoded_list) == 12:
                tx = rlp.decode(payload, EIP1559Transaction)
                return tx, 'eip1559', tx_type
            else:
                raise Exception(f"Неожиданное количество полей: {len(decoded_list)}")
        else:
            raise Exception("Невозможно декодировать транзакцию как список")

    tx, tx_type_name, tx_type_byte = decode_transaction(raw_tx)
    print("Тип транзакции:", tx_type_name)

    # Восстановление подписи и вычисление хэша подписываемых данных
    if tx_type_name == 'legacy':
        # Если v == 27 или 28 – обычная legacy транзакция
        if tx.v in (27, 28):
            recovery_id = tx.v - 27
            unsigned_tx = rlp.encode([tx.nonce, tx.gasPrice, tx.gas, tx.to, tx.value, tx.data])
        else:
            # EIP-155: v = chain_id * 2 + 35 или 36
            chain_id = (tx.v - 35) // 2
            recovery_id = tx.v - (chain_id * 2 + 35)
            unsigned_tx = rlp.encode([
                tx.nonce, tx.gasPrice, tx.gas, tx.to, tx.value, tx.data,
                chain_id, 0, 0
            ])
        msg_hash = keccak(unsigned_tx)
    elif tx_type_name == 'eip1559':
        # Для EIP-1559 подписываемые данные формируются как:
        # unsigned_payload = rlp.encode([chainId, nonce, maxPriorityFeePerGas, maxFeePerGas, gasLimit, to, value, data, accessList])
        unsigned_payload = rlp.encode([
            tx.chainId,
            tx.nonce,
            tx.maxPriorityFeePerGas,
            tx.maxFeePerGas,
            tx.gasLimit,
            tx.to,
            tx.value,
            tx.data,
            tx.accessList
        ])
        # unsigned транзакция – это типовой байт (0x02) + unsigned_payload
        unsigned_tx = bytes([2]) + unsigned_payload
        msg_hash = keccak(unsigned_tx)
        # В EIP-1559 v обычно равен 0 или 1
        recovery_id = tx.v
    else:
        raise Exception("Неизвестный тип транзакции")

    def public_key_to_address(pub_key_bytes: bytes) -> str:
        # Если ключ начинается с 0x04, отбросим его
        if pub_key_bytes[0] == 4:
            pub_key_bytes = pub_key_bytes[1:]
        # Вычисляем Keccak-256 хэш
        hash_bytes = keccak(pub_key_bytes)
        # Адрес — последние 20 байт хэша
        raw_address = hash_bytes[-20:]
        # Приводим к формату с контрольной суммой
        return raw_address.hex()

    # Восстанавливаем публичный ключ из подписи
    sig = Signature(vrs=(recovery_id, tx.r, tx.s))
    pub_key = sig.recover_public_key_from_msg_hash(msg_hash)
    print("Публичный ключ (hex):", pub_key.to_hex())
    print("Адрес (hex):", public_key_to_address(pub_key.to_bytes()))
    print(f'chainId: {tx.chainId},')
    print(f'nonce: {tx.nonce},')
    print(f'maxPriorityFeePerGas: {tx.maxPriorityFeePerGas},')
    print(f'maxFeePerGas: {tx.maxFeePerGas},')
    print(f'gasLimit: {tx.gasLimit},')
    print(f'to: {tx.to.hex()},')
    print(f'value: {tx.value},')
    print(f'data: {tx.data.hex()},')
    print(f'accessList: {tx.accessList}')
    print(f'v: {tx.v},')
    print(f'r: {tx.r},')
    print(f's: {tx.s}')


class Chain:
    def __init__(self, name: str, rpc: str, native_token: str, multiplier: float = 1.0):
        self.name = name
        self.rpc = rpc
        self.native_token = native_token
        self.multiplier = multiplier


class Chains:
    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH')
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH')
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH')
    BSC = Chain('BSC', 'https://1rpc.io/bnb', 'BNB')
    LINEA = Chain('LINEA', 'https://1rpc.io/linea', 'ETH', 1.3)


class Onchain:

    def __init__(self, chain: Chain, private_key: str):
        self.chain = chain
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(chain.rpc))
        self.address = self.w3.eth.account.from_key(private_key).address

    def _get_abi(self, path: str):
        with open(path) as f:
            return json.loads(f.read())

    def _get_multiplier(self, min_mult: float = 1.03, max_mult: float = 1.1) -> float:
        return random.uniform(min_mult, max_mult)

    def get_fee(self, tx_params: dict) -> dict:
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

    def send_token(self, amount: float, to_address: str, token: Token | str | None  = None) -> str:

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


if __name__ == '__main__':
    # decode_and_print_raw_tx('0x02f8ad0a26830186a083018d5a8276559494b008aa00579c1307b0ef2c499ad98a8ce58e5880b844a9059cbb000000000000000000000000624c222fed7f88500afa5021cc760b3106fe34be00000000000000000000000000000000000000000000000000000000000186a0c001a0dd176c6e3f9e9521c0499dfe371bcf920d77383a555d04d9f50b49ea01479bc9a063573fbc0327c4dea7f03e6a838b0de914cbff2b020d712a30540757a7c4afde')
    # send_erc20_token(Tokens.USDT_OP, 0.1, '0x624c222fEd7f88500Afa5021cC760B3106fe34be')
    private_key = os.getenv('PK')

    onchain = Onchain(Chains.Optimism, private_key)

    onchain.send_token(0.1, '0x624c222fEd7f88500Afa5021cC760B3106fe34be', Tokens.USDC_OP)
    onchain.send_token(0.0001, '0x624c222fEd7f88500Afa5021cC760B3106fe34be')
