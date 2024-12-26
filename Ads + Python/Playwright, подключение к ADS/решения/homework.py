""""""
import random

from typing import Optional

import requests

"""
Задание 1 - medium

Создайте функцию run_browser, которая принимает на вход номер профиля и запускает браузер.
Функция должна проверять статус профиля с помощью функции check_browser, если активен, по подключать
playwright к нему, если нет, то запустить профиль через функцию open_browser и подключить playwright к нему.
Функция должна делать 3 попытки запуска браузера и подключения к нему,
если браузер по каким-то причинам не запустился или не получилось сделать подключение к нему,
Проверять статус подключения нужно через метод is_connected.
Функция должна возвращать объект Browser из Playwright.
slow_mo должен быть случайным числом от 700 до 1400.

"""
from playwright.sync_api import sync_playwright, Browser, Playwright

ads_local_api = "http://local.adspower.net:50325"


def check_browser(profile_number: int) -> Optional[str]:
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


def open_browser(profile_number: int) -> str:
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
    response = requests.get(ads_local_api + path, params=params).json()
    return response['data']['ws']['puppeteer']


def run_browser(profile_number: int) -> Browser:
    pw = None
    for _ in range(3):
        try:
            puppeteer = check_browser(profile_number)
            if not puppeteer:
                puppeteer = open_browser(profile_number)
            pw = sync_playwright().start()
            browser = pw.chromium.connect_over_cdp(puppeteer, slow_mo=random.randint(700, 1400))
            if browser.is_connected():
                return browser
        except Exception as e:
            print(e)
            pw.stop() if pw else None
    raise Exception('Browser not connected')


# код пишем тут

"""
Задание 2  - medium
Создайте функцию close_browser, которая принимает на вход номер профиля, объект браузера из Playwright
и объект Playwright, функция должна закрыть браузер.
Должен быть запущен метод browser.close() у объекта браузера из Playwright, если объект браузера не пустой.
Должен быть отправлен запрос на закрытие браузера через API ADS.
Должен быть запущен метод pw.stop() у объекта Playwright.
"""
from playwright.sync_api import sync_playwright, Browser, Playwright
import requests

ads_local_api = "http://local.adspower.net:50325"


def close_browser(profile_number: int, browser: Browser, pw: Playwright) -> None:
    path = '/api/v1/browser/stop'
    params = dict(serial_number=profile_number)
    requests.get(ads_local_api + path, params=params)
    if browser:
        browser.close()
    pw.stop() if pw else None


# код пишем тут

"""
Задание 3  - hard
Напишите класс ADS, который будет принимать на вход номер профиля и иметь следующие аттрибуты:
- profile_number - номер профиля
- _profile_id - защищенный аттрибут, который будет хранить id профиля, изначально None
- _pw - объект Playwright
- _browser - объект браузера из Playwright
- context - объект контекста из Playwright
- page - объект страницы из Playwright

Класс должен иметь следующие методы:
- _run_browser - открывает браузер, с номером профиля в аттрибуте profile_number,
 при помощи методов open_browser и check_browser
- _check_browser - проверяет статус профиля из атрибута profile_number, возвращает данные для подключения к браузеру
- _open_browser - открывает браузер из атрибута profile_number, возвращает данные для подключения к браузеру
- _get_profile_id - запрашивает id профиля из ADS по номеру профиля
- геттер profile_id - возвращает id профиля из атрибута _profile_id, если он есть,
иначе запускает метод _get_profile_id, записывает id профиля в атрибут _profile_id и возвращает его
- магический метод __enter__ - запускает метод _run_browser, кладет объект браузера в аттрибут browser,
объект контекста в аттрибут context, создает новую страницу и кладет ее в аттрибут page, печатает в терминале
информацию о запуске профиля с указанием номера и возвращает объект класса
- магический метод __exit__ - корректно закрывает браузер, печатает в терминале информацию о закрытии профиля
с указанием номера.

Напишите код, который будет использовать класс ADS:
- возьмите список номеров профилей
- в цикле перебирайте номера профилей
- объявите объект класса ADS через контекстный менеджер с номером профиля
- внутри контекстного менеджера напечатайте в терминале id профиля
- запустите метод page.goto('https://google.com') у объекта ads
- ждите паузу 2-3 секунды
- завершите работу с профилем
- перейдите к следующему профилю
 
Скрипт должен запустить все номера профилей, напечатать id профиля и перейти на google.com,
после чего корректно завершить работу с профилями.
В терминале должна быть информация о запуске и завершении работы с профилями
из магических методов __enter__ и __exit__.

Да, вы правильно поняли, вам нужно погуглить как добавить магические методы для работы с контекстным менеджером
в классе и как они работают. Можно работать без них, но иногда они не заменимы, особенно, если нужно закрывать какие-то ресурсы или
подключения.
"""

