# отправка транзакции с нативным токеном
# сбор параметров транзакции
# что такое газ, какие параметры транзакции за него отвечают
# как считать газ и цену газа
# что такое eip-1559 и legacy, как определять и менять параметры транзакции
# особенности разных блокчейнов
# упаковка транзакции
# подпись транзакции
# получение хеша транзакции и ожидание включения в блок
"""
{
    "chainId": 56,
    "from": "0xac8ce8fbc80115a22a9a69e42f50713aae9ef2f7",
    "to": "0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7",
    "value": "0x5af3107a4000"
    "nonce": "0x928",
    "data": "0x",

    "gas": "0x5208", # gasLimit # 1 000 000 000

    "gasPrice": "0x3b9aca00",
}

"""
import random
import time
from pprint import pprint

from eth_account import Account
from web3 import Web3, HTTPProvider

from main import Amount


class Chain:
    def __init__(self, name: str, rpc_url: str):
        self.name = name
        self.rpc = rpc_url


LINEA = Chain('LINEA', 'https://1rpc.io/linea')
BSC = Chain('BSC', 'https://1rpc.io/bnb')
ETH = Chain('ETH', 'https://1rpc.io/eth')
ARBITRUM = Chain('ARBITRUM', 'https://1rpc.io/arb')
OPTIMISM = Chain('OPTIMISM', 'https://1rpc.io/op')


class Onchain:
    def __init__(self, chain: Chain, private_key: str):
        self.chain = chain
        self.private_key = private_key
        self.w3 = Web3(HTTPProvider(chain.rpc))

    def get_native_balance(self, address: str) -> Amount:
        """
        Получение баланса нативного токена
        :param address: адрес кошелька
        :return: баланс в Amount
        """
        address = self.w3.to_checksum_address(address)
        balance_wei = self.w3.eth.get_balance(address)
        return Amount(balance_wei, is_wei=True)

    def _get_fees(self, tx_params: dict) -> dict:
        """
        Получение параметров газа для транзакции для eip-1559 и legacy
        :param tx_params: параметры транзакции
        :return: измененная транзакция
        """
        fees = self.w3.eth.fee_history(20, 'latest', [20])

        if self.chain.name == 'LINEA':
            gas_price = 7
        else:
            gas_price = self.w3.eth.gas_price

        if any(fees.get('baseFeePerGas', [0])):
            # eip-1559
            base_fee = gas_price
            priority_fees = [fee[0] for fee in fees.get('reward', [[0]])]
            median_index = len(priority_fees) // 2
            priority_fees.sort()
            priority_fee = int(priority_fees[median_index] * random.uniform(1.03, 1.1))

            max_fee = int(base_fee + priority_fee * random.uniform(1.03, 1.1))
            tx_params['maxFeePerGas'] = max_fee
            tx_params['maxPriorityFeePerGas'] = priority_fee
        else:
            tx_params['gasPrice'] = int(gas_price * random.uniform(1.03, 1.1))

        return tx_params




    def send_native(self, to_address: str, amount: float) -> str:
        """
        Отправка нативного токена
        :param to_address: адрес получателя
        :param amount: сумма
        :return: хеш транзакции
        """
        from_address =  self.w3.eth.account.from_key(self.private_key).address
        to_address = self.w3.to_checksum_address(to_address)

        tx_params = {
            'chainId': self.w3.eth.chain_id,
            'from': from_address,
            'to': to_address,
            'nonce': self.w3.eth.get_transaction_count(from_address),
            'value': self.w3.to_wei(amount, 'ether')
        }

        tx_params = self._get_fees(tx_params)
        try:
            tx_params['gas'] = self.w3.eth.estimate_gas(tx_params)
        except Exception as e:
            print(f'Ошибка оценки газа {e}')
            raise ValueError('Ошибка оценки газа')


        # decrypt

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f'Транзакция {tx_hash.hex()} отправлена, в блокчейне {self.chain.name}')
        return receipt['transactionHash'].hex()


def main():
    pk = '0x'
    onchain = Onchain(OPTIMISM, pk)
    onchain.send_native('0x624c222fEd7f88500Afa5021cC760B3106fe34be', 0.0001)


if __name__ == '__main__':
    main()
