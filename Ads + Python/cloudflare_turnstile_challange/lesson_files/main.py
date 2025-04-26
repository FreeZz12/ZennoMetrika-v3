import os
import shutil
import time

from loguru import logger
import requests
from better_proxy import Proxy
from twocaptcha import TwoCaptcha  # install: pip install 2captcha-python
from patchright.sync_api import sync_playwright, expect
from fake_useragent import UserAgent

from config import config
from ads import Ads

solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)




def change_ip(proxy):
    # requests.get(config.LINK_IP_CHANGE)
    response = requests.get('https://api.ipify.org/?format=json', proxies=proxy.as_proxies_dict)
    logger.info(f'IP изменен: {response.text}')
    time.sleep(3)


def solve_captcha_in_ads():
    logger.info("Hello from cloudflare-turnstile-challange!")

    ads = Ads(profile_number=979)

    url = 'https://coinlist.co/login'

    logger.info(f'Зашли на страницу {url}')

    ads.page.add_init_script(
        path=os.path.join(os.path.dirname(__file__), 'render_listener.js')
    )

    ads.open_url(url)

    logger.info('Ждем пока скрипт запустится')

    turnstile_params = ads.page.evaluate('window.turnParams')

    logger.info(f'turnstile_params: {turnstile_params}')

    captcha_response = solver.turnstile(
        sitekey=turnstile_params['sitekey'],
        url=turnstile_params['pageurl'],
        useragent=turnstile_params['userAgent'],
        action=turnstile_params['action'],
        data=turnstile_params['cData'],
        pagedata=turnstile_params['chlPageData'],
        proxy={'type': 'HTTPS', 'uri': config.PROXY},
    )
    logger.info(f'captcha_response: {captcha_response}')

    ads.page.evaluate(f'window.cfCallback("{captcha_response["code"]}")')

    logger.success('Капча решена')

    cookies = ads.context.cookies('https://coinlist.co/login')

    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://coinlist.co/login',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"124.0.6367.119"',
        'sec-ch-ua-full-version-list': '"Chromium";v="124.0.6367.119", "Google Chrome";v="124.0.6367.119", "Not-A.Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-platform-version': '"12.6.5"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': turnstile_params['userAgent'],
    }

    proxy = {
        'http': f'http://{config.PROXY}',
        'https': f'http://{config.PROXY}',
    }

    response = requests.get('https://coinlist.co/login',
                            cookies=cookies_dict, headers=headers, proxies=proxy)

    logger.info(f'response: {response.text}')



def get_cookies_and_headers(proxy) -> tuple[dict, str]:
    user_agent = UserAgent(
        browsers=['Chrome', 'Yandex Browser'],
        os=['Mac OS X'],
    ).random

    if os.path.exists('temp'):
        shutil.rmtree('temp')

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir="temp",
            channel="chrome",
            headless=True,
            no_viewport=True,
            user_agent=user_agent,
            proxy=proxy.as_playwright_proxy,
            slow_mo=1000,
        )
        page = context.new_page()


        page.goto('https://coinlist.co/login')
    
        for _ in range(10):
            if not page.get_by_text('Ray ID:').is_visible():
                break
            logger.info('Находимся на странице с Ray ID')
            page.wait_for_timeout(1000)
        else:
            logger.error('Остались на странице с капчей')
            return None, None
        
        page.wait_for_timeout(3000)
        page.wait_for_load_state('load')

        expect(page.get_by_text("Don't have a CoinList account?")).to_be_visible(timeout=5000)

        logger.info('Сайт загрузился успешно')

        logger.info('Скачиваем куки')
        cookies = page.context.cookies()
        user_agent = page.evaluate('navigator.userAgent', isolated_context=False)
        logger.info(f'user_agent: {user_agent}')
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        return cookies_dict, user_agent




def solve_captcha_request():
    proxy = Proxy.from_str(config.PROXY)
    # change_ip(proxy)

    for _ in range(10):
        cookies_dict, user_agent = get_cookies_and_headers(proxy)
        if cookies_dict and user_agent:
            break
        logger.info('Попытка получить куки и user_agent')
        time.sleep(1)

    logger.info(f'cookies_dict: {cookies_dict}')
    logger.info(f'user_agent: {user_agent}')



    logger.info(f'cookies_dict: {cookies_dict}')

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://coinlist.co/login',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"124.0.6367.119"',
        'sec-ch-ua-full-version-list': '"Chromium";v="124.0.6367.119", "Google Chrome";v="124.0.6367.119", "Not-A.Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-platform-version': '"12.6.5"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent
    }


    response = requests.get('https://coinlist.co/login',
                            cookies=cookies_dict, headers=headers, proxies=proxy.as_proxies_dict)

    logger.info(f'Запрос пробил капчу: {"t have a CoinList account?" in response.text}')



def response_example():
    url = 'https://coinlist.co/login'
    response = requests.get(url)

    print(response.text)


if __name__ == "__main__":
    solve_captcha_request()
    # solve_captcha_in_ads()
