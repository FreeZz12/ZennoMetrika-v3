""""""

"""
Задание 0 - easy
Выберите 2 RPC провайдера, зарегистрируйтесь на них и персональные RPC URL.
Например: 1rpc и ankr
"""

# код пишем тут


"""
Задание 1 - easy

Напишите скрипт, который будет подключаться к RPC провайдеру и проверять подключение.
Скрипт должен делать запросы используя прокси и headers с указанием поддельного User-Agent и Content-Type.
Соберите конструкцию подключения к RPC провайдеру своими руками без копипаста конспекта,
с правильным указанием headers и прокси. Проверьте работоспособность скрипта.
w3.is_connected() должен возвращать True.
Не присылайте реальные прокси вмесие с решением, подмените выдуманными данными.
"""

from web3 import Web3, HTTPProvider

request_kwargs = {
    'proxies': {
        'http': 'http://user:password@proxy:port',
        'https': 'http://user:password@proxy:port',
    },
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/json',
    }}

w3 = Web3(HTTPProvider('https://1rpc.io/eth', request_kwargs=request_kwargs))
print(w3.is_connected())


"""
Задание 2  - medium
Создайте класс-модель Chain, в котором будут атрибуты:
- name (название сети)
- rpc_url (url RPC провайдера)
- native_token (название нативного токена)

Создайте класс хранилище Chains, который будет хранить список объектов Chain.
Создайте объекты сетей для сетей:
- Binance Smart Chain
- Ethereum
- Polygon
- Arbitrum One
- Optimism

Напишите скрипт, который будет проверять доступность RPC провайдера для каждой сети.
Скрипт должен в цикле перебрать все сети и проверить доступность RPC провайдера.

* Для удобства в класс Chains можете добавить метод класса, который будет возвращать список всех сетей.

"""

class Chain:
    def __init__(self, name, rpc_url, native_token):
        self.name = name
        self.rpc_url = rpc_url
        self.native_token = native_token

class Chains:

    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH')
    Binance_Smart_Chain = Chain('Binance Smart Chain', 'https://1rpc.io/bnb', 'BNB')
    Polygon = Chain('Polygon', 'https://1rpc.io/matic', 'MATIC')
    Arbitrum_One = Chain('Arbitrum One', 'https://1rpc.io/arb', 'ETH')
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH')

    @classmethod
    def get_chains(cls) -> list[Chain]:
        """
        Возвращает список всех сетей
        :return: list[Chain]
        """
        chains = []
        for chain in cls.__dict__:
            if isinstance(cls.__dict__[chain], Chain):
                chains.append(cls.__dict__[chain])
        return chains


chains = Chains.get_chains()
for chain in chains:
    w3 = Web3(HTTPProvider(chain.rpc_url))
    print(f'Проверяем сеть: {chain.name}')
    print(w3.is_connected())
    print()


# код пишем тут

"""
Задание 3 - hard
Напишите скрипт, который будет извлекать кошельки из файла wallets.txt и проверять 
баланс нативного токена во всех сетях из задания 2.
Скрипт должен выводить баланс нативного токена для каждой сети.
Для проверки баланса используйте метод w3.eth.get_balance(address) из библиотеки web3.py.
Для исключения ошибок перед запросом баланса пропустите адрес через метод address = w3.to_checksum_address(address),
это необходимо для приведения адреса к правильному формату.
Для конвертации баланса в человекочитаемый вид используйте метод w3.from_wei(balance, 'ether') или
поделите полученное значение на 10 ** 18. (balance = balance_wei / 10 ** 18)

Вывод скрипта должен быть в формате:
Проверяем кошелек: 0x1234567890
-- Binance Smart Chain: 0.11 BNB
-- Ethereum: 0.22 ETH
-- Polygon: 0.33 MATIC
-- Arbitrum One: 0.44 ETH
-- Optimism: 0.55 ETH

и так далее для всех кошельков из файла wallets.txt

"""

with open('wallets.txt') as f:
    wallets = f.read().splitlines()

for address in wallets:
    print(f'Проверяем кошелек: {address}')
    for chain in chains:
        w3 = Web3(HTTPProvider(chain.rpc_url))
        address = w3.to_checksum_address(address)
        balance = w3.eth.get_balance(address)
        balance = w3.from_wei(balance, 'ether')
        print(f'-- {chain.name}: {balance} {chain.native_token}')
    print()
