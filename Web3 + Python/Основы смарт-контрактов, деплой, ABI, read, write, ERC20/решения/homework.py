""""""

"""
Задание 1 - easy
Напишите функцию, которая принимает на вход
- rpc_url - адрес провайдера блокчейна
- адрес контракта токена ERC20
- адрес кошелька
- decimals токена

и отправляет при помощи requests запрос к провайдеру через
метод eth_call для получения баланса кошелька в контракте.
Функция должна возвращать баланс кошелька в человекочитаемом виде.

"""

import requests

def get_balance(rpc_url: str, contract_address: str, address: str, decimals: int) -> float:
    response = requests.post(rpc_url, json={
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": contract_address,
            "data": f"0x70a08231000000000000000000000000{address[2:].lower()}"
        }, "latest"],
        "id": 1
    })

    balance = int(response.json()['result'], 16)
    return balance / 10 ** decimals

# код пишем тут

"""
Задание 2  - hard - можно пропустить
Создайте собственный ERC20 токен в сети Ethereum Sepolia.
Добавьте функцию mint(uint256 amount) в контракт токена, которая
будет создавать новые токены и добавлять их на адрес владельца контракта
- totalSupply должен увеличиваться на amount
- баланс вызывающего должен увеличиваться на amount
Функция должна работать только. если вызывающий - владелец контракта.

"""

# файл с контрактом в файле ZarevCoin.sol

# контракт https://sepolia.etherscan.io/address/0x5ca775f0065ea685945f2a665d03a9eadac0192c


# код пишем тут


