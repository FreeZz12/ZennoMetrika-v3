import requests
from playwright.sync_api import Page, Browser, sync_playwright

from models.account import Account


class Ads:
    def __init__(self, account: Account):
        """
        Инициализация объекта Ads
        :param account: объект аккаунта
        """
        self.account = account
        self.browser = self.open_browser()
        self.context = self.browser.contexts[0]
        self.page = self.context.new_page()

    def open_browser(self) -> Browser:
        """
        Открывает браузер по определенному профилю
        :param profile_number: номер профиля
        :return: объект страницы браузера
        """
        # api адрес для запуска браузера
        ads_local_api = 'http://local.adspower.net:50325/api/v1/browser/start'

        # параметры для запуска браузера по определенному профилю
        params = dict(serial_number=self.account.profile_number)
        # отправка запроса на запуск браузера
        response = requests.get(ads_local_api, params=params)

        # вывод ответа
        print(response.text)

        # получение данных из ответа
        endpoint = response.json()['data']['ws']['puppeteer']

        # создание объекта playwright
        pw = sync_playwright().start()
        # подключение playwright к браузеру
        browser = pw.chromium.connect_over_cdp(endpoint)

        return browser
