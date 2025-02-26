
"""
Задание 3 - hard

Напишите класс Onchain:
В init класса должны быть переданы Chain и приватный ключ.
Методы: send_token, get_fee, get_balance, _get_abi, _prepare_tx_params, allowance, approve,
Допишите методы в класс Onchain:
_get_relay_request_id(self, to_chain: Chain, amount: float, from_token: Token | None = None, to_token: Token | None = None) -> str
метод bridge_relay(self, to_chain: Chain, amount: float, from_token: Token | None = None, to_token: Token | None = None) -> str

Методы должны работать с объектами Token и Chain.

Напишите скрипт, который получает список приватных ключей из файла private_keys.txt,
перемешивает их, берет рандомную сеть из списка сетей, создает объект Onchain.
Далее проверяет были ли у данного кошелька за последние 24 часа транзакции с bridge_relay, если да, то пропускает
если нет, делает отправку ETH / USDT / USDC в рандомную сеть из списка сетей.
Скрипт должен работать в бесконечном цикле и делать транзакцию по отправке токенов для каждого
кошелька раз в сутки. Сделайте рандомную паузу между транзакциями, чтобы они равномерно распределялись
в течении суток.
Порядок кошельков должен каждый день меняться, чтобы не было паттерна в транзакциях.

!Подсказка!
Для проверки наличия транзакций используйте https://www.ankr.com/docs/advanced-api/query-methods/#ankr_gettransactionsbyaddress
1. запросите транзакции в нужных сетях за последние 24 часа
3. проверьте наличие транзакций с bridge_relay по нативным токенам или ERC20 токенам
"""
import time
import json
import os
from random import uniform, shuffle, choice

from web3 import Web3
import requests

from task_1 import Chain, Chains, Tokens, Token

