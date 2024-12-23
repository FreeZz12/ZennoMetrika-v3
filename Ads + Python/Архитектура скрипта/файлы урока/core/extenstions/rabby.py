from playwright.sync_api import Page, Browser, Locator

from config.config import rabby_url
from core.ads import Ads
from models.chain import Chain


class Rabby:
    def __init__(self, ads: Ads):
        self.ads = ads

    def auth(self):

        # открываем страницу
        self.ads.page.goto(rabby_url)
        # вводим пароль
        self.ads.page.get_by_test_id('unlock-password').fill(self.ads.account.password_rabby)
        # нажимаем кнопку разблокировки
        self.ads.page.get_by_test_id('unlock-submit').click()


    def confirm(self, locator: Locator):

        with self.ads.browser.contexts[0].expect_page() as page_catcher:
            locator.click()
        metamask_page = page_catcher.value
        metamask_page.get_by_test_id('confirm-btn').click()

    def set_chain(self, chain: Chain):
        print('Setting chain to', chain.name)


    def send_token(self):
        """
        Отправляет токены на биржу
        :param browser_page: объект страницы браузера
        :param sub_address_cex: суб адрес биржи
        :return:
        """
        # открываем метамаск
        self.ads.page.goto(rabby_url)
        # нажимаем кнопку отправки токенов
        self.ads.page.get_by_test_id('send').click()
        # вводим адрес получателя суб адрес биржи
        self.ads.page.get_by_test_id('recipient-address').fill(self.ads.account.sub_address_cex)
        # вводим количество токенов
        self.ads.page.get_by_test_id('maximum').click()
        # нажимаем кнопку далее
        self.ads.page.get_by_test_id('next').click()
        # подтверждаем транзакцию в метамаске
        self.ads.page.get_by_test_id('confirm').click()
