import random

from web3 import Web3
import requests

from config import config
from chains import Chains, Chain
from amount import Amount
from tokens import Tokens
from utils import get_tx_params, get_fee, sing_send_tx, get_token_price_from_binance, get_abi

work_chain = Chains.Arbitrum
w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
account = w3.eth.account.from_key(config.private_key)
w3.eth.default_account = account.address


def get_bridge_data(to_chain: Chain) -> tuple[str, str, Amount]:
    url = 'https://api.memebridge.app/api/v1/NetworkFee'
    params = dict(
        addr=account.address,
        symbol='ETH',
        fromchain=work_chain.chain_id,
        tochain=to_chain.chain_id,
        value=0.0001
    )
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    last_four_digits = data['data']['networkInfo']['lastFourDigits']
    manager = w3.to_checksum_address(data['data']['networkInfo']['manager'])
    amount_fee = Amount(data['data']['networkInfo']['toAssetFee']['gasFee'])
    return last_four_digits, manager, amount_fee


def bridge(to_chain: Chain, amount: Amount) -> str:

    last_four_digits, manager_address, amount_fee = get_bridge_data(to_chain)
    amount_with_fee_and_id = str(amount.wei + amount_fee.wei)[:-len(last_four_digits)] + last_four_digits

    if work_chain.native_token == 'ETH':
        tx_params = get_tx_params(
            w3,
            to=manager_address,
            value=int(amount_with_fee_and_id)
        )
    else:
        tx_params = get_tx_params(
            w3,
        )
        weth = Tokens.get_wrapped_native_token(work_chain)
        contract = w3.eth.contract(
            address=weth.address,
            abi=get_abi('erc20')
        )
        print(manager_address, amount_with_fee_and_id)
        tx_params = contract.functions.transfer(
            to=manager_address,
            value=int(amount_with_fee_and_id)
        ).build_transaction(tx_params)

    tx_params.update(get_fee(w3))
    tx_params['gas'] = w3.eth.estimate_gas(tx_params)
    tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    print(f"Tx hash: {tx_hash}")
    return tx_hash

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

def send_gas(amount_usdt: int, *chains: Chain):
    """
    :param amount: Количество токенов в USDT
    """
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
    print(f"Tx hash: {tx_hash}")
    return tx_hash





def main():
    amount =  Amount(1, 6)
    # bridge(Chains.Arbitrum, amount)
    # print(get_gas_data(Chains.POLYGON, Chains.BSC))

    send_gas(1, Chains.POLYGON, Chains.BSC)


if __name__ == '__main__':
    main()
