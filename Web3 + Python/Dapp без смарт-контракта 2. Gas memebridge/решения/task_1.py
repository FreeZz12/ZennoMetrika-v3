import random

import requests
from eth_account import Account
from web3 import Web3

from config import config
from chains import Chains, Chain
from amount import Amount
from tokens import Tokens
from utils import get_tx_params, get_abi, get_fee, sing_send_tx


def get_gas_data(*chains: Chain):
    target_chains_id = [str(chain.chain_id) for chain in chains]

    url = 'https://gas.memebridge.app/api/v1/chainInfo'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    meme_chains_id = ''
    manager = None
    meme_chains = data['data']['to']
    random.shuffle(meme_chains)

    for meme_chain in meme_chains:
        if meme_chain['chainID'] in target_chains_id:
            if manager is None:
                manager = meme_chain['manager']
            if manager != meme_chain['manager']:
                raise ValueError('Manager address is different')
            meme_chains_id += hex(meme_chain['id'])[2:]

    if len(meme_chains_id) / 2 != len(chains):
        raise ValueError('Chains count is different')

    input_data = '0x1' + hex(len(chains))[2:] + meme_chains_id
    return manager, input_data


def get_eth_price():
    url = 'https://gas.memebridge.app/api/v1/tokenPrice'
    response = requests.get(url)
    response.raise_for_status()
    return float(response.json()['data']['tokenPrice']['ETH'])


def send_gas(w3: Web3, amount_usdt: int, *chains: Chain):
    '''
    :param amount: Количество токенов в USDT
    '''
    total_amount_in_usdt = amount_usdt * len(chains)
    eth_price = get_eth_price()
    amount_eth = Amount(total_amount_in_usdt / eth_price)

    manager, input_data = get_gas_data(*chains)

    rounded_fee = '000100000000'
    rounded_amount = int(str(amount_eth.wei)[:-len(rounded_fee)] + rounded_fee)

    tx_params = get_tx_params(
        w3,
        to=manager,
        data=input_data,
        value=rounded_amount
    )
    tx_params.update(get_fee(w3))
    tx_params['gas'] = w3.eth.estimate_gas(tx_params)
    tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    print(f'Tx hash: {tx_hash}')
    return tx_hash


def get_balance(chain: Chain, address: str) -> int:
    address = Web3.to_checksum_address(address)
    return Web3(Web3.HTTPProvider(chain.rpc)).eth.get_balance(address)


def main():
    account = Account.from_key(config.private_key)
    min_balance = Amount(3)
    monad_balance = get_balance(Chains.MONAD, account.address)
    if monad_balance > min_balance.wei:
        print('Not enough balance')
        return

    chains = [
        Chains.Arbitrum,
        Chains.Optimism,
        Chains.BASE,
        Chains.LINEA
    ]

    selected_chain = max(chains, key=lambda chain: get_balance(chain, account.address))
    print(f'Выбрали сеть: {selected_chain.name}')
    w3 = Web3(Web3.HTTPProvider(selected_chain.rpc))
    w3.eth.default_account = account.address
    amount_usd = random.choice([1, 3, 5])
    send_gas(w3, amount_usd, Chains.MONAD)



if __name__ == '__main__':
    main()
