from web3 import Web3
from eth_abi import decode
import asyncio
import aiohttp
from typing import List, Dict
import json

# Адрес Multicall контракта (можно использовать любой из популярных)
MULTICALL_ADDRESS = '0xcA11bde05977b3631167028862bE2a173976CA11'

# ABI Multicall контракта
MULTICALL_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "target", "type": "address"},
                    {"internalType": "bytes", "name": "callData", "type": "bytes"}
                ],
                "internalType": "struct Multicall3.Call[]",
                "name": "calls",
                "type": "tuple[]"
            }
        ],
        "name": "aggregate",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "blockNumber",
                "type": "uint256"
            },
            {
                "internalType": "bytes[]",
                "name": "returnData",
                "type": "bytes[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ABI ERC20 токена
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

class MulticallClient:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to RPC node")
        
        self.multicall = self.w3.eth.contract(
            address=self.w3.to_checksum_address(MULTICALL_ADDRESS),
            abi=MULTICALL_ABI
        )

    def decode_result(self, contract_address: str, function_abi: Dict, result: bytes) -> any:
        """Декодирует результат вызова функции"""
        contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(contract_address),
            abi=[function_abi]
        )
        return contract.functions[function_abi['name']].decode_function_result(result)

    def encode_function_call(self, contract_address: str, function_abi: Dict, *args) -> str:
        """Кодирует вызов функции в bytes"""
        contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(contract_address),
            abi=[function_abi]
        )
        # Получаем функцию
        func = contract.functions[function_abi['name']]
        # Кодируем вызов
        encoded = func(*args)._encode_transaction_data()
        print(f"Encoded call for {function_abi['name']}: {encoded}")
        return encoded

    async def multicall_query(self, calls: List[Dict]) -> List:
        """
        Выполняет multicall запрос
        
        Args:
            calls: Список словарей с параметрами вызовов
                  [{'target': '0x...', 'function': {...}, 'args': [...]}, ...]
        
        Returns:
            Список результатов вызовов
        """
        multicall_calls = []
        
        for call in calls:
            encoded_call = self.encode_function_call(
                call['target'],
                call['function'],
                *call.get('args', [])
            )
            multicall_calls.append({
                'target': self.w3.to_checksum_address(call['target']),
                'callData': encoded_call
            })        

        try:
            # Выполняем multicall запрос
            block_number, return_data = self.multicall.functions.aggregate(multicall_calls).call()
            print(f"Block number: {block_number}")
            print(f"Return data: {return_data}")
            
            # Декодируем результаты
            decoded_results = []
            for i, data in enumerate(return_data):
                try:
                    # Создаем контракт для декодирования
                    contract = self.w3.eth.contract(
                        address=self.w3.to_checksum_address(calls[i]['target']),
                        abi=[calls[i]['function']]
                    )
                    # Декодируем результат
                    decoded = decode([calls[i]['function']['outputs'][0]['type']], data)
                    decoded_results.append(decoded[0])  # Берем первый элемент, так как balanceOf возвращает одно значение
                except Exception as e:
                    print(f"Error decoding result for call {i}: {str(e)}")
                    decoded_results.append(None)
            
            return decoded_results
        except Exception as e:
            print(f"Error in multicall: {str(e)}")
            return []

async def main():
    # Используем 1rpc.io/eth
    rpc_url = 'https://1rpc.io/eth'
    
    try:
        # Создаем клиент
        client = MulticallClient(rpc_url)
        addresses = ['0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7'] * 2000
        tokens = ['0xdac17f958d2ee523a2206206994597c13d831ec7']
        
        
        # Пример вызова функции balanceOf у нескольких ERC20 токенов
        calls = []
        for token in tokens:
            for address in addresses:
                calls.append({
                    'target': token,
                    'function': {
                    'name': 'balanceOf', 
                    'inputs': [{'type': 'address', 'name': 'account'}],
                    'outputs': [{'type': 'uint256'}],
                    'stateMutability': 'view',
                    'type': 'function'
                },
                'args': [address]
            })
        
        results = await client.multicall_query(calls)
        print("Decoded results:", results)
        
        # Выводим баланс в читаемом формате
        for i, balance in enumerate(results):
            if balance is not None:
                print(f"Balance for call {i}: {balance}")
            else:
                print(f"Failed to get balance for call {i}")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 