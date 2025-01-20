from __future__ import annotations

import random
import time
from pprint import pprint
import re

import requests
from playwright.sync_api import sync_playwright, Page, Frame, Browser, Playwright

from playwright.sync_api import sync_playwright


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

    page = start_browser(949)

    page.goto('https://iframetester.com/?url=https://iframetester.com/')

    main_frame = page.main_frame  # основной фрейм страницы

    list_frames = page.frames

    # # поиск фрейма в цикле по точному содержанию url
    # for frame in list_frames:
    #     if 'https://pancakeswap.finance/' == frame.url:
    #         frame.get_by_role('button', name='Connect').first.click()
    #
    # # поиск фрейма в цикле по частичному содержанию url
    # for frame in list_frames:
    #     if 'pancakeswap' in frame.url:
    #         frame.get_by_role('button', name='Connect').first.click()
    #
    #
    # # поиск фрейма в цикле по name
    # for frame in list_frames:
    #     if 'pancakeswap' in frame.name:
    #         frame.get_by_role('button', name='Connect').first.click()

    page.frame(name='google_esf')  # будет искать фрейм по атрибуту name (или id)
    page.frame(name='iframe-window')
    page.frame(url='https://pancakeswap.finance/')  # будет искать фрейм по точному совпадению url
    page.frame(url=re.compile('^https://pancakeswap.*'))  # будет искать фрейм по частичному совпадению

    # поиск фрейма по селектору css или xpath
    page.frame_locator('#google_esf')
    page.frame_locator('#iframe-window').get_by_role('button', name='Connect').first.click()
    page.frame_locator("//div[@class='iframe-container']/iframe").get_by_role('button', name='Connect').first.click()





if __name__ == '__main__':
    main()
