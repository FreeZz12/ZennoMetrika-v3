import json
from web3 import Web3
from solcx import compile_standard, install_solc


from dotenv import load_dotenv
import os

load_dotenv()

pk = os.getenv("pk")

# Устанавливаем нужную версию компилятора Solidity
install_solc("0.8.0")

# Читаем исходный код контракта
with open("ZarevCoin.sol", "r") as file:
    contract_source_code = file.read()

# Компилируем контракт
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ZarevCoin.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

# Извлекаем ABI и байткод
contract_interface = compiled_sol["contracts"]["ZarevCoin.sol"]["ERC20"]
abi = contract_interface["abi"]
bytecode = contract_interface["evm"]["bytecode"]["object"]

# Подключаемся к Ethereum ноде (например, локальный Ganache или тестовая сеть)
w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
if not w3.is_connected():
    raise Exception("Не удалось подключиться к ноде!")

# Создаем объект контракта
ZarevCoin = w3.eth.contract(abi=abi, bytecode=bytecode)

address = w3.eth.account.from_key(pk).address

# Строим транзакцию для деплоя
transaction = ZarevCoin.constructor(
"ZarevCoin", "ZVC", 18, 1000000*10**18
).build_transaction({
    "chainId": w3.eth.chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": address,
    "nonce": w3.eth.get_transaction_count(address),
})

# Подписываем транзакцию
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=pk)

# Отправляем транзакцию
tx_hash = w3.eth.send_raw_transaction(signed_txn['raw_transaction'])
print("Транзакция отправлена, хэш:", tx_hash.hex())

# Ожидаем подтверждения транзакции
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Контракт задеплоен по адресу:", tx_receipt['contractAddress'])