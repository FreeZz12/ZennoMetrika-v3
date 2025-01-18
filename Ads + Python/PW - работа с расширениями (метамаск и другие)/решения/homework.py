""""""

"""
Задание 1 - easy

Напишите скрипт, который запускает браузер,
открывает расширение метамаска, авторизуется в кошельке,
выбирает сеть Linea для работы.

"""
password = '12345678'
page = context.new_page()
page.goto('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html')
page.get_by_test_id('unlock-password').fill(password)
page.get_by_test_id('unlock-submit').click()

# код пишем тут

"""
Задание 2  - medium

Напишите функцию select_chain, которая принимает на вход:
- страницу браузера
- название сети

Функция должна выбирать сеть в кошельке метамаск.


"""
from playwright.sync_api import Page
import time


def select_chain(page: Page, chain: str) -> None:
    """
    Выбирает сеть в metamask. Если сеть не найдена, добавляет новую из параметра chain
    :param chain: наименование сети
    :return: None
    """
    page.goto('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html')
    page.get_by_test_id("network-display").wait_for(timeout=5000, state='visible')
    chain_button = page.get_by_test_id("network-display")
    if chain == chain_button.inner_text():
        return

    chain_button.click()
    time.sleep(2)
    enabled_networks = page.locator('div[data-rbd-droppable-id="characters"]')
    if enabled_networks.get_by_text(chain, exact=True).count():
        enabled_networks.get_by_text(chain, exact=True).click()
    else:
        raise ValueError(f"Сеть {chain} не найдена")

# код пишем тут

"""
Задание 3 - hard
Напишите функцию set_chain, которая принимает на вход :
- страницу браузера
- название сети
- словарь с параметрами сети: rpc, chain_id, native_token

Функция должна создавать сеть, если ее нет в списке сетей, и выбирать ее.
"""


def set_chain(page: Page, chain_name: str, chain: dict) -> None:
    """
    Добавляет новую сеть в metamask. Берет параметры из объекта Chain.
    :param chain: объект сети
    :return: None
    """
    page.goto( "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#settings/networks/add-network")
    time.sleep(2)
    try:
        select_chain(page, chain_name)
        return
    except ValueError:
        page.get_by_test_id('network-form-network-name').wait_for(timeout=5000, state='visible')
        page.get_by_test_id('network-form-network-name').fill(chain_name)
        page.get_by_test_id('test-add-rpc-drop-down').click()
        page.get_by_role('button', name='Add RPC URL').click()
        page.get_by_test_id('rpc-url-input-test').fill(chain['rpc'])
        page.get_by_role('button', name='Add URL').click()
        if page.get_by_test_id('network-form-chain-id-error').count():
            raise Exception(
                f"Error: metamask не принимает rpc {chain['rpc']}, попробуйте другой")
        page.get_by_test_id('network-form-chain-id').fill(str(chain['chain_id']))
        page.get_by_test_id('network-form-ticker-input').fill(chain['native_token'])
        page.get_by_role('button', name='Save').click()

    select_chain(page, chain_name)

# код пишем тут

