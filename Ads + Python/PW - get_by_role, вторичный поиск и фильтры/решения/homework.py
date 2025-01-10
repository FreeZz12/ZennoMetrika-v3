""""""
import time

"""
Задание 1 - easy

Напишите вызовы метода get_by_role для поиска элементов на странице:
1. <button>Connect Wallet</button>
2. <input placeholder="0">
3. <input type="checkbox"></input>
4. <a href="https://google.com">Google</a>
5. <div role="dialog">Some Box</div>

Потренироваться можно тут: https://cdpn.io/cpe/boomboom/index.html?key=index.html-d99af6be-f89a-15f1-4fe5-427f6ecdd20b
"""
page.get_by_role("button", name="Connect Wallet")
page.get_by_role("texbox")
page.get_by_role("checkbox")
page.get_by_role("link", name="Google")
page.get_by_role("dialog", name="Some Box")


"""
Задание 2  - medium
Напишите скрипт, который будет открывать сайт https://pancakeswap.finance/,
нажимать на кнопку "Connect Wallet" , в открывшемся окне выбирать "Metamask".
Скрипт должен учитывать ситуацию когда кошелек уже подключен.

"""

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
page.goto("https://pancakeswap.finance/")
button_connect = page.get_by_role("button", name="Connect Wallet")
if button_connect.count():
    button_connect.click()
    page.get_by_text("Metamask").first.click()


# код пишем тут

"""
Задание 3 - hard
Напишите скрипт, который будет создавать новый кошелек в MetaMask.
Для получения текста из элемента используйте метод inner_text.
Для заполнения полей используйте метод fill.
"""

# код пишем тут

from playwright.sync_api import Page

def create_wallet(page: Page) -> tuple[str, str]:
    """
    Создает кошелек в metamask, возвращает адрес кошелька, seed фразу и пароль в виде кортежа.
    :return: tuple (seed, password)
    """
    metamask_url = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"

    page.goto(metamask_url)

    page.get_by_test_id('onboarding-terms-checkbox').click()
    page.get_by_test_id('onboarding-create-wallet').click()
    page.get_by_test_id('metametrics-no-thanks').click()

    # генерируем пароль и вводим в 2 поля
    password = 'qwerty12345'
    
    page.get_by_test_id('create-password-new').fill(password)
    page.get_by_test_id('create-password-confirm').fill(password)
    page.get_by_test_id('create-password-terms').click()
    page.get_by_test_id('create-password-wallet').click()

    page.get_by_test_id('secure-wallet-recommended').click()
    page.get_by_test_id('recovery-phrase-reveal').click()

    seed = []
    for i in range(12):
        test_id = f"recovery-phrase-chip-{i}"
        word = page.get_by_test_id(test_id).inner_text()
        seed.append(word)

    page.get_by_test_id('recovery-phrase-next').click()
    for i in range(12):
        if page.get_by_test_id(f'recovery-phrase-input-{i}').count():
            page.get_by_test_id(f'recovery-phrase-input-{i}').fill(seed[i])
    page.get_by_test_id('recovery-phrase-confirm').click()
    time.sleep(3)
    page.get_by_test_id('onboarding-complete-done').click()
    page.get_by_test_id('pin-extension-next').click()

    seed_str = " ".join(seed)

    return seed_str, password


