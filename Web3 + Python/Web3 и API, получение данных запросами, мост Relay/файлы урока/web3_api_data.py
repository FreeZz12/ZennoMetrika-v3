import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from web3 import Web3
import requests

load_dotenv()


@dataclass
class Chain:
    name: str
    rpc: str
    native_currency: str
    chain_id: int
    multiplier: int = 1


class Chains:
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH', 42161)
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH', 10)


w3 = Web3(Web3.HTTPProvider(Chains.Arbitrum.rpc))
private_key = os.getenv("PK")
address = w3.eth.account.from_key(private_key).address


def get_fee(tx_params: dict, w3: Web3) -> dict:
    fee_history = w3.eth.fee_history(20, 'latest', [20])
    base_fee = fee_history['baseFeePerGas'][-1]
    priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
    max_priority_fee = max(priority_fees)
    max_fee = (base_fee + max_priority_fee) * 1.1

    tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
    tx_params['maxFeePerGas'] = int(max_fee)

    return tx_params

def get_request_id(to_chain: Chain, amount: float, to_token_contract: str) -> str:
    url = 'https://api.relay.link/quote'
    body = {
        "user": address,
        "originChainId": w3.eth.chain_id,
        "destinationChainId": to_chain.chain_id,
        "originCurrency": "0x0000000000000000000000000000000000000000",
        "destinationCurrency": to_token_contract,
        "recipient": address,
        "tradeType": "EXACT_INPUT",
        "amount": int(amount * 10 ** 18),
        "referrer": "relay.link/swap",
        "useExternalLiquidity": False,
        "useDepositAddress": False
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Origin': 'https://relay.link',
    }

    response = requests.post(url, json=body, headers=headers)

    return response.json()['steps'][0]['requestId']

def bridge_relay(to_chain: Chain, amount: float, to_token_contract: str | None = None):

    if to_token_contract is None:
        to_token_contract = '0x0000000000000000000000000000000000000000'

    request_id = get_request_id(to_chain, amount, to_token_contract)

    contract_address = w3.to_checksum_address('0xa5f565650890fba1824ee0f21ebbbf660a179934')

    tx_params = {
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
        'chainId': w3.eth.chain_id,
        'to': contract_address,
        'value': int(amount * 10 ** 18),
        'data': request_id
    }

    tx_params = get_fee(tx_params, w3)

    tx_params['gas'] = w3.eth.estimate_gas(tx_params)

    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Tx hash: {tx_hash.hex()}")

    return tx_hash.hex()



def main():
    bridge_relay(Chains.Optimism, 0.0001)
    bridge_relay(Chains.Optimism, 0.0001, '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58')



if __name__ == "__main__":
    main()
