""""""
from typing import Optional

import requests

"""
Задание 1 - easy

Напишите функцию open_browser, которая принимает на вход номер профиля
и запускает браузер с этим профилем.

"""
def open_browser(profile_number: int) -> dict:
    ads_local_api = 'http://localhost:50325'
    path = '/api/v1/browser/start'
    params = dict(
        serial_number=profile_number,
        open_tabs=1)
    response = requests.get(ads_local_api + path, params=params)
    return response.json()


"""
Задание 2  - medium
Напишите функцию check_browser, которая принимает на вход номер профиля,
если профиль не активен, возвращает None, если активен, возвращает значение из
полученного json по ключам response['data']['ws']['puppeteer'].

Напишите функцию open_browser, которая принимает на вход номер профиля,
проверяет его статус с помощью функции check_browser, если профиль активен,
возвращает значение из полученного json по ключам response['data']['ws']['puppeteer'],
если профиль не активен, запускает браузер с этим профилем и возвращает значение из
полученного json по ключам response['data']['ws']['puppeteer'].
"""
ads_local_api = 'http://localhost:50325'

def check_browser(profile_number: int) -> Optional[dict]:
    """
    Проверяет статус профиля,
    :param profile_number: номер профиля в ADS
    :return: если профиль не активен, возвращает None, если активен, возвращает значение из полученного json по ключам response['data']['ws']['puppeteer']
    """
    path_status = '/api/v1/browser/active'
    params = dict(serial_number=profile_number)
    response = requests.get(ads_local_api + path_status, params=params).json()
    status = response['data']['status']
    if status == 'Inactive':
        return None
    return response['data']['ws']['puppeteer']

def open_browser(profile_number: int) -> dict:
    """
    Запускает браузер с профилем profile_number, если еще не запущен
    :param profile_number: номер профиля в ADS
    :return: возвращает значение из полученного json по ключам response['data']['ws']['puppeteer']
    """
    puppeteer = check_browser(profile_number)
    if puppeteer:
        return puppeteer
    path = '/api/v1/browser/start'
    params = dict(
        serial_number=profile_number,
        open_tabs=1)
    response = requests.get(ads_local_api + path, params=params)
    return response.json()

"""
Задание 3 - hard

Создайте класс ADS, который имеет следующие аттрибуты:
- защищенный атрибут _ads_local_api, который хранит строку с адресом API
- метод __init__, который принимает на вход номер профиля и сохраняет его в аттрибут profile_number,
и запускает метод open_browser.
- метод check_browser, который проверяет статус профиля profile_number,
если профиль не активен, возвращает None, если активен, возвращает значение из
полученного json по ключам response['data']['ws']['puppeteer']
- метод open_browser, который проверяет статус профиля profile_number с помощью метода check_browser,
если профиль активен, возвращает значение из полученного json по ключам response['data']['ws']['puppeteer'],
если профиль не активен, запускает браузер с этим профилем и возвращает значение из полученного json 
по ключам response['data']['ws']['puppeteer'].
- метод close_browser, который закрывает профиль profile_number
"""

class ADS:
    def __init__(self, profile_number: int):
        self._ads_local_api = 'http://localhost:50325'
        self.profile_number = profile_number
        self.open_browser()

    def check_browser(self) -> Optional[dict]:
        """
        Проверяет статус профиля,
        :param profile_number: номер профиля в ADS
        :return: если профиль не активен, возвращает None, если активен, возвращает значение из полученного json по ключам response['data']['ws']['puppeteer']
        """
        path_status = '/api/v1/browser/active'
        params = dict(serial_number=self.profile_number)
        response = requests.get(self._ads_local_api + path_status, params=params).json()
        status = response['data']['status']
        if status == 'Inactive':
            return None
        return response['data']['ws']['puppeteer']

    def open_browser(self) -> dict:
        """
        Запускает браузер с профилем profile_number, если еще не запущен
        :param profile_number: номер профиля в ADS
        :return: возвращает значение из полученного json по ключам response['data']['ws']['puppeteer']
        """
        puppeteer = self.check_browser()
        if puppeteer:
            return puppeteer
        path = '/api/v1/browser/start'
        params = dict(
            serial_number=self.profile_number,
            open_tabs=1)
        response = requests.get(self._ads_local_api + path, params=params)
        return response.json()['data']['ws']['puppeteer']

    def close_browser(self) -> dict:
        """
        Закрывает профиль profile_number
        """
        path = '/api/v1/browser/stop'
        params = dict(serial_number=self.profile_number)
        response = requests.get(self._ads_local_api + path, params=params)
        return response.json()


