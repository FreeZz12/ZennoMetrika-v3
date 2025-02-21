import json
import os
import random

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


class Chain:
    def __init__(self, name: str, rpc: str, native_token: str, multiplier: float = 1.0):
        self.name = name
        self.rpc = rpc
        self.native_token = native_token
        self.multiplier = multiplier


class Chains:
    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH')
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH')
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH')
    BSC = Chain('BSC', 'https://1rpc.io/bnb', 'BNB')
    LINEA = Chain('LINEA', 'https://1rpc.io/linea', 'ETH', 1.3)


class Token:
    def __init__(self, name: str, address: str, decimals: int):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.decimals = decimals


class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6)
    USDT_ARBITRUM = Token('USDT', '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', 6)


class Onchain:

    def __init__(self, chain: Chain, private_key: str):
        self.chain = chain
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(chain.rpc))
        self.address = self.w3.eth.account.from_key(private_key).address

    def _get_abi(self, path: str):
        """
        Получение ABI из файла
        :param path: полный путь к файлу с указанием расширения файла
        :return: список словарей json
        """
        with open(path) as f:
            return json.loads(f.read())

    def _get_multiplier(self, min_mult: float = 1.03, max_mult: float = 1.1) -> float:
        return random.uniform(min_mult, max_mult)

    def get_fee(self, tx_params: dict) -> dict:
        fee_history = self.w3.eth.fee_history(20, 'latest', [20])

        if not any(fee_history.get('baseFeePerGas', [0])):
            tx_params['gasPrice'] = self.w3.eth.gas_price * self._get_multiplier() * self.chain.multiplier
            return tx_params

        base_fee = fee_history['baseFeePerGas'][-1]
        priority_fees = [fee[0] for fee in fee_history.get('reward', [0])] or [0]
        max_priority_fee = max(priority_fees) * self._get_multiplier() * self.chain.multiplier
        max_fee = (base_fee + max_priority_fee) * self._get_multiplier() * self.chain.multiplier

        tx_params['maxPriorityFeePerGas'] = int(max_priority_fee)
        tx_params['maxFeePerGas'] = int(max_fee)

        return tx_params

    def send_token(self, amount: float, to_address: str, token: Token | str | None = None) -> str:

        to_address = self.w3.to_checksum_address(to_address)

        token_name = None

        if token is None:
            token_name = self.chain.native_token
            amount_wei = int(amount * 10 ** 18)
            tx_params = self._prepare_tx_params(to_address, amount_wei)
        else:
            if isinstance(token, Token):
                contract_address = token.address
                token_name = token.name
            else:
                contract_address = token

            token_contract_address = self.w3.to_checksum_address(contract_address)
            abi = self._get_abi('erc20.json')
            contract = self.w3.eth.contract(address=token_contract_address, abi=abi)

            if isinstance(token, Token):
                decimals = token.decimals
            else:
                decimals = contract.functions.decimals().call()

            if token_name is None:
                token_name = contract.functions.symbol().call()

            amount_wei = int(amount * 10 ** decimals)
            tx_params = self._prepare_tx_params()
            tx_params = contract.functions.transfer(to_address, amount_wei).build_transaction(tx_params)

        # получаем историю комиссий
        tx_params = self.get_fee(tx_params)

        if tx_params.get('gas') is None:
            tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * self._get_multiplier())

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f'Транзакция {tx_hash.hex()} отправлена, в блокчейне {self.chain.name}, токен {token_name}')
        return tx_hash.hex()

    def _prepare_tx_params(self, to_address: str | None = None, value: int | None = None) -> dict:
        tx_params = {
            'chainId': self.w3.eth.chain_id,
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
        }

        if to_address:
            tx_params['to'] = self.w3.to_checksum_address(to_address)
        if value:
            tx_params['value'] = value

        return tx_params

    def allowance(self, token: Token, spender: str) -> int:
        """
        Получение суммы имеющегося апрува на токены
        :param token: объект токена с адресом контракта
        :param spender: адрес кошелька, на который разрешено переводить токены
        :return: сумма апрува в wei
        """
        spender = self.w3.to_checksum_address(spender)
        abi = self._get_abi('erc20.json')
        contract = self.w3.eth.contract(address=token.address, abi=abi)
        return contract.functions.allowance(self.address, spender).call()


    def approve(self, token: Token, spender: str, amount: float) -> str:
        """
        Отправка транзакции апрува на токены
        :param token: объект токена с адресом контракта
        :param spender: адрес кошелька, на который разрешено переводить токены
        :param amount: сумма апрува в токенах (не в wei)
        :return: хэш транзакции
        """
        spender = self.w3.to_checksum_address(spender)
        amount = int(amount * 10 ** token.decimals)
        abi = self._get_abi('erc20.json')
        contract = self.w3.eth.contract(address=token.address, abi=abi)

        allowance = contract.functions.allowance(self.address, spender).call()
        if amount != 0 and allowance >= amount:
            print(f'Транзакция апрув не требуется, т.к. разрешение уже есть')
            return '0x'

        tx_params = contract.functions.approve(spender, amount).build_transaction(self._prepare_tx_params())
        tx_params = self.get_fee(tx_params)
        tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * self._get_multiplier() * self.chain.multiplier)

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Транзакция апрув {tx_hash.hex()} отправлена, в блокчейне {self.chain.name},\n'
              f'токен {token.name} на сумму {amount / 10 ** token.decimals} кошельку {spender}')
        return tx_hash.hex()


def main():
    onchain = Onchain(Chains.Arbitrum, os.getenv('PK'))
    print(onchain.allowance(Tokens.USDT_ARBITRUM, '0x000000000022d473030f116ddee9f6b43ac78ba3'))
    print()

    onchain.approve(Tokens.USDT_ARBITRUM, '0x000000000022d473030f116ddee9f6b43ac78ba3', 1000)

    print(onchain.allowance(Tokens.USDT_ARBITRUM, '0x000000000022d473030f116ddee9f6b43ac78ba3'))


if __name__ == '__main__':
    main()
