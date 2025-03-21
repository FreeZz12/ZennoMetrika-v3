from pprint import pprint

import requests
from web3 import Web3

from amount import Amount
from chains import Chains, Chain
from config import config
from tokens import Tokens, Token, TokenType
from utils import get_tx_params, get_fee, sing_send_tx, approve


class CotractData:
    def __init__(self, name: str, address: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.chain = chain


class Contracts:

    permit2_arbitrum = CotractData(
        name='permit2',
        address='0x000000000022d473030f116ddee9f6b43ac78ba3',
        chain=Chains.Arbitrum)

    permit2_op = CotractData(
        name='permit2',
        address='0x000000000022D473030F116dDEE9F6B43aC78BA3',
        chain=Chains.Optimism)


    @classmethod
    def get_contract_data_by_name(cls, name: str, chain: Chain) -> CotractData | None:
        for contract_data in cls.__dict__.values():
            if isinstance(contract_data, CotractData):
                if contract_data.name == name and contract_data.chain == chain:
                    return contract_data
        raise ValueError(f'Контракт {name} не найден в сети {chain.name}')


def get_quote(w3: Web3, address: str, amount: Amount, token_in: Token, token_out: Token) -> tuple[
    dict, dict | None]:
    url = "https://trading-api-labs.interface.gateway.uniswap.org/v1/quote"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "JoyCGj29tT4pymvhaGciK4r1aIPvqW6W53xT1fwo",
        "origin": "https://app.uniswap.org",
        "referer": "https://app.uniswap.org/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    data = {
        "amount": str(amount.wei),
        "gasStrategies": [
            {
                "limitInflationFactor": 1.15,
                "displayLimitInflationFactor": 1.15,
                "priceInflationFactor": 1.5,
                "percentileThresholdFor1559Fee": 75,
                "minPriorityFeeGwei": 2,
                "maxPriorityFeeGwei": 9
            }
        ],
        "swapper": address,
        "tokenIn": token_in.address,
        "tokenInChainId": w3.eth.chain_id,
        "tokenOut": token_out.address,
        "tokenOutChainId": w3.eth.chain_id,
        "type": "EXACT_INPUT",
        "urgency": "normal",
        "protocols": ["V3"],  # , "V2" "V4",
        "slippageTolerance": 2.5
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    return data['quote'], data['permitData']


def get_swap(w3: Web3, address: str, amount: Amount, token_in: Token, token_out: Token) -> dict:
    if token_in.token_type == TokenType.NATIVE:
        token_in.address = w3.to_checksum_address('0x0000000000000000000000000000000000000000')
    if token_out.token_type == TokenType.NATIVE:
        token_out.address = w3.to_checksum_address('0x0000000000000000000000000000000000000000')

    url = "https://trading-api-labs.interface.gateway.uniswap.org/v1/swap"
    quote, permit_data = get_quote(w3, address, amount, token_in, token_out)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "JoyCGj29tT4pymvhaGciK4r1aIPvqW6W53xT1fwo",
        "origin": "https://app.uniswap.org",
        "referer": "https://app.uniswap.org/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    data = {
        'gasStrategies': [
            {
                "limitInflationFactor": 1.15,
                "displayLimitInflationFactor": 1.15,
                "priceInflationFactor": 1.5,
                "percentileThresholdFor1559Fee": 75,
                "minPriorityFeeGwei": 2,
                "maxPriorityFeeGwei": 9
            }
        ],
        'quote': quote,
        'refreshGasPrice': True,
        'simulateTransaction': True,
        'urgency': "normal"
    }

    if permit_data:
        pprint(permit_data)
        full_message = {
            'types': permit_data['types'],
            'domain': permit_data['domain'],
            'message': permit_data['values'],
        }
        signed_permit = w3.eth.account.sign_typed_data(full_message=full_message, private_key=config.private_key)
        data['signature'] = '0x' + signed_permit['signature'].hex()
        data['permitData'] = permit_data

    response = requests.post(url, headers=headers, json=data)
    pprint(response.json())
    return response.json()['swap']


def swap_api(w3: Web3, work_chain: Chain, token_in: Token, token_out: Token, amount: Amount):


    if token_in.token_type != TokenType.NATIVE:
        approve(
            w3=w3,
            token=token_in,
            spender=Contracts.get_contract_data_by_name('permit2', work_chain).address,
            amount=amount,
            private_key=config.private_key,
            is_max=True
        )

    swap_data = get_swap(
        w3=w3,
        address=w3.eth.default_account,
        amount=amount,
        token_in=token_in,
        token_out=token_out
    )
    tx_params = get_tx_params(
        w3=w3,
        to=swap_data['to'],
        value=int(swap_data['value'], 16),
        data=swap_data['data'],
    )
    tx_params.update(get_fee(w3))
    tx_params['gas'] = w3.eth.estimate_gas(tx_params)

    tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    print(f"Transaction hash: {tx_hash}")

def main():
    work_chain = Chains.Optimism
    token_in = Tokens.USDC_OP
    token_out = Tokens.USDT_OP
    amount = Amount(0.2, token_in.decimals)
    w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
    account = w3.eth.account.from_key(config.private_key)
    w3.eth.default_account = account.address

    swap_api(w3, token_in, token_out, amount)


if __name__ == '__main__':
    main()
