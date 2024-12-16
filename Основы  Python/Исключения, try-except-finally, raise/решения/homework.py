""""""

"""
Задание 1  - easy

Создайте собственный тип исключения - RandomException, который наследуется от Exception.
Напишите функцию, которая с вероятностью 50% будет выбрасывать это исключение.
Напишите код, который будет в цикле (100 раз) вызывать эту функцию и обрабатывать исключение, 
выводя в консоль сообщение о том, что исключение произошло.

"""
import random


class RandomException(Exception):
    pass


def random_exception():
    if random.randint(0, 1):
        raise RandomException('Random exception')


for _ in range(100):
    try:
        random_exception()
    except RandomException as e:
        print(e)

"""
Задание 2 - medium

Напишите функцию:

get_request(url: str, params: dict, attempts: int = 5, return_exception: bool = False) -> Optional[dict, list[dict]]:

которая сделает GET запрос на url с параметрами params и возвращает json, в случае неудачи повторит запрос attempts раз,
с паузой от 1 до 5 секунд между попытками.
- если return_exception равен True, то в случае окончания попыток вернет исключение типа GetException (создайте)
- если False, то вернет None.

"""
from typing import Optional
import random
import time

import requests


class GetException(Exception):
    pass


def get_request(url: str, params: dict, attempts: int = 5, return_exception: bool = False) -> Optional[
    dict, list[dict]]:
    """
    Метод для выполнения GET запроса, с повторением в случае неудачи.
    :param url: URL для запроса
    :param params: Параметры запроса
    :param attempts: Количество попыток
    :param return_exception: Возвращать ли исключение
    :return: Ответ сервера
    """
    for i in range(attempts):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            time.sleep(random.randint(1, 5))
    if return_exception:
        raise GetException('All attempts failed')
    return None

