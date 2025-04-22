import requests
import base64

import tempfile
from loguru import logger
from twocaptcha import TwoCaptcha # type: ignore
from bs4 import BeautifulSoup # type: ignore


from config import config


def captcha_com():

    solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)

    logger.info('Начинаем работу 🚀')

    session_url = 'https://captcha.com/demos/features/captcha-demo.aspx'

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'host': 'captcha.com',
        'origin': 'https://captcha.com',
        'referer': 'https://captcha.com/demos/features/captcha-demo.aspx',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    })
    response = session.get(session_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    captcha_id = soup.find('input', {'id': 'BDC_VCID_demoCaptcha'})['value']
    logger.info(f'Получен ID капчи: {captcha_id}')

    url = f'https://captcha.com/forms/captcha-demo-features/captcha-endpoint.php?get=base64-image-data&c=demoCaptcha&t={captcha_id}'
    response = session.get(url)

    # Получаем base64-строку из ответа
    base64_data = response.text

    # Проверяем, содержит ли ответ префикс data:image
    if 'data:image' in base64_data:
        # Удаляем префикс (data:image/png;base64,)
        base64_data = base64_data.split(',')[1]

    # Декодируем base64 в байты
    image_bytes = base64.b64decode(base64_data)

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(image_bytes)
        tmp_path = tmp_file.name
        logger.info(f'Путь к изображению: {tmp_path}')
        response = solver.normal(
            file=tmp_path,
            numeric=4,
            lang='en'
        )

    logger.info(f'Распознанная капча: {response}')
    submit_url = 'https://captcha.com/forms/captcha-demo-features/submit-process.php'
    payload = {
        'captchaCode': response['code'],
        'captchaId': captcha_id,
        'validateCaptchaButton': 'true'
    }
    logger.debug(f'payload: {payload}')
    response = session.post(submit_url, data=payload)
    logger.info(f'Ответ от сервера: {response.text}')
