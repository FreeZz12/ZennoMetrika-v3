from web3 import Web3
from web3.contract import Contract

from chains import Chains, Chain
from tokens import Tokens, Token
from amount import Amount
from utils import get_abi, get_tx_params, sing_send_tx, approve, to_amount

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



class CotractData:
    def __init__(self, name: str, address: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.chain = chain


class Contracts:
    stargate_pool_usdc_op = CotractData(
        'stargate_pool_usdc',
        '0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
        Chains.Optimism)

    stargate_pool_native_op = CotractData(
        'stargate_pool_native',
        '0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        Chains.Optimism)

    stargate_pool_usdt_op = CotractData(
        'stargate_pool_usdt',
        '0x19cFCE47eD54a88614648DC3f19A5980097007dD',
        Chains.Optimism)

    stargate_pool_native_arb = CotractData(
        'stargate_pool_native',
        '0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F',
        Chains.Arbitrum)

    stargate_pool_usdt_arb = CotractData(
        name='stargate_pool_usdt',
        address='0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
        chain=Chains.Arbitrum
    )

    stargate_pool_usdc_arb = CotractData(
        name='stargate_pool_usdc',
        address='0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        chain=Chains.Arbitrum
    )

    @classmethod
    def get_contract_data_by_name(cls, name: str, chain: Chain) -> CotractData | None:
        for contract_data in cls.__dict__.values():
            if isinstance(contract_data, CotractData):
                if contract_data.name == name and contract_data.chain == chain:
                    return contract_data
        raise ValueError(f'Контракт {name} не найден в сети {chain.name}')


def get_stargate_fee(w3: Web3, contract: Contract,  to_chain: Chain, amount_wei: int) -> tuple[int, int]:
    min_amount = int(amount_wei * 0.995)
    fee = contract.functions.quoteSend(
        (
            chains_eid[to_chain.chain_id],
            '0x' + w3.eth.default_account[2:].zfill(64),
            amount_wei,
            min_amount,
            '0x',
            '0x',
            '0x01'
        ),
        False
    ).call()
    return fee


def validate(contract: Contract, to_chain: Chain) -> bool:
    credit = contract.functions.paths(chains_eid[to_chain.chain_id]).call()
    return credit

def bridge(w3: Web3,  private_key: str, from_chain: Chain, to_chain: Chain, amount: float | Amount, token: Token | None = None):

    amount = to_amount(amount, token)

    token_name = token.name.lower() if token else 'native'
    contract_data = Contracts.get_contract_data_by_name(f'stargate_pool_{token_name}', from_chain)
    if token:
        approve(w3, token, contract_data.address, amount, private_key)

    contract = w3.eth.contract(address=contract_data.address, abi=get_abi(contract_data.name))

    if not validate(contract, to_chain):
        print(f'Токен {token_name} не поддерживается для сети {to_chain.name}')
        return

    min_amount = int(amount.wei * 0.995)
    fee = get_stargate_fee(contract, to_chain, amount.wei)
    value = fee[0] if token else fee[0] + amount.wei
    tx_params = get_tx_params(w3, value=value)

    tx_params = contract.functions.send(
        _sendParam=(
            chains_eid[to_chain.chain_id],
            '0x' + w3.eth.default_account[2:].zfill(64),
            amount.wei,
            min_amount,
            '0x',
            '0x',
            '0x01'
        ),
        _fee=fee,
        _refundAddress=w3.eth.default_account
    ).build_transaction(tx_params)
    tx_hash = sing_send_tx(w3, tx_params, private_key)
    print(f'Hash: {tx_hash}')
