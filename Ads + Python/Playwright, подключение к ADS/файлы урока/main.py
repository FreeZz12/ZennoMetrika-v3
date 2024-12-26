import random
import time
from pprint import pprint

import requests
from playwright.sync_api import sync_playwright


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
    for _ in range(3):
        profile_data = open_browser(941)
        url_connect = profile_data.get('data').get('ws').get('puppeteer')
        time.sleep(3)
        pw = sync_playwright().start()
        try:
            browser = pw.chromium.connect_over_cdp(url_connect, slow_mo=random.randint(800, 1200))
            if not browser.is_connected():
                print("Browser not connected")
                exit(1)
            context = browser.contexts[0]
            page = context.new_page()
        except Exception as e:
            pw.stop() if pw else None

        if not browser.is_connected():
            browser.close()

        close_browser(941)
        pw.stop() if pw else None
















if __name__ == '__main__':
    main()