""""""
from playwright.sync_api import Page

"""
Задание 1 - easy

Напишите функцию, которая возвращает UserAgent запущенного браузера.
"""

def get_user_agent(page: Page) -> str:
    return page.evaluate('navigator.userAgent')
# код пишем тут

"""
Задание 2  - medium
Напишите функцию get_ip, которая возвращает ip адрес запущенного браузера.

"""

def get_ip(page: Page) -> str:
    return page.evaluate(
        """
        async () => {
        response = await fetch('https://api.ipify.org?format=json')
        response_json = await response.json()
        return response_json.ip
        }
        """
    )

