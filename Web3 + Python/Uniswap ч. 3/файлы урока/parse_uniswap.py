import os
import time
from pprint import pprint

from dotenv import load_dotenv
import requests
from eth_abi import decode
from web3 import Web3

from chains import Chains
from contracts import Contracts


class Etherscan:
    def __init__(self, api_key: str, chain_id: int = 1):
        self.api_key = api_key
        self.base_url = 'https://api.etherscan.io/v2/api'
        self.chain_id = chain_id

    def get_block_by_timestamp(self, timestamp: int):
        url = 'https://api.etherscan.io/v2/api'

        params = {
            'chainid': self.chain_id,
            'module': 'block',
            'action': 'getblocknobytime',
            'timestamp': timestamp,
            'closest': 'before',
            'apikey': self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('result')


    def get_transactions_by_address(self, address: str, start_block: int = 0, end_block: int | str = 'latest'):
        url = 'https://api.etherscan.io/v2/api'
        params = {
            'chainid': self.chain_id,
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': 'desc',
            'apikey': self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('result')



def main():
    load_dotenv()

    chain = Chains.Optimism
    uniswap_contract = '0x851116d9223fabed8e56c0e6b8ad0c31d98b3507'
    etherscan = Etherscan(api_key=os.getenv('ETHERSCAN_API_KEY'), chain_id=chain.chain_id)
    block = etherscan.get_block_by_timestamp(int(time.time() - 60 * 60 * 100))
    tx_list = etherscan.get_transactions_by_address(uniswap_contract, start_block=block)
    recipients = {}
    bipses = {}
    for tx in tx_list:
        input_tx = tx['input']
        if not input_tx.startswith('0x3593564c'):
            continue
        commands, inputs, deadline = decode(['bytes','bytes[]', 'uint256'],  bytes.fromhex(input_tx[10:]))
        for index in range(len(commands)):
            command = hex(commands[index])
            if command == '0x6':
                input_data = inputs[index]
                token, recipient, bips = decode(['address', 'address', 'uint256'], input_data)
                recipients[recipient] = recipients.get(recipient, 0) + 1
                bipses[bips] = bipses.get(bips, 0) + 1
    print(recipients)
    print(bipses)














if __name__ == '__main__':
    main()