import time
import random
from playwright.sync_api import sync_playwright, Browser
import requests

class ADS:
    _local_api_url = "http://local.adspower.net:50325"

    def __init__(self, profile_number: int):
        self.profile_number = profile_number
        self._pw = None  # объект Playwright
        self._profile_id = None  # id профиля
        self._browser = None  # объект браузера из Playwright
        self.context = None  # объект контекста из Playwright
        self.page = None  # объект страницы из Playwright

    def _get_profile_id(self) -> str:
        """
        Получает id профиля из ADS по номеру профиля
        :return: id профиля
        """
        path = '/api/v1/user/list'
        params = dict(serial_number=self.profile_number)
        response = requests.get(self._local_api_url + path, params=params).json()
        return response['data']['list'][0]['user_id']

    @property
    def profile_id(self) -> str:
        """
        Возвращает id профиля из атрибута _profile_id
        :return: id профиля
        """
        if not self._profile_id:
            self._profile_id = self._get_profile_id()
        return self._profile_id

    def __enter__(self):
        self.browser = self._run_browser()
        self.context = self.browser.contexts[0]
        self.page = self.context.new_page()
        print(f"Запущен профиль {self.profile_number}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_browser()
        if exc_type is None:
            print(f"Профиль {self.profile_number} завершен успешно")
        else:
            print(f"Профиль {self.profile_number} завершен с ошибкой {exc_val}")
        return True

    def _run_browser(self) -> Browser:
        """
        Открывает браузер, с номером профиля в атрибуте profile_number,
        при помощи методов open_browser и check_browser, делает 3 попытки.
        :return: объект Browser из Playwright
        """
        for _ in range(3):
            try:
                puppeteer = self._check_browser()
                if not puppeteer:
                    puppeteer = self._open_browser()
                self._pw = sync_playwright().start()
                return self._pw.chromium.connect_over_cdp(puppeteer, slow_mo=random.randint(700, 1400))
            except Exception as e:
                print(e)
                self._pw.stop() if self._pw else None
        raise Exception('Browser not connected')

    def _check_browser(self) -> Optional[str]:
        path_status = '/api/v1/browser/active'
        params = dict(serial_number=self.profile_number)
        response = requests.get(self._local_api_url + path_status, params=params).json()
        status = response['data']['status']
        if status == 'Inactive':
            return None
        return response['data']['ws']['puppeteer']

    def _open_browser(self) -> str:
        path = '/api/v1/browser/start'
        params = dict(
            serial_number=self.profile_number,
            open_tabs=1)
        response = requests.get(self._local_api_url + path, params=params).json()
        return response['data']['ws']['puppeteer']

    def _close_browser(self):
        path = '/api/v1/browser/stop'
        params = dict(serial_number=self.profile_number)
        requests.get(self._local_api_url + path, params=params)
        if self._browser:
            self._browser.close()
        self._pw.stop() if self._pw else None


def main():
    profile_numbers = [941, 942, 943]
    for profile_number in profile_numbers:
        with ADS(profile_number) as ads:
            print(ads.profile_id)
            ads.page.goto('https://google.com')
            time.sleep(2)


main()
# код пишем тут
