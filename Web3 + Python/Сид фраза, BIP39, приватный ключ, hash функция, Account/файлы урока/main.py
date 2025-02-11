from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from eth_account import Account
import binascii
import secrets
import random

from web3 import Web3
from eth_keys import keys
import binascii

def main():
    rpc_provider = 'https://1rpc.io/eth'
    w3 = Web3(HTTPProvider(rpc_provider))

    seed = 'garbage clinic hub erosion bitter round limit leave crash color drum habit'
    pk = '88e59a41581323f283e8d1e8933e20a138bcd0cd2b2f5ea4e2916b89e5ded6e4'
    w3.eth.account.enable_unaudited_hdwallet_features()
    account1 : LocalAccount = w3.eth.account.from_mnemonic(seed, account_path="m/44'/60'/1'/0/1")
    address : LocalAccount = w3.eth.account.from_key(pk).address
    print(address)

    # публичный ключ
    private_key_bytes = binascii.unhexlify(pk)

    # Создаём объект приватного ключа
    private_key = keys.PrivateKey(private_key_bytes)

    # Получаем публичный ключ
    public_key = private_key.public_key
    print(public_key.to_hex())

    # Получаем адрес
    address = public_key.to_checksum_address()
    print(address)
    # при помощи keccak256
    address = Web3.keccak(hexstr=public_key.to_hex()).hex()
    print('0x' + address[24:])



    # 0123456789abcdef

    # что такое хеш и хеш функция
    # что такое mnemonic фраза и как ее создать
    # что такое публичный ключ
    # что такое адрес кошелька
    # аккаунт (адрес, приватный ключ, публичный ключ) в web3.py







if __name__ == '__main__':
    main()
