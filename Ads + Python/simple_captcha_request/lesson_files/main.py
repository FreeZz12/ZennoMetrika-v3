import base64
import json

from datetime import datetime
from loguru import logger # loguru
from twocaptcha import TwoCaptcha # 2captcha-python
import requests # requests


from config import config



def dawn():
    logger.info('Начинаем работу dawn 🚀')
    app_id = '680736b078b502263dc58be4'

    def _get_captcha_id() -> str:
        url = 'https://ext-api.dawninternet.com/chromeapi/dawn/v1/puzzle/get-puzzle'
        params = {
            'appid': app_id,
        }
        response = requests.get(url, params=params)
        return response.json()['puzzle_id']

    def _get_captcha_image(captcha_id: str) -> str:
        url = 'https://ext-api.dawninternet.com/chromeapi/dawn/v1/puzzle/get-puzzle-image'
        params = {
            'appid': app_id,
            'puzzle_id': captcha_id,
        }
        response = requests.get(url, params=params)
        return response.json()['imgBase64']

    def get_auth_token(answer: str, captcha_id: str) -> str:
        url = 'https://ext-api.dawninternet.com/chromeapi/dawn/v1/user/login/v2'
        params ={
            'appid': app_id,
        }
        payload = {
            "username": "zarevlesson@gmail.com",
            "password": "12345678",
            "logindata": {
                "_v": {
                "version": "1.1.5"
                },
                "datetime": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            },
            "puzzle_id": captcha_id,
            "ans": answer,
            "appid": app_id
            }
        response = requests.post(url, params=params, json=payload)
        logger.info(f'Ответ от сервера: {json.dumps(response.json(), indent=4)}')
        return response.json()['data']['token']
    
    def get_point(auth_key: str):
        url = 'https://ext-api.dawninternet.com/api/atom/v1/userreferral/getpoint'
        params = {
            'appid': app_id
        }
        headers = {
            'authorization': f'Bearer {auth_key}'
        }
        response = requests.get(url, params=params, headers=headers)
        print(json.dumps(response.json(), indent=4))
        return response.json()


    captcha_id = _get_captcha_id()
    logger.info(f'Получен ID капчи: {captcha_id}')
    captcha_image_base64 = _get_captcha_image(captcha_id)
    with open('captcha.png', 'wb') as f:
        f.write(base64.b64decode(captcha_image_base64))

    solver = TwoCaptcha(config.TWO_CAPTCHA_API_KEY)
    response = solver.normal(
        file='captcha.png',
        numeric=4,
        lang='en'
    )
    logger.info(f'Распознанная капча: {response}')
    auth_token = get_auth_token(response['code'], captcha_id)


    point_data = get_point(auth_token)



def main():
    dawn()


if __name__ == "__main__":
    main()
