""""""

"""
Задание 1 - easy

Откройте https://localapi-doc-en.adspower.com/.
Напишите запрос поискового метода Playwright, который будет находить все видимые элементы a на странице.

"""

# код пишем тут

import requests
from playwright.sync_api import sync_playwright


def open_browser(profile_number: int) -> dict:
    params = dict(serial_number=profile_number)
    url = "http://local.adspower.net:50325/api/v1/browser/start"
    response = requests.get(url, params=params)
    data = response.json()
    return data



profile_data = open_browser(941)
url_connect = profile_data.get('data').get('ws').get('puppeteer')
pw = sync_playwright().start()
browser = pw.chromium.connect_over_cdp(url_connect)
if not browser.is_connected():
    print("Browser not connected")
    exit(1)
context = browser.contexts[0]
page = context.pages[0]
page.goto("https://localapi-doc-en.adspower.com/")
page.locator("a:visible").highlight()

"""


Задание 2 - medium


Откройте https://localapi-doc-en.adspower.com/.
Напишите запросы, используя поисковые методы PlayWright,
для нахождения элемента span с текстом "API Overview"
1. Используя метод locator() + xpath
2. Используя метод get_by_text()

"""
# ищем по xpath
page.goto("https://localapi-doc-en.adspower.com/")
xpath = "//span[text()='API Overview']"
page.locator(xpath).highlight()

# ищем по тексту
page.goto("https://localapi-doc-en.adspower.com/")
page.get_by_text("API Overview").highlight()

"""
Задание 3  - hard

Напишите скрипт, который будет открывать страницу расширения метамаск
по ссылке chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#unlock
вводит пароль при помощи метода fill(text), и нажимает кнопку "Unlock".
"""
page.goto("chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#unlock")
password = '1234678'
page.get_by_test_id("unlock-password").fill(password)
page.get_by_test_id("unlock-page").click()
