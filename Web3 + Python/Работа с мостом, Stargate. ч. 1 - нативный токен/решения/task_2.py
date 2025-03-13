from typing import Literal

from web3 import Web3
from web3.contract import Contract

from config import config
from chains import Chains, Chain
from contracts import Contracts
from amount import Amount
from utils import get_tx_params, sing_send_tx

chains_eid = {
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

work_chain = Chains.ARBITRUM
w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
account = w3.eth.account.from_key(config.private_key)
w3.eth.default_account = account.address


def get_stargate_fee(to_chain: Chain, contract: Contract, amount_wei: int) -> tuple[int, int]:
    """
    Получаем комиссию за отправку токенов через мост Stargate.
    :param to_chain: целевая сеть
    :param contract: инстанс контракта
    :param amount_wei: количество токенов в wei
    :return: Кортеж (нативная комиссия, комиссия в токенах LZ)
    """
    fee = contract.functions.quoteSend(
        (
            chains_eid[to_chain.chain_id],
            '0x' + account.address[2:].zfill(64),
            amount_wei,
            int(amount_wei * 0.995),
            '0x',
            '0x',
            '0x01'
        ),
        False
    ).call()
    return fee


def bridge(to_chain: Chain, amount: Amount):
    # получаем объект с данными контракта
    contract_data = Contracts.stargate_pool_native[work_chain]
    # создаем инстанс контракта
    contract = contract_data.get_contract(w3)
    # получаем комиссию
    fee = get_stargate_fee(to_chain, contract, amount.wei)
    tx_params = get_tx_params(w3, value=amount.wei + fee[0])

    tx_params = contract.functions.send(
        _sendParam=(
            chains_eid[to_chain.chain_id],
            '0x' + account.address[2:].zfill(64),
            amount.wei,
            int(amount.wei * 0.995),
            '0x',
            '0x',
            '0x01'
        ),
        _fee=fee,
        _refundAddress=account.address
    ).build_transaction(tx_params)
    tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    print(f'Hash: {tx_hash}')


def main():
    amount = Amount(0.0005)
    bridge(to_chain=Chains.OP, amount=amount)


if __name__ == '__main__':
    main()
