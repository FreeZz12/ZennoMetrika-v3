
import json
import time
from config import config
from ads import Ads
import secrets

from twocaptcha import TwoCaptcha  # 2captcha-python
from loguru import logger

from console import init_logger


init_logger()


def riselabs_callback(ads: Ads):
    solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    logger.info('Запускаем скрипт riselabs🔥')
    url = 'https://faucet.testnet.riselabs.xyz'

    ads.open_url(url)

    site_key = ads.page.locator('#cf-turnstile').get_attribute('data-sitekey')
    logger.info(f'Сайт ключ: {site_key}')

    result = solver.turnstile(site_key, url)
    logger.info(f'Результат: {json.dumps(result, indent=4)}')

    ads.page.evaluate(f'onTurnstileSuccess("{result["code"]}")')

    time.sleep(3)

    ads.page.get_by_role('button', name='Request Token').click()


def riselabs_insert_input(ads: Ads):
    solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    logger.info('Запускаем скрипт riselabs🔥')
    url = 'https://faucet.testnet.riselabs.xyz'

    ads.open_url(url)

    site_key = ads.page.locator('#cf-turnstile').get_attribute('data-sitekey')
    logger.info(f'Сайт ключ: {site_key}')

    result = solver.turnstile(site_key, url)
    logger.info(f'Результат: {json.dumps(result, indent=4)}')

    ads.page.evaluate(
        f'document.getElementsByName("cf-turnstile-response")[0].value = "{result["code"]}"')

    time.sleep(3)

    ads.page.get_by_role('button', name='Request Token').click()


def riselabs_create_event(ads: Ads):
    solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    logger.info('Запускаем скрипт riselabs🔥')
    url = 'https://faucet.testnet.riselabs.xyz'

    ads.open_url(url)

    site_key = ads.page.locator('#cf-turnstile').get_attribute('data-sitekey')
    logger.info(f'Сайт ключ: {site_key}')

    result = solver.turnstile(site_key, url)
    logger.info(f'Результат: {json.dumps(result, indent=4)}')

    widget_id_element = ads.page.locator('[name="cf-turnstile-response"]')
    widget_id_full = widget_id_element.get_attribute('id')  
    widget_id = widget_id_full.split('-')[-1].split('_')[0]

    event_data = {
        'chlId': secrets.token_hex(8),
        'event': 'complete',
        'source': 'cloudflare-challenge',
        'token': result['code'],
        'widgetId': widget_id
    }

    # отправляем событие
    ads.page.evaluate('''
        (event_data) => {
            const event = new MessageEvent(
                "message",
                {
                    data: event_data,
                    origin: "https://challenges.cloudflare.com"
                }
            )
            window.dispatchEvent(event)
        }''', event_data)


    time.sleep(3)

    ads.page.get_by_role('button', name='Request Token').click()


def main():
    logger.info('Запускаем скрипт 🔥')
    profile_number = 979

    ads = Ads(profile_number=profile_number)
    logger.info(f'Запустили профиль {profile_number}')

    riselabs_create_event(ads)


if __name__ == '__main__':
    main()


"""
logger.info(f'Сайт ключ: {site_key}')

solved_captcha = solver.turnstile(site_key, url)
logger.info(f'Решенный капча: {solved_captcha}')
captcha_solved_token = solved_captcha['code']
ads.page.evaluate(f'onTurnstileSuccess("{captcha_solved_token}")')

logger.success('Работа скрипта завершена успешно!')

"""
