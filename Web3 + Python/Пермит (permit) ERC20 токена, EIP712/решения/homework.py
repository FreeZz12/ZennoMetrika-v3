""""""

"""
Задание 1 - easy
Напишите функцию is_permit, которая принимает адрес токена или 
объект токена и возвращает True, если токен поддерживает пермит,
иначе False.

"""

def is_token_permit(token: Token) -> bool:
    """
    Проверяет, поддерживает ли токен permit
    :param token: объект токена
    :return: True, если токен поддерживает permit, иначе False
    """
    contract = w3.eth.contract(address=token.address, abi=get_abi('erc20.json'))
    try:
        # если вызывается без ошибки, значит токен поддерживает permit
        contract.functions.DOMAIN_SEPARATOR().call()
        return True
    except Exception as e:
        return False


# код пишем тут

"""
Задание 2  - medium

Прикрепите к решению хеш транзакции выдачи пермита
токена USDC ровно на сумму 0.12345777 на любой адрес.
Транзакция должна быть отправлена НЕ адресом, который
выдает пермит.
"""

