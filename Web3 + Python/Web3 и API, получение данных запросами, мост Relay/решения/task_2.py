

"""
Задание 2  - medium

Скрипт для отправки рандомных токенов из рандомной сети в рандомную сеть на рандомную сумму.
Для работы используются сети Arbitrum, Optimism, Base, Linea.

Напишите скрипт, который выбирает рандомную сеть из списка сетей, подключает w3 к выбранной сети,
выбирает следующую рандомную сеть, которая не равна текущей сети и делает отправку в нее пересылку
токенов.
Для отправки используются токены ETH, USDT, USDC, приоритет отдается стейблкоинам,
если есть оба токена, то выбирается тот у кого больше баланс, если нет стейблкоинов, то отправляется ETH.

Сумма определяется рандомно в пределах баланса токена на кошельке, оставляйте нативный токен
на комиссии.

"""


from random import choice, uniform
import json
import os

from web3 import Web3
from dotenv import load_dotenv

from task_1 import bridge_relay, Token, Tokens, Chains

load_dotenv()



def get_balance(address: str, token: Token, w3: Web3) -> float:
    with open('erc20.json') as f:
        abi = json.load(f)
    contract = w3.eth.contract(token.address, abi=abi)
    balance_wei = contract.functions.balanceOf(address).call()
    return balance_wei / 10 ** token.decimals


def main():
    # берем список сетей
    chains = [Chains.Arbitrum, Chains.Optimism]  # , Chains.Base, Chains.Linea]
    # выбираем рандомную сеть
    from_chain = choice(chains)
    # удаляем выбранную сеть из списка
    chains.remove(from_chain)
    # создаем объект w3 для выбранной сети
    w3 = Web3(Web3.HTTPProvider(from_chain.rpc))
    # выбираем рандомную сеть для пересылки
    to_chain = choice(chains)

    private_key = os.getenv('PK')
    address = w3.eth.account.from_key(private_key).address

    # получаем объекты токенов для выбранной сети
    from_usdt = Tokens.get_token_by_name('USDT', from_chain)
    from_usdc = Tokens.get_token_by_name('USDC', from_chain)

    balances = {
        from_usdt: get_balance(address, from_usdt, w3),
        from_usdc: get_balance(address, from_usdc, w3),
        None: w3.eth.get_balance(address) / 10 ** 18 - 0.001  # нативный токен
    }

    if balances[from_usdt] < 1 and balances[from_usdc] < 1:
        from_token = None  # нативный токен
    else:
        if balances[from_usdt] > balances[from_usdc]:
            from_token = from_usdt
        else:
            from_token = from_usdc

    amount = uniform(0, balances[from_token])

    to_tokens = [
        Tokens.get_token_by_name('USDT', to_chain),
        Tokens.get_token_by_name('USDC', to_chain),
        None  # нативный токен
    ]

    to_token = choice(to_tokens)

    bridge_relay(to_chain, amount, from_token, to_token)


# код пишем тут
