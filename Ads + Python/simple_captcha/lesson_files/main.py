import tempfile

from twocaptcha import TwoCaptcha
from loguru import logger

from ads import Ads
from config import config


def democaptcha():
    logger.info('Начинаем работу 🚀')
    ads = Ads(profile_number=979)
    ads.open_url('https://democaptcha.com/demo-form-eng/image.html')

    solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)

    image_locator = ads.page.locator('#htest_image')
    image_bytes = image_locator.screenshot()

    with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp_file:
        tmp_file.write(image_bytes)
        tmp_path = tmp_file.name
        response = solver.normal(
            file=tmp_path,
            numeric=4,
            minLen=6,
            caseSensitive=1,
            lang='en',
            hintText='blue symbols only')
        logger.info(f'Распознанная капча: {response}')

    ads.page.locator('[name="message"]').fill('Hello')
    ads.page.locator('#vericode').fill(response['code'])
    ads.page.locator('.btn-install').click()

    # прошли капчу
    solver.report(response['id'], True)






if __name__ == "__main__":
    democaptcha()
