import random
import time
from pprint import pprint

import requests
from playwright.sync_api import sync_playwright, Page

from playwright.sync_api import sync_playwright


# Используйте идентификатор вашего расширения и путь к всплывающему окну


def open_browser(profile_number: int) -> dict:
    params = dict(serial_number=profile_number)
    url = "http://local.adspower.net:50325/api/v1/browser/start"
    response = requests.get(url, params=params)
    data = response.json()
    return data


def close_browser(profile_number: int) -> dict:
    params = dict(serial_number=profile_number)
    url = "http://local.adspower.net:50325/api/v1/browser/stop"
    response = requests.get(url, params=params)
    data = response.json()
    return data


def main():
    profile_data = open_browser(949)
    url_connect = profile_data.get('data').get('ws').get('puppeteer')
    time.sleep(3)
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(url_connect, slow_mo=random.randint(800, 1200))
    if not browser.is_connected():
        print("Browser not connected")
        exit(1)
    context = browser.contexts[0]
    page = context.new_page()
    page.goto('https://pancakeswap.finance/')
    page.get_by_role('button', name='Connect').first.click()
    with context.expect_page() as page_catcher:
        page.get_by_text('Metamask').first.click()
    metamask_page = page_catcher.value
    metamask_page.wait_for_load_state(state='load')
    metamask_page.get_by_test_id('confirm-btn').click()

    # открывает те расширения, которые нужны для работы
    # настройка расширений для конкретной работы
    # если работа с кошельком:
     # авторизация в кошельке
     # настройка кошелька для работы BSC
     # меняем счет в кошельке на нужный
    # открываем сайт
    # подключаем кошелек к сайту
    # делаем активность
    # Меняем сеть в кошельке
    # подключаем кошелек к другому сайту
    # выберу счет 1


    pass


if __name__ == '__main__':
    main()
