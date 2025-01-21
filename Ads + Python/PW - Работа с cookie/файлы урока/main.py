from __future__ import annotations

import random
import time
from pprint import pprint
import re

import requests
from playwright.sync_api import sync_playwright, Page, Frame, Browser, Playwright

from playwright.sync_api import sync_playwright
from typing_extensions import TypedDict


def start_browser(profile_number: int) -> Page:
    profile_data = open_browser(profile_number)
    url_connect = profile_data.get('data').get('ws').get('puppeteer')
    time.sleep(2)
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(url_connect, slow_mo=random.randint(800, 1200))
    if not browser.is_connected():
        print("Browser not connected")
        exit(1)
    context = browser.contexts[0]
    return context.new_page()

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


def dump_frame_tree(frame: Frame, indent: str = "") -> None:
    """
    Рекурсивно выводит дерево фреймов, необходимо передать main_frame.
    :param frame: фрейм
    :param indent: отступ
    :return: None
    """
    print(indent + frame.name + '@' + frame.url)
    for child in frame.child_frames:
        dump_frame_tree(child, indent + "    ")


def main():

    page = start_browser(948)

    page.goto('x.com')

    auth_token = '2e5282ab5c9d18c399edf4de398c14f4e637aca9'

    cookies_all = page.context.cookies()
    cookies_with_url = page.context.cookies(urls="https://iframetester.com/")
    cookie_value = cookies_all[0]['value']


    page.context.add_cookies(
        [
            {
                "name": "auth_token",
                "value": auth_token,
                "domain": ".x.com",
                "path": "/",
                "expires": int(time.time()) + 3600,
                "httpOnly": True,
                "secure": True,
                "sameSite": 'None',
            },
        ]
    )
    page.context.clear_cookies(name="auth_token", domain=".x.com", path="/")







if __name__ == '__main__':
    main()
