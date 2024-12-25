import datetime
import json
import time

import requests

ads_local_api = 'http://localhost:50325'

# # Тестовый запрос на получение статуса ADS Local API
# path = '/status'
# params = dict()
# response = requests.get(ads_local_api+path, params=params)
# print(response.text)

# Открыть профиль
"""
--blink-settings=imagesEnabled=false  # Отключить загрузку изображений
--window-position=0,0 # Позиция окна
--window-size=1920,1080 # Размер окна
--start-maximized # Открыть в максимальном размере
--disable-notifications # Отключить уведомления
--lang=en # Язык интерфейса
"""


#
# path = '/api/v1/browser/start'
# params = dict(
#     serial_number=949,
#     open_tabs=1,
#     ip_tab=1,
#     new_first_tab=1,
#     launch_args='["--window-position=0,0", "--start-maximized"]')
# response = requests.get(ads_local_api + path, params=params)
# print(response.text)


# # Закрыть профиль
#
# path = '/api/v1/browser/stop'
# params = dict(serial_number=949)
# response = requests.get(ads_local_api + path, params=params)
# print(response.text)
#
# time.sleep(1)

# # Статус профиля
# path = '/api/v1/browser/active'
# params = dict(serial_number=949)
# response = requests.get(ads_local_api + path, params=params)
# print(response.json()['data']['status'] == 'Active')
#
# path_status = '/api/v1/browser/active'
# profile_number = 949
# params = dict(serial_number=profile_number)
# status = requests.get(ads_local_api + path_status, params=params).json()['data']['status']
# if status == 'Inactive':
#     path_start = '/api/v1/browser/start'
#     params = dict(
#         serial_number=profile_number,
#         open_tabs=0
#     )
#     response = requests.get(ads_local_api + path_start, params=params)
#     print(response.text)
# time.sleep(1)
# print('Profile is active')
#
# path_close = '/api/v1/browser/stop'
# params = dict(serial_number=profile_number)
# response = requests.get(ads_local_api + path_close, params=params)
# print(response.json())

#
# # Создание группы
#
# path = '/api/v1/group/create'
# payload = dict(
#     group_name='Group 1'
# )
# response = requests.post(ads_local_api + path, json=payload)
# print(response.text)
# # - 5497897
#

def get_application_list():
    path = '/api/v1/application/list'
    params = dict(page_size=50)
    response = requests.get(ads_local_api + path, params=params)
    print(response.json())


def create_profile():
    cookie = [{"domain": ".x.com", "expirationDate": int(datetime.datetime.now().timestamp()) + 10000,
               "name": "auth_token", "path": "/", "sameSite": "unspecified", "secure": True,
               "value": "2e5282ab5c9d18c399edf4de398c14f4e637aca9"}]
    cookie_str = json.dumps(cookie)
    # Создание профиля
    payload = dict(
        name='User test',
        group_id=5497897,
        domain_name='test.com',
        open_urls=["https://www.google.com/"],
        sys_app_cate_id=28765,
        cookie=cookie_str,
        user_proxy_config=dict(
            proxy_soft='other',
            proxy_type='http',
            proxy_host='192.168.1.1',
            proxy_port=8080,
            proxy_user='login',
            proxy_password='password',
        ),
        fingerprint_config=dict(
            language_switch=0,
            page_language='en-US',
            screen_resolution='1920_1080',
            random_ua=dict(
                ua_version=['131'],
                ua_system_version=['Mac OS X 14', 'Mac OS X 15']
            ),
            browser_kernel_config=dict(
                version='131',
                type='chrome'
            )

        )
    )
    path = '/api/v1/user/create'

    response = requests.post(ads_local_api + path, json=payload)
    print(response.text)


def get_profile_info(profile_number):
    path = '/api/v1/user/list'
    params = dict(serial_number=profile_number)
    response = requests.get(ads_local_api + path, params=params)
    print(response.json()['data']['list'][0]['user_id'])


def delete_profiles(profile_ids: list):
    path = '/api/v1/user/delete'
    payload = dict(
        user_ids=profile_ids
    )
    response = requests.post(ads_local_api + path, json=payload)
    print(response.text)


delete_profiles(['jic9041'])
