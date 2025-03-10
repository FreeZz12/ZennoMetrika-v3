import time

from eth_abi import encode
from eth_account.datastructures import SignedMessage
from web3 import Web3

from amount import Amount
from chains import Chains
from tokens import Tokens, Token
from config import config
from utils import get_abi, get_tx_params, sing_send_tx

work_chain = Chains.Arbitrum
w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
account = w3.eth.account.from_key(config.private_key)
w3.eth.default_account = account.address


token = Tokens.get_token_by_name('USDC', work_chain)
spender = w3.to_checksum_address('0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7')

contract = w3.eth.contract(address=token.address, abi=get_abi('erc20.json'))
permit_nonce = contract.functions.nonces(w3.eth.default_account).call()
deadline = int(time.time() + (24*60*60))
amount_wei = 100000 * 10 ** token.decimals

def is_token_permit(token: Token) -> bool:
    """ Поддерживает ли токен permit """
    pass


def get_permit(token: Token, amount: Amount, spender: str) -> SignedMessage:
    spender = w3.to_checksum_address(spender)
    contract_token = w3.eth.contract(address=token.address, abi=get_abi('erc20.json'))
    permit_nonce = contract_token.functions.nonces(w3.eth.default_account).call()
    deadline = int(time.time() + (24 * 60 * 60))
    permit_type_hash = Web3.keccak(text="Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)")
    encoded_data = encode(
            ['bytes32', 'address', 'address', 'uint256', 'uint256', 'uint256'],
            [permit_type_hash, w3.eth.default_account, spender, amount.wei, permit_nonce, deadline]
        )
    struct_hash = Web3.keccak(encoded_data)
    domain_separator = contract_token.functions.DOMAIN_SEPARATOR().call()
    digest = Web3.solidity_keccak(
        ['bytes1', 'bytes1', 'bytes32', 'bytes32'],
        [b'\x19', b'\x01', domain_separator, struct_hash]
    )
    signed_data = w3.eth.account._sign_hash(
        digest,
        private_key=account.key
    )
    return signed_data

    # tx_params = contract.functions.permit(
    #     w3.eth.default_account,
    #     spender,
    #     amount_wei,
    #     deadline,
    #     signed_data.v,
    #     hex(signed_data.r),
    #     hex(signed_data.s)
    # ).build_transaction(get_tx_params(w3))
    #
    # tx_hash = sing_send_tx(w3, tx_params, config.private_key)
    # print(f"Transaction hash: {tx_hash}")
    #
    #
    # print(100 * 10 ** token.decimals)
    # print(deadline)
    # print(signed_data.v)
    # print(hex(signed_data.r))
    # print(hex(signed_data.s))




def manual_permit():
    full_message = {
        "types": {
            "Permit": [
                {
                    "name": "owner",
                    "type": "address"
                },
                {
                    "name": "spender",
                    "type": "address"
                },
                {
                    "name": "value",
                    "type": "uint256"
                },
                {
                    "name": "nonce",
                    "type": "uint256"
                },
                {
                    "name": "deadline",
                    "type": "uint256"
                }
            ],
            "EIP712Domain": [
                {
                    "name": "name",
                    "type": "string"
                },
                {
                    "name": "version",
                    "type": "string"
                },
                {
                    "name": "chainId",
                    "type": "uint256"
                },
                {
                    "name": "verifyingContract",
                    "type": "address"
                }
            ]
        },
        "domain": {
            "name": "USD Coin",
            "version": "2",
            "chainId": w3.eth.chain_id,
            "verifyingContract": token.address
        },
        "primaryType": "Permit",
        "message": {
            "owner": w3.eth.default_account,
            "spender": spender,
            "value": 100 * 10 ** token.decimals,
            "nonce": permit_nonce,
            "deadline": deadline
        }
    }

    signed_data = w3.eth.account.sign_typed_data(private_key=config.private_key, full_message=full_message)

    print(100 * 10 ** token.decimals)
    print(deadline)
    print(signed_data.v)
    print(hex(signed_data.r))
    print(hex(signed_data.s))







if __name__ == '__main__':
    automatic_permit()
    # manual_permit()
