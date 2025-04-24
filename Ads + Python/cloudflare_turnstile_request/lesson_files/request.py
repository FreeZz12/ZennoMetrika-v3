
import random
import time


from fake_useragent import UserAgent  # pip install fake-useragent
import requests  # pip install requests
from better_proxy import Proxy  # pip install better-proxy
from twocaptcha import TwoCaptcha  # pip install 2captcha-python
from loguru import logger  # pip install loguru

from config import config

solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)

cache_ip = ['']

def change_ip() -> None:
    try:
        requests.get(config.LINK_IP_CHANGE, timeout=5)
    except Exception:
        pass

def check_unique_ip(proxy: Proxy) -> bool:
    response = requests.get(
        'https://api.ipify.org?format=json', proxies=proxy.as_proxies_dict)
    logger.info(f'IP адрес: {response.text}')
    ip = response.json()['ip']
    last_ip = cache_ip[-1]
    cache_ip.append(ip)
    if ip == last_ip:
        logger.error('IP адрес не изменился')
        return False
    return True



def riselabs_request():
    logger.info('Запускаем скрипт riselabs🔥')

    url = 'https://faucet.testnet.riselabs.xyz'
    site_key = '0x4AAAAAABDerdTw43kK5pDL'
    proxy = Proxy.from_str(config.PROXY)  # format login:password@ip:port
    user_agent = UserAgent(
        browsers=['Chrome'],
        os=['Mac OS X'],
    ).random
    change_ip()

    if not check_unique_ip(proxy):
        time.sleep(10)
        return

    headers = {
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,th;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://faucet.testnet.riselabs.xyz',
        'priority': 'u=1, i',
        'referer': 'https://faucet.testnet.riselabs.xyz/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "YaBrowser";v="25.2", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': user_agent,
    }

    result = solver.turnstile(
        site_key,
        url,
        useragent=user_agent,
        proxy={'type': 'HTTPS', 'uri': config.PROXY}
    )
    token = result['code']
    logger.info(f'Токен: {token[:10]}...{token[-10:]}')

    payload = {
        'address': '0x' + ''.join(random.choices('0123456789abcdef', k=40)),
        'turnstileToken': token,
        'tokens': [
            'ETH',
        ]}

    response = requests.post(
        'https://faucet-api.riselabs.xyz/faucet/multi-request',
        headers=headers,
        json=payload,
        proxies=proxy.as_proxies_dict
    )
    logger.info(f'Ответ: {response.text}')

    logger.success('Работа скрипта завершена успешно!')

    ""


def main():
    while True:
        riselabs_request()

if __name__ == '__main__':
    main()
