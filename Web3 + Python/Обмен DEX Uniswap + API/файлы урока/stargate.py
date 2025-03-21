import time

import requests
from web3 import Web3
from web3.contract import Contract

from chains import Chains, Chain
from contracts import Contracts, ContractRaw
from config import config

from tokens import Token, Tokens, TokenType
from utils import get_abi, get_tx_params, sing_send_tx

work_chain = Chains.Arbitrum
w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
account = w3.eth.account.from_key(config.private_key)
w3.eth.default_account = account.address

chains_data = {
    1: 30101,  # Ethereum
    56: 30102,  # BNB Chain
    43114: 30106,  # Avalanche
    137: 30109,  # Polygon
    42161: 30110,  # Arbitrum
    10: 30111,  # OP (OP Mainnet)
    1088: 30151,  # Metis
    59144: 30183,  # Linea
    5000: 30181,  # Mantle
    8453: 30184,  # Base
    2222: 30177,  # Kava
    534352: 30214,  # Scroll
    1313161554: 30211,  # Aurora (значение network_id добавлено извне)
    1116: 30153,  # CORE
    146: 30332,  # Sonic
    100: 30145,  # Gnosis (Gnosis Chain)
    8217: 30150,  # Kaia (второй элемент с endpointID 30150)
    167000: 30290,  # Taiko
    1380012617: 30235,  # Rari Chain
    1329: 30280,  # Sei
    14: 30295,  # Flare
    1625: 30294,  # Gravity
    2741: 30324,  # Abstract
    1868: 30340,  # Soneium
    80094: 30362,  # Berachain
    30: 30333,  # Rootstock
    1480: 30330,  # Vana
    57073: 30339,  # Ink
    122: 30138,  # Fuse
    666666666: 30267,  # Degen
    1514: 30364  # Story
}


def get_native_drop_amount(to_chain: Chain) -> int:
    contract = Contracts.get_contract_raw_by_name_and_chain('stargate_token_messaging', to_chain).get_contract(w3)
    to_chain_id = chains_data[to_chain.chain_id]
    amounts = contract.functions.nativeDropAmounts(to_chain_id).call()
    return amounts


def get_lo_fee(contract: Contract, to_chain: Chain, amount: int) -> tuple[int, int]:
    fee = contract.functions.quoteSend(
        (
            chains_data[to_chain.chain_id],
            '0x' + account.address[2:].zfill(64),
            amount,
            int(amount * 0.995),
            #  0x0003 cursorhere -> 01 0011 01000000000000000000000000000249f0 + _extraOptions[2:]
            # _extraOptions = 01 0031 02000000000000000000001b48eb57e000000000000000000000000000ac8ce8fbc80115a22a9a69e42f50713aae9ef2f7"

            #  000301003102
            # 0x000301001101000000000000000000000000000249f0
            # "01003102000000000000000000001b48eb57e000  000000000000000000000000ac8ce8fbc80115a22a9a69e42f50713aae9ef2f7"
            # 0003 01 0031 02 00000000000000000002bc4f987a2000            # 000000000000000000000000ac8ce8fbc80115a22a9a69e42f50713aae9ef2f7
            '0x', # gas destination medium-bus 0x000101
            '0x',
            '0x' # taxi 0x или bus 0x01
        ),
        False,
    ).call()
    return fee


def send(token: Token, to_chain: Chain, amount: float):
    amount_wei = int(amount * 10 ** token.decimals)
    if token.token_type == TokenType.NATIVE:
        token.name = TokenType.NATIVE
    contract_raw = Contracts.get_contract_raw_by_name_and_chain(f'stargate_pool_{token.name.lower()}', work_chain)
    contract = contract_raw.get_contract(w3)
    fee = get_lo_fee(contract, to_chain, amount_wei)
    value = fee[0] + amount_wei if token.token_type == TokenType.NATIVE else 0
    tx_params = contract.functions.send(
        (
            chains_data[to_chain.chain_id],
            '0x' + account.address[2:].zfill(64),
            amount_wei,
            int(amount_wei * 0.995),
            '0x',
            '0x',
            '0x01'
        ),
        fee,
        account.address,
    ).build_transaction(get_tx_params(w3, value=value))

    tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    print(f'Tx hash: {tx_hash}')
    return '0x' + tx_hash

def get_status(tx_hash: str):
    url = f'https://scan.layerzero-api.com/v1/messages/tx/{tx_hash}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print(data)

def get_bus_status(to_chain: Chain, tx_hash: str, timeout: int = 60):
    time.sleep(30)
    from_chain_id = chains_data[work_chain.chain_id]
    to_chain_id = chains_data[to_chain.chain_id]
    url = f'https://mainnet.stargate-api.com/v1/buses/queue/{from_chain_id}/{to_chain_id}'
    for attempt in range(timeout):
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for passenger in data['queue']['passengers']:
            if passenger['txHash'] == tx_hash:
                time.sleep(5)
                break
        else:
            time.sleep(30)
            return



def main():
    native = Tokens.get_native(work_chain)

    tx_hash = send(native, Chains.Optimism, 0.0002)
    # get_status('0xd4b41d45ff8ba315a03f0a441b1b28856bc2c5c9b05feb0b9f4242754eb9a140')
    get_bus_status(Chains.Optimism, tx_hash)


if __name__ == '__main__':
    main()
