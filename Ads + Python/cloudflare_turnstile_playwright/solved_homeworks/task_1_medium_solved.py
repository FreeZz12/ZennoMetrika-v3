
"""
Написать скрипт, который будет решать каптчу на
сайте https://www.accessify.com/contact/
через ads + playwright

"""
# решение задачи

import time

import requests
from config import config
from ads import Ads

from twocaptcha import TwoCaptcha
from loguru import logger

solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)


def accessify(ads: Ads):
    logger.info('Запускаем скрипт accessify🔥')
    url = 'https://www.accessify.com/contact/'

    ads.open_url(url)

    site_key = ads.page.locator(
        '.cf-turnstile').first.get_attribute('data-sitekey')
    logger.info(f'Сайт ключ: {site_key}')

    ads.page.get_by_label('Name').fill('some name')
    ads.page.get_by_label('Email Address').fill('admin@gmail.com')
    ads.page.get_by_label('Page URL to remove').fill('https://coinlist.co/login')
    ads.page.get_by_label('Message').fill('some message')

    solved_captcha = solver.turnstile(site_key, url)
    logger.info(f'Решенный капча: {solved_captcha}')
    captcha_solved_token = solved_captcha['code']
    ads.page.evaluate(
        f"document.getElementsByName('cf-turnstile-response')[0].setAttribute('value', '{captcha_solved_token}');")
    ads.page.get_by_role('button', name='Send Message').click()



def main():
    logger.info('Запускаем скрипт 🔥')
    profile_number= 979

    ads= Ads(profile_number=profile_number)
    logger.info(f'Запустили профиль {profile_number}')
    accessify(ads)





if __name__ == '__main__':
    main()
