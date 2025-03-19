from web3 import Web3

from config import config
from chains import Chains
from tokens import Tokens
from stargate import bridge



"""
Задание 1 - easy
Написать скрипт для отправки USDC токена из сети Arbitrum в сеть Optimism через мост Stargate.

* оставляйте параметры extraOptions=0x, composeMsg=0x, oftCmd=0x01 по умолчанию как в уроке

"""

def main():
    from_chain = Chains.Arbitrum
    to_chain = Chains.Optimism
    token = Tokens.get_token_by_name('USDC', from_chain)
    w3 = Web3(Web3.HTTPProvider(from_chain.rpc))
    w3.eth.default_account = w3.eth.account.from_key(config.private_key).address
    bridge(w3, config.private_key, from_chain=from_chain, to_chain=to_chain, amount=1, token=token)



if __name__ == '__main__':
    main()