class ContractData:
    def __init__(self, name: str, address: str, abi: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.abi = abi
        self.chain = chain


class ContractsData:
    WOOFI_ROUTER_ARB = ContractData('Woofi Router', '0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7',
                                    'woofi_router_abi.json', Chains.Arbitrum)

    RELAY_RECEIVER_NATIVE = ContractData('Relay Receiver Native',
                                         '0xa5F565650890fBA1824Ee0F21EbBbF660a179934',
                                         'not_abi', Chains.Arbitrum)

    RELAY_RECEIVER_ERC20 = ContractData('Relay Receiver ERC20', '0xf70da97812cb96acdf810712aa562db8dfa3dbef',
                                        'not_abi', Chains.Arbitrum)


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
        :return: список словарей json пригодный для передачи в объект контракта
        """
        with open(path) as f:
            return json.loads(f.read())

    def _get_multiplier(self, min_mult: float = 1.03, max_mult: float = 1.1) -> float:
        """
        Генерация случайного множителя комиссии
        """
        return uniform(min_mult, max_mult)

    def get_fee(self, tx_params: dict) -> dict:
        """
        Получение комиссий для legacy и EIP-1559 транзакций, редактирует переданный словарь tx_params
        """
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
        """
        Отправка любых токенов (ERC20 или нативного токена) на адрес to_address, если
        не указан token, то отправляется нативный токен сети.
        :param amount: сумма токенов в человеческом формате
        :param to_address: адрес получателя
        :param token:  объект Token или адрес контракта ERC20
        :return: hash транзакции в формате hex
        """

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
        """
        Подготовка стандартных параметров транзакции, по необходимости добавляются to и value
        :param to_address: адрес получателя, в случае отправки нативного токена, при работе с ERC20 - None
        :param value: сумма нативных токенов в wei, в случае отправки нативного токена, при работе с ERC20 - None
        :return: словарь параметров транзакции
        """
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

    def get_balance(self, address: str | None = None, token: Token | None = None) -> float:

        address = address or self.address
        address = self.w3.to_checksum_address(address)

        if not token:
            return self.w3.eth.get_balance(address) / 10 ** 18

        with open('erc20.json') as file:
            abi = json.loads(file.read())

        contract = self.w3.eth.contract(address=token.address, abi=abi)

        balance = contract.functions.balanceOf(address).call()

        return balance / 10 ** token.decimals

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
        tx_params['gas'] = int(
            self.w3.eth.estimate_gas(tx_params) * self._get_multiplier() * self.chain.multiplier)

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Транзакция апрув {tx_hash.hex()} отправлена, в блокчейне {self.chain.name},\n'
              f'токен {token.name} на сумму {amount / 10 ** token.decimals} кошельку {spender}')
        return tx_hash.hex()

    def swap_woofi(self, from_token: Token, to_token: Token, amount: float) -> str:
        """
        Своп токенов через Woofi
        :param from_token: объект Token, токен, который отправляем
        :param to_token: объект Token, токен, который получаем
        :param amount: сумма токенов в человеческом формате
        """

        weth_token = Tokens.get_token_by_name('WETH', self.chain)
        eth_token = Tokens.get_token_by_name('ETH', self.chain)

        if from_token != eth_token:
            self.approve(from_token, ContractsData.WOOFI_ROUTER_ARB.address, amount)

        abi = self._get_abi(ContractsData.WOOFI_ROUTER_ARB.abi)
        contract = self.w3.eth.contract(
            address=ContractsData.WOOFI_ROUTER_ARB.address,
            abi=abi
        )

        min_to_amount = contract.functions.querySwap(
            fromToken=weth_token.address if from_token == eth_token else from_token.address,
            toToken=weth_token.address if to_token == eth_token else to_token.address,
            fromAmount=int(amount * 10 ** from_token.decimals)
        ).call()

        min_to_amount = int(min_to_amount * 0.95)

        amount_wei = int(amount * 10 ** from_token.decimals)

        value = amount_wei if from_token == eth_token else 0

        tx_params = self._prepare_tx_params(value=value)

        tx_params = contract.functions.swap(
            fromToken=from_token.address,
            toToken=to_token.address,
            fromAmount=amount_wei,
            minToAmount=min_to_amount,
            to=self.address,
            rebateTo=self.address
        ).build_transaction(tx_params)

        tx_params = self.get_fee(tx_params)

        if tx_params.get('gas') is None:
            tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * self._get_multiplier())

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx['raw_transaction'])
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(
            f'Транзакция {tx_hash.hex()} отправлена, в блокчейне {self.chain.name}, своп {from_token.name} -> {to_token.name}')
        return tx_hash.hex()

    def _get_relay_contract(
            self,
            to_chain: Chain,
            amount: float,
            from_token: Token | None = None,
            to_token: Token | None = None
    ) -> str:

        response = self._get_relay_request_api(to_chain, amount, from_token, to_token)
        return response['steps'][0]['items'][0]['data']['to']

    def _get_relay_request_api(
            self,
            to_chain: Chain,
            amount: float,
            from_token: Token | None = None,
            to_token: Token | None = None
    ) -> dict:

        amount_wei = int(amount * 10 ** from_token.decimals)

        url = 'https://api.relay.link/quote'
        body = {
            "user": self.address,
            "originChainId": self.chain.chain_id,
            "destinationChainId": to_chain.chain_id,
            "originCurrency": from_token.address,
            "destinationCurrency": to_token.address,
            "recipient": self.address,
            "tradeType": "EXACT_INPUT",
            "amount": amount_wei,
            "referrer": "relay.link/swap",
            "useExternalLiquidity": False,
            "useDepositAddress": False
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Origin': 'https://relay.link',
        }

        return requests.post(url, headers=headers, json=body).json()

    def _get_relay_request_id(
            self,
            to_chain: Chain,
            amount: float,
            from_token: Token | None = None,
            to_token: Token | None = None
    ) -> str:

        response = self._get_relay_request_api(to_chain, amount, from_token, to_token)
        return response['steps'][0]['requestId']

    def _get_call_data(
            self,
            to_chain: Chain,
            amount: float,
            from_token: Token | None = None,
            to_token: Token | None = None
    ) -> str:

        response = self._get_relay_request_api(to_chain, amount, from_token, to_token)
        print(response)
        return response['steps'][0]['items'][0]['data']['data']

    def relay_bridge(
            self,
            to_chain: Chain,
            amount: float,
            from_token: Token | None = None,
            to_token: Token | None = None) -> str:

        native_token = Token(
            'ETH',
            '0x0000000000000000000000000000000000000000',
            18,
            self.chain
        )

        from_token = from_token or native_token
        to_token = to_token or native_token

        amount_wei = int(amount * 10 ** from_token.decimals)

        if from_token == native_token:
            response = self._get_relay_request_api(to_chain, amount, from_token, to_token)
            request_id = response['steps'][0]['requestId']
            contract_address = response['steps'][0]['items'][0]['data']['to']
            tx_params = self._prepare_tx_params(to_address=contract_address, value=amount_wei)
            tx_params['data'] = request_id
        else:
            data = self._get_call_data(to_chain, amount, from_token, to_token)
            tx_params = self._prepare_tx_params(to_address=from_token.address)
            tx_params['data'] = data

        tx_params = self.get_fee(tx_params)
        tx_params['gas'] = self.w3.eth.estimate_gas(tx_params)

        signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(tx_hash.hex())
        return tx_hash.hex()

    def check_relay_tx(self) -> bool:
        """
        Проверка наличия транзакций с bridge_relay за последние 24 часа
        в сетях Arbitrum, Optimism, Base, Linea
        :return: True, если транзакции есть, False, если нет
        """
        url = 'https://rpc.ankr.com/multichain/'
        ankr_api_key = os.getenv('ANKR_API_KEY')
        body = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'ankr_getTransactionsByAddress',
            'params': {
                'blockchain':  ['arbitrum', 'optimism', 'base', 'linea'],
                'fromTimestamp': int(time.time() - 24 * 60 * 60),
                'address': self.address
            }
        }
        response = requests.post(url + ankr_api_key, json=body).json()
        native = ContractsData.RELAY_RECEIVER_NATIVE.address.lower()
        erc20 = ContractsData.RELAY_RECEIVER_ERC20.address.lower()
        for tx in response['result']['transactions']:
            if tx['to'].lower() == native or erc20 in tx['input'].lower():
                return True
        return False


def main2():
    with open('private_keys.txt') as f:
        private_keys = f.read().splitlines()

    # фиксированная задержка между транзакциями
    fix_delay = 24 * 60 * 60 / len(private_keys)  # фиксированная задержка между транзакциями

    while True:
        # перемешиваем список приватных ключей
        shuffle(private_keys)
        # берем рандомный ключ из списка
        for private_key in private_keys:
            # обновляем список сетей
            chains = [Chains.Arbitrum, Chains.Optimism, Chains.Base, Chains.Linea]
            # выбираем рандомную сеть
            from_chain = choice(chains)
            # удаляем выбранную сеть из списка
            chains.remove(from_chain)
            # создаем объект w3 для выбранной сети
            onchain = Onchain(from_chain, private_key)
            # проверяем наличие транзакций с bridge_relay
            if onchain.check_relay_tx():
                continue
            # выбираем рандомную сеть для пересылки
            to_chain = choice(chains)
            # выбираем рандомный токен на отправку и получение
            tokens = [
                Tokens.get_token_by_name('USDT', from_chain),
                Tokens.get_token_by_name('USDC', from_chain),
                None # нативный токен
            ]
            from_token = choice(tokens)
            to_tokens = [
                Tokens.get_token_by_name('USDT', to_chain),
                Tokens.get_token_by_name('USDC', to_chain),
                None # нативный токен
            ]
            to_token = choice(to_tokens)
            # получаем баланс кошелька
            balance = onchain.get_balance(token=from_token)
            # выбираем рандомную сумму для пересылки
            amount = uniform(0, balance)
            # отправляем токены
            onchain.relay_bridge(to_chain, amount, from_token, to_token)

            # рандомная задержка между транзакциями
            delay = fix_delay + uniform(-fix_delay / 2, fix_delay / 2)
            time.sleep(delay)


main2()
