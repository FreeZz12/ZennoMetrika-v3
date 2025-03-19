import random
import time

import requests
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from web3._utils.contracts import decode_transaction_data

from amount import Amount
from chains import Chains, Chain
from tokens import Tokens, Token, TokenType
from stargate import bridge, Contracts
from utils import get_list_from_file, get_abi, get_token_price_from_binance
from config import config

"""

Задание 3 - hard
Доработайте предыдущий скрипт, чтобы он проверял объем отправленных токенов через мост Stargate за
последний месяц и не отправлял больше 5000$ в месяц. (учитывает USDT, USDC и нативный токен) во всех
сетях. 
Данные должны браться из блокчейна перед запуском аккаунта. Если объем уже больше 5000$, то
аккаунт пропускается.
 Используйте API Etherscan или ankr.
"""
chains = [Chains.Arbitrum, Chains.Optimism, Chains.BASE, Chains.LINEA]


def get_volume(address: str) -> float:
    """
    Получает объем отправленных токенов через мост Stargate за последний месяц
    :param account: аккаунт
    :param chain: сеть
    :return: объем в $
    """
    url = 'https://rpc.ankr.com/multichain/' + config.ankr_api_key
    body = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "ankr_getTransactionsByAddress",
        "params": {
            "blockchain": ["arbitrum", "optimism", "base", "linea"],
            "address": address,
            "fromTimestamp": int(time.time()) - 30 * 24 * 60 * 60,
            "toTimestamp": int(time.time()),
            "sort": "desc"
        }
    }
    response = requests.post(url, json=body)
    response.raise_for_status()
    data = response.json()
    transactions = data['result']['transactions']
    print(len(transactions))
    native_contracts = [
        Contracts.stargate_pool_native_op,
        Contracts.stargate_pool_native_arb,
        Contracts.stargate_pool_native_base, # todo добавить контракт
        Contracts.stargate_pool_native_linea # todo добавить контракт
        ]
    stable_contracts = [
        Contracts.stargate_pool_usdt_op,
        Contracts.stargate_pool_usdt_arb,
        Contracts.stargate_pool_usdt_base, # todo добавить контракт
        Contracts.stargate_pool_usdt_linea, # todo добавить контракт
        Contracts.stargate_pool_usdc_op,
        Contracts.stargate_pool_usdc_arb,
        Contracts.stargate_pool_usdc_base, # todo добавить контракт
        Contracts.stargate_pool_usdc_linea # todo добавить контракт
        ]
    native_contracts = [contract.address.lower() for contract in native_contracts]
    stable_contracts = [contract.address.lower() for contract in stable_contracts]
    volume = 0
    contract = Web3().eth.contract(address=Contracts.stargate_pool_usdt_op.address, abi=get_abi(Contracts.stargate_pool_usdt_op.name))
    fn_abi = contract.functions.send.abi
    for transaction in transactions:
        if transaction['to'].lower() in native_contracts:
            amount = int(transaction['value'], 16) / 1e18  * get_cached_eth_price()
            volume += amount
        elif transaction['to'].lower() in stable_contracts:
            input_data = decode_transaction_data(fn_abi, transaction['input'])
            amount = input_data['_sendParam']['amountLD'] / 1e6
            volume += amount
    return volume



def get_cached_eth_price(max_age=3600):
    current_time = time.time()

    if not hasattr(get_cached_eth_price, "price") or \
            not hasattr(get_cached_eth_price, "last_update") or \
            current_time - get_cached_eth_price.last_update > max_age:
        get_cached_eth_price.price = get_token_price_from_binance('ETH')
        get_cached_eth_price.last_update = current_time
        print(f"ETH price updated: ${get_cached_eth_price.price}")

    return get_cached_eth_price.price


class TokenWithBalance:
    def __init__(self, token: Token, amount: Amount):
        self.token = token
        self.amount = amount
        match token.token_type:
            case TokenType.STABLE:
                self.usd_balance = amount.ether
            case TokenType.NATIVE:
                self.usd_balance = amount.ether * get_cached_eth_price()
            case TokenType.ERC20:
                self.usd_balance = -1


def get_balance(w3: Web3, token: Token) -> Amount:
    if token.token_type != TokenType.NATIVE:
        token_contract = w3.eth.contract(address=token.address, abi=get_abi('erc20'))
        balance = token_contract.functions.balanceOf(w3.eth.default_account).call()
        return Amount(balance, token.decimals)
    else:
        return Amount(w3.eth.get_balance(w3.eth.default_account))


def check_balances(account: LocalAccount, chain: Chain) -> list[TokenWithBalance]:
    w3 = Web3(HTTPProvider(chain.rpc))
    w3.eth.default_account = account.address
    tokens = [Tokens.get_token_by_name('USDC', chain),
              Tokens.get_token_by_name('USDT', chain),
              Tokens.get_native(chain)]
    balances = []
    for token in tokens:
        balance = get_balance(w3, token)
        balances.append(TokenWithBalance(token, balance))

    return balances

def select_token_with_balance(tokens_with_balances: list[TokenWithBalance]) -> TokenWithBalance:
    stables = list(filter(lambda twb: twb.usd_balance > 10 and twb.token.token_type == TokenType.STABLE, tokens_with_balances))
    if len(stables) == 2:
        return max(stables, key=lambda twb: twb.usd_balance)
    elif len(stables) == 1:
        return stables[0]
    else:
        return list(filter(lambda twb: twb.token.token_type == TokenType.NATIVE, tokens_with_balances))[0]



def worker(private_key: str) -> bool:
    account = Account.from_key(private_key)
    volume = get_volume(account.address)
    if volume > 5000:
        print(f'Объем отправленных токенов {volume} больше 5000$ за месяц, аккаунт пропускается')
        return False
    random.shuffle(chains)
    for chain in chains:
        tokens_with_balances = check_balances(account, chain)
        if not any([token_with_balance.usd_balance > 10 for token_with_balance in tokens_with_balances]):
            continue
        to_chain = random.choice([c for c in chains if c != chain])
        token_with_balance = select_token_with_balance(tokens_with_balances)
        w3 = Web3(HTTPProvider(chain.rpc))
        if token_with_balance.token.token_type == TokenType.NATIVE:
            fee = random.uniform(3, 5) / get_cached_eth_price()
            amount = token_with_balance.amount.ether - fee
            bridge(w3, private_key, chain, to_chain, amount)
        else:
            token = token_with_balance.token
            amount = token_with_balance.amount
            bridge(w3, private_key, chain, to_chain, amount, token)
        return True
    else:
        print(f'На аккаунте {account.address} нет токенов для отправки')
        return False




def main():
    private_keys = get_list_from_file('private_keys.txt')
    while True:
        random.shuffle(private_keys)
        for private_key in private_keys:
            status = worker(private_key)
            if status:
                time.sleep(random.randint(5, 10) * 60)


if __name__ == '__main__':
    main()

