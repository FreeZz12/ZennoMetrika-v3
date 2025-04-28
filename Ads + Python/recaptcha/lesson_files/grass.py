import json
import time
from loguru import logger
import requests
from better_proxy import Proxy
from web3 import Web3
from twocaptcha import TwoCaptcha  # pip install 2captcha-python
from fake_useragent import UserAgent

from config import config
from ads import Ads


def get_valid_address():
    w3 = Web3(Web3.HTTPProvider('https://1rpc.io/eth'))
    while True:
        block = w3.eth.get_block('latest')
        transactions = block.transactions
        for transaction_hash in transactions:
            transaction = w3.eth.get_transaction(transaction_hash)
            balance = w3.eth.get_balance(transaction['from'])
            if balance > 0.001 * 1e18:
                return transaction['from']


def change_ip():
    requests.get(config.LINK_IP_CHANGE)


def main():
    change_ip()
    twocaptcha = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    url = 'https://app.getgrass.io/register'
    site_key = '6LeeT-0pAAAAAFJ5JnCpNcbYCBcAerNHlkK4nm6y'

    ads = Ads(979)
    ads.open_url(url)

    cookie_accept = ads.page.get_by_role('button', name='ACCEPT ALL')
    if cookie_accept.is_visible():
        cookie_accept.click()

    ads.page.get_by_placeholder('Email').fill('test@test.com')
    ads.page.locator('.chakra-checkbox__control').nth(0).click()
    ads.page.locator('.chakra-checkbox__control').nth(1).click()

    user_agent = ads.page.evaluate('navigator.userAgent')
    token = twocaptcha.recaptcha(
        site_key,
        url,
        userAgent=user_agent,
        proxy={'type': 'HTTPS', 'uri': config.PROXY},
    )['code']

    logger.info(f'Token: {token}')
    script = open('lesson_files/callback_finder.js', 'r').read()
    ads.page.evaluate(script, token)

    ads.page.get_by_role('button', name='Continue').click()


def response():
    twocaptcha = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    url = 'https://app.getgrass.io/register'
    user_agent = UserAgent().random

    site_key = '6LeeT-0pAAAAAFJ5JnCpNcbYCBcAerNHlkK4nm6y'
    token = twocaptcha.recaptcha(
        site_key,
        url,
        userAgent=user_agent,
        proxy={'type': 'HTTPS', 'uri': config.PROXY},
    )['code']
    logger.info(f'Token: {token}')
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://app.grass.io',
        'priority': 'u=1, i',
        'referer': 'https://app.grass.io/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': user_agent,
    }

    data = {
        "email": "admin3@gmail.com",
        "referralCode": "",
        "marketingEmailConsent": True,
        "recaptchaToken": token,
        "termsAccepted": True,
        "page": "register"
    }

    proxies = {
        'http': f'http://{config.PROXY}',   
        'https': f'http://{config.PROXY}',
    }
    response = requests.post(
        'https://api.getgrass.io/sendOtp', headers=headers, data=json.dumps(data), proxies=proxies)
    print(response.text)


if __name__ == "__main__":
    response()
