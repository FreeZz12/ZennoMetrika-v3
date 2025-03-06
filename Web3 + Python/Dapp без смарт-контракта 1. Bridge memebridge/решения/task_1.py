
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

import requests

from config import config
from chains import Chains, Chain
from amount import Amount
from tokens import Tokens
from utils import get_tx_params, get_fee, sing_send_tx, get_token_price_from_binance, get_abi

work_chain = Chains.POLYGON
w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)  # для polygon сети
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
        tx_params = contract.functions.transfer(
            to=manager_address,
            value=int(amount_with_fee_and_id)
        ).build_transaction(tx_params)

    tx_params.update(get_fee(w3))
    tx_params['gas'] = w3.eth.estimate_gas(tx_params)
    tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    print(f"Tx hash: {tx_hash}")
    return tx_hash


def main():
    amount =  Amount(0.00005)
    bridge(Chains.Arbitrum, amount)



if __name__ == '__main__':
    main()
