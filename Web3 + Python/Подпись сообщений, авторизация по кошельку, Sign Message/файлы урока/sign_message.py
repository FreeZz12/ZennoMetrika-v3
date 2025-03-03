import os

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from dotenv import load_dotenv
import requests

load_dotenv()

private_key = 'f629450ef53189883457c174dc6c95a2125a870ed3b579f58c8078604dcfa93b'


def sign_message(message_text: str) -> str:
    message = encode_defunct(text=message_text)
    signed_message = Account.sign_message(message, private_key=private_key)
    return '0x' + signed_message.signature.hex()


def main():
    message_text = 'Please sign this message to confirm you are the owner of this address and Sign in to TrustGo App'
    message = encode_defunct(text=message_text)
    signed_message = Account.sign_message(message, private_key=private_key)
    signature = signed_message.signature.hex()
    # signature = sign_message(message_text)
    print(f'Signed Message: {signature}')

    url_check_signed_message = 'https://mp.trustalabs.ai/accounts/check_signed_message'
    body = {
        'mode': 'evm',
        'address': Account.from_key(private_key).address,
        'message': 'Please sign this message to confirm you are the owner of this address and Sign in to TrustGo App',
        'signature': '0x' + signature
    }
    response = requests.post(url_check_signed_message, json=body)
    token = response.json()['data']['token']

    url_check_token = f'https://mp.trustalabs.ai/accounts/check_token?token={token}'
    response = requests.get(url_check_token)
    print(response.json())

    url_check_score = 'https://mp.trustalabs.ai/trustgo/score'
    params = dict(
        account=Account.from_key(private_key).address,
        chainId=59144
    )
    headers = {
        'Authorization': f'TOKEN {token}'
    }
    response = requests.get(url_check_score, params=params, headers=headers)
    print(response.json())

    # message_hex = encode_defunct(text=message_text)
    # # print(f'Message: {encode_defunct(text=message_text).body.hex()}')
    # # print(f'Message: {message_text.encode().hex()}')
    # print(f'Message: {message_hex.body.hex()}')
    # signed_message = Web3().eth.account.sign_message(message_hex, private_key=private_key)
    # print(f'Signed Message: {signed_message.signature.hex()}')


main()
