""""""
from typing import Optional

"""
Задание 1 - easy

Напишите функцию open_url, которая принимает на вход URL и объект page из Playwright 
и открывает переданный URL в переданном объекте page, если URL равен уже открытому URL на странице,
то функция ничего не делает.

 
"""

# код пишем тут
from playwright.sync_api import Page


def open_url(url: str, page: Page) -> None:
    if url == page.url:
        return
    page.goto(url, wait_until='load')


"""
Задание 2  - medium
Напишите функцию page_catcher, которая принимает на вход объект BrowserContext из Playwright и
объект Locator из Playwright, который содержит в себе локатор элемента на странице.
Функция должна поймать открывающуюся страницу, при нажатии на переданный элемент и вернуть объект
page новой страницы.
"""
from playwright.sync_api import Locator, Page, BrowserContext


def page_catcher(context: BrowserContext, locator: Locator) -> Page:
    """
    Ловец открывающихся страниц при нажатии на элемент.
    :param context: контекст браузера
    :param locator: элемент на странице, который открывает новую страницу
    :return: объект новой страницы
    """
    with context.expect_page() as page_info:
        locator.click()
    return page_info.value


# код пишем тут

"""
Задание 3 - hard
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
- метод prepare_browser - при запуске метода, должны закрыться все открытые вкладки, кроме той, которая лежит
в атрибуте page. (будьте осторожны с системными вкладками расширений) 
- _get_profile_id - запрашивает id профиля из ADS по номеру профиля
- геттер profile_id - возвращает id профиля из атрибута _profile_id, если он есть,
иначе запускает метод _get_profile_id, записывает id профиля в атрибут _profile_id и возвращает его
- магический метод __enter__ - запускает метод _run_browser, кладет объект браузера в аттрибут browser,
объект контекста в аттрибут context, создает новую страницу и кладет ее в аттрибут page, печатает в терминале
информацию о запуске профиля с указанием номера и возвращает объект класса.
- магический метод __exit__ - корректно закрывает браузер, печатает в терминале информацию о закрытии профиля
с указанием номера.
- метод open_url - открывает переданный URL в объекте page, если URL уже открыт, то ничего не делает
- метод page_catcher - принимает объект Locator из Playwright, который содержит в себе локатор элемента на странице,
метод должен поймать открывающуюся страницу, при нажатии на переданный элемент и вернуть объект page новой страницы.
- метод reload_context - открывает новую страницу и сразу же закрывает её, тем самым принудительно обновляя
список открытых вкладок в контексте браузера.
- метод find_page - находит страницу по тексту в URL в контексте браузера, если страница не найдена, возвращает None
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

    def prepare_browser(self):
        for page in self.context.pages:
            if page.url == self.page.url:
                continue
            if 'offscreen' in page.url:  # пропускаем системные вкладки расширений
                continue
            page.close()

    def open_url(self, url: str):
        if url == self.page.url:
            return
        self.page.goto(url, wait_until='load')

    def page_catcher(self, locator):
        with self.context.expect_page() as page_info:
            locator.click()
        return page_info.value

    def reload_context(self):
        page = self.context.new_page()
        page.close()

    def find_page(self, url_text: str):
        for page in self.context.pages:
            if url_text in page.url:
                return page
        return None