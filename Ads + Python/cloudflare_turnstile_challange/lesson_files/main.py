import os
import shutil

from loguru import logger
import requests
from better_proxy import Proxy
from twocaptcha import TwoCaptcha  # install: pip install 2captcha-python
from patchright.sync_api import sync_playwright, Browser, Page, expect
from fake_useragent import UserAgent

from config import config
from ads import Ads

solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)


def change_ip():
    requests.get(config.LINK_IP_CHANGE)


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



def solve_captcha_request():
    change_ip()

    proxy = Proxy.from_str(config.PROXY)

    user_agent = UserAgent(
        browsers=['Chrome'],
        os=['Mac OS X'],
    ).random

    shutil.rmtree('...')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir="...",
            channel="chrome",
            headless=False,
            no_viewport=True,
            user_agent=user_agent,
            proxy=proxy.as_playwright_proxy,
            slow_mo=1000
        )

        page = browser.new_page()
        page.on("console", lambda msg: print(f"Сообщение консоли: {msg.text}"))
        
        # Чтение содержимого файла render_listener.js
        with open(os.path.join(os.path.dirname(__file__), 'render_listener.js'), 'r') as file:
            script_content = file.read()
            
        # Добавляем init скрипт стандартным способом
        page.add_init_script(
            path=os.path.join(os.path.dirname(__file__), 'render_listener.js')
        )
        page.wait_for_timeout(3000)
        page.goto('https://coinlist.co/login', wait_until='domcontentloaded')

        page.wait_for_timeout(3000)

        try:
            expect(page.get_by_text('Use of the site is subject')).to_be_visible(timeout=10000)
            logger.info('Сайт загрузился успешно')
        except Exception as e:
            if page.get_by_text('Ray ID:').is_visible():
                logger.error('Остались на странице с капчей', e)
                is_script_initialized = page.evaluate('''() => {
                    try {
                        return window.test === 1;
                    } catch (e) {
                        return false;
                    }
                }''', isolated_context=False)
                logger.info(f'is_script_initialized: {is_script_initialized}')
                # TODO: решить капчу через 2captcha

        logger.info('Скачиваем куки')
        cookies = page.context.cookies()
        user_agent = page.evaluate('navigator.userAgent', isolated_context=False)
        logger.info(f'user_agent: {user_agent}')

    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
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

    logger.info(f'response: {response.text}')


def response_example():
    url = 'https://coinlist.co/login'
    response = requests.get(url)

    print(response.text)


if __name__ == "__main__":
    solve_captcha_request()
    # solve_captcha_request()
