import rlp
from web3 import Web3


# что такое смарт-контракт
# как устроен смарт-контракт
# как создать смарт-контракт
# как развернуть смарт-контракт
# как верифицировать смарт-контракт
# как вызвать метод смарт-контракта
# как храниться смарт-контракт

# * Смарт-контракт - это программа / скрипт, код которого прибит гвоздями к блокчейну.

class ContractCalculator:
    total = 0

    def sum(self, a, b):
        self.total = self.total + a + b
        return a + b

    def sub(self, a, b):
        self.total = self.total + a - b
        return a - b

    def mul(self, a, b):
        self.total = self.total + a * b
        return a * b

class Blockchain:
    accounts = {
        '0x00...01': {  # * EOA (обычный кошелёк) 	Externally Owned Account
            'balance': 1000000000000000000,  # * нативный баланс в Wei
            'nonce': 0,  # * количество транзакций отправленных с адреса
        },
        '0x00...02': {  # * контракт (адрес контракта) Contract Account
            'balance': 1000000000000000000,  # * нативный баланс в Wei
            'nonce': 0,  # * количество транзакций отправленных с адреса
            'code': '0x00...00',  # * байт-код контракта
            'storage': {  # * хранилище контракта
                '_balanceOf': {'address': 1000000000000000000},  # * ключ: значение
                'decimals': 6,  # * ключ: значение
                # ...
            },
            'storageRoot': '0x00...00',  # * хэш хранилища
            'codeHash': '0x00...00',  # * хэш байт-кода
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
"""
function name() public view returns (string)
function symbol() public view returns (string)
function decimals() public view returns (uint8)
function totalSupply() public view returns (uint256)
function balanceOf(address _owner) public view returns (uint256 balance)
function transfer(address _to, uint256 _value) public returns (bool success)

function approve(address _spender, uint256 _value) public returns (bool success)
function transferFrom(address _from, address _to, uint256 _value) public returns (bool success)
function allowance(address _owner, address _spender) public view returns (uint256 remaining)

"""
class ERC20:
    _name: str
    _symbol: str
    _decimals: int
    _total_supply: int
    _balances: dict[str, int]
    _allowances: dict[str, dict[str, int]]
    _owner: str

    """
    _allowances = {вася: {петя: 100, коля: 200},
                   игорь: {маша: 50, настя: 150},
                   маша: {вася: 10, петя: 20}}
                   коля: {ирина: 10, софия: 20}}
    
    """

    def __init__(self, owner: str, name: str, symbol: str, decimals: int, total_supply: int):
        self._owner = owner
        self._name = name
        self._symbol = symbol
        self._decimals = decimals
        self._total_supply = total_supply
        self._balances = {
            self._owner: total_supply
        }
        self._allowances = {}

    def name(self):
        return self._name

    def symbol(self):
        return self._symbol

    def decimals(self):
        return self._decimals

    def totalSupply(self):
        return self._total_supply

    def balanceOf(self, address: str):
        return self._balances.get(address, 0)

    def transfer(self, SENDER: str, recipient: str, amount: int):
        if self.balanceOf(SENDER) < amount:
            print('Not enough balance')
            return False

        self._balances[SENDER] -= amount
        self._balances[recipient] = self._balances.get(recipient, 0) + amount
        return True

    def approve(self, SENDER: str, spender: str, amount: int):
        self._allowances[SENDER][spender] = amount
        return True

    def allowance(self, owner: str, spender: str):
        return self._allowances.get(owner, {}).get(spender, 0)

    def transferFrom(self, SENDER: str, owner: str, recipient: str, amount: int):
        if self.allowance(owner, SENDER) < amount:
            print('Not enough allowance')
            return False

        if self.balanceOf(owner) < amount:
            print('Not enough balance')
            return False

        self._balances[owner] -= amount
        self._balances[recipient] = self._balances.get(recipient, 0) + amount
        self._allowances[owner][SENDER] -= amount
        return True



def generage_address_contract(owner: str, nonce: int) -> str:
    address = Web3.to_checksum_address(owner)
    encoded = rlp.encode([bytes.fromhex(address[2:]), nonce])
    contract_address = Web3.keccak(encoded)[12:].hex()
    return '0x' + contract_address

print(generage_address_contract('0x624c222fEd7f88500Afa5021cC760B3106fe34be', 6))

0x3afa7a286bf61b9a59ce4a5ebc856f7333788b6d

def is_contract(address: str):
    """
    Проверка, является ли адрес контрактом
    :param address: адрес контракта
    :return: True, если контракт, иначе False
    """
    w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
    contract_address = w3.to_checksum_address(address)
    code = w3.eth.get_code(contract_address)
    print(code.hex())

is_contract('0x3aFa7A286bF61B9A59ce4A5ebc856F7333788B6d')



def get_signature_func(func_name: str) -> str:
    """
    Создание сигнатуры функции из ее определения
    :param func_name: имя функции и параметры
    :return: сигнатура функции
    """
    return Web3.keccak(text=func_name)[:4].hex()

print(get_signature_func('transfer(address,uint256)'))



def print_storage(contract: str) -> None:
    """
    Получение слота хранилища контракта по ключу
    :param contract: адрес контракта
    :return: None
    """
    w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))

    contract_address = w3.to_checksum_address(contract)

    for slot_index in range(100):
        slot = w3.eth.get_storage_at(contract_address, slot_index).hex()
        print(slot)

print_storage('0x3aFa7A286bF61B9A59ce4A5ebc856F7333788B6d')


def get_balance_from_storage(contract: str, address: str) -> int:
    """
    Получение баланса адреса из хранилища контракта
    :param contract: адрес контракта
    :param address: адрес
    :return: баланс
    """
    w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
    contract_address = w3.to_checksum_address(contract)
    key = w3.to_checksum_address(address)
    key_int = int(key, 16)
    slot = w3.solidity_keccak(['uint256', 'uint256'], [key_int, 5])
    value = w3.eth.get_storage_at(contract_address, slot)
    return int(value.hex(), 16)

print(get_balance_from_storage('0x3aFa7A286bF61B9A59ce4A5ebc856F7333788B6d', '0x624c222fEd7f88500Afa5021cC760B3106fe34be'))