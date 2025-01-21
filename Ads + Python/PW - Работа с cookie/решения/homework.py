""""""
import time
from playwright.sync_api import Page

"""
Задание 1 - medium

Напишите функцию auth_x, которая принимает на вход 2 аргумента:
1. page: Page - объект страницы
2. token: str - токен для авторизации

Функция должна, добавлять куки авторизации для сайта x.com в контекст браузера,
со сроком жизни 1 год.

"""

def auth_x(page: Page, token: str):
    page.context.add_cookies(
        [
            {
                "name": "auth_token",
                "value": token,
                "domain": ".x.com",
                "path": "/",
                "expires": int(time.time()) + 3600*24*365,
                "httpOnly": True,
                "secure": True,
                "sameSite": 'None',
            },
        ]
    )