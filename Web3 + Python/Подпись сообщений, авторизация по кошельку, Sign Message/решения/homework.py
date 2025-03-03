""""""

"""
Задание 1 - medium

Напишите скрипт, который авторизуется на платформе https://bima.money/faucet с помощью подписи сообщения
и запросов.
1. Изучите запросы при подключении кошелька
2. Найдите запрос для получения временной метки и сообщения для подписи
3. Подпишите сообщение
4. Найдите запрос для авторизации
5. Отправьте запрос на авторизацию с подписью и временной меткой

Внимательно смотрите на заголовки запросов, они могут быть важными для авторизации.

Итоговый запрос на ****/wallet/connect должен вернуть ответ содержащий errmsg:"no error"

"""




from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv
import requests

load_dotenv()

private_key = 'f629450ef53189883457c174dc6c95a2125a870ed3b579f58c8078604dcfa93b'
address = Account.from_key(private_key).address

def get_challenge() -> tuple[str, str]:
    """
    Получение временной метки и сообщения для подписи
    :return: timestamp, сообщение для подписи
    """
    url_get_challenge = 'https://mainnet-api-v1.bima.money/bima/wallet/tip_info'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://bima.money",
        "Referer": "https://bima.money/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Address": address,
    }
    response = requests.get(url_get_challenge, headers=headers)
    return response.json()['data']['timestamp'], response.json()['data']['tip_info']


def sign_message(message_text: str) -> str:
    message = encode_defunct(text=message_text)
    signed_message = Account.sign_message(message, private_key=private_key)
    return '0x' + signed_message.signature.hex()


def connect_wallet(signature: str, timestamp: str):
    url_connect_wallet = 'https://mainnet-api-v1.bima.money/bima/wallet/connect'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://bima.money",
        "Referer": "https://bima.money/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Address": address,
    }
    body = {
        "signature": signature,
        "timestamp": timestamp
    }
    response = requests.post(url_connect_wallet, headers=headers, json=body)
    if response.json()['errmsg'] == 'no error':
        print('Авторизация прошла успешно')
    else:
        print('Ошибка авторизации')


def main():
    timestamp, message_text = get_challenge()
    signature = sign_message(message_text)
    connect_wallet(signature, timestamp)




main()
# код пишем тут
