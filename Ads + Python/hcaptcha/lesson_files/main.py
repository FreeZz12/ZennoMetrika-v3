import os
import random
import time
from loguru import logger
import requests
from twocaptcha import TwoCaptcha

from ads import Ads
from config import config


class SolverCaptcha:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.solvecaptcha.com'

    def hcaptcha(
            self,
            site_key: str,
            page_url: str,
            invisible: int = 1
    ) -> dict | None:
        task_id = self._create_task(page_url, site_key, 'hcaptcha', invisible)
        result = self._get_task_result(task_id)
        if result is None:
            logger.error('Не удалось решить капчу')
            raise Exception('Не удалось решить капчу')

        if result['status'] == 1:
            return result
        else:
            logger.error(f'Не удалось решить капчу: {result}')
            raise Exception('Не удалось решить капчу')

    def _create_task(
            self,
            page_url: str,
            site_key: str,
            method: str,
            invisible: int = 1
    ):
        params = {
            'key': self.api_key,
            'method': method,
            'sitekey': site_key,
            'pageurl': page_url,
            'invisible': invisible,
            'json': 1
        }
        r = requests.get(self.base_url + '/in.php', params=params)
        logger.info(r.text)

        return r.json()['request']

    def _get_task_result(self, task_id: str) -> dict | None:
        params = {
            "key": self.api_key,
            "action": 'get',
            "id": task_id,
            "json": 1
        }
        for _ in range(20):
            time.sleep(10)
            r = requests.get(self.base_url + '/res.php', params=params)
            try:
                data = r.json()
                if data.get('status', 0) == 1:
                    return data
                elif data.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                    return None
                elif data.get('request') == 'CAPCHA_NOT_READY':
                    logger.info('Капча еще не решена')
            except:
                logger.error(f'Ошибка при получении результата: {r.text}')
                return None


def main():
    ads = Ads('979')
    solver = SolverCaptcha(config.SOLVECAPTCHA_API_KEY)
    two_captcha_solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    random_wallet = '0x' + ''.join(random.choices('0123456789abcdef', k=40))
    site_key = '0a76a396-7bf6-477e-947c-c77e66a8222e'
    url = 'https://faucet-2.seismicdev.net'
    ads.open_url(url)
    ads.page.get_by_placeholder(
        'Enter your address or ENS name').fill(random_wallet)
    # try:
    #     captcha_data = solver.solve_captcha(site_key, url)
    # except Exception as e:
    #     logger.error(f'Не удалось решить капчу: {e}')
    captcha_data = two_captcha_solver.hcaptcha(site_key, url, invisible=1)
    logger.info('Капча решена')
    token = captcha_data['request']
    ads.page.get_by_role('button', name='Request').click()
    script = open(os.path.join(os.path.dirname(__file__), 'inject_hcaptcha.js'), 'r').read()
    ads.page.wait_for_timeout(3000)
    ads.page.evaluate(script, token)
    logger.info('Капча введена')
    time.sleep(10)
    print()


if __name__ == "__main__":
    main()
