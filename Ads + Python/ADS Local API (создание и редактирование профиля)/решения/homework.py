""""""
from __future__ import annotations

import json

"""
Задание 1 - easy
Напишите функцию get_profile_id, которая принимает на вход номер профиля и 
возвращает его id в ADS.
"""
import requests


def get_profile_id(profile_number: int) -> str:
    """
    Возвращает id профиля в ADS по его номеру
    :param profile_number: номер профиля
    :return: id профиля
    """
    url = 'http://local.adspower.com:50325'
    path = '/api/v1/user/list'
    params = dict(serial_number=profile_number)
    response = requests.get(url + path, params=params)
    return response.json()['data']['list'][0]['user_id']


"""
Задание 2  - medium
Напишите функцию set_proxy, которая принимает на вход:
- номер профиля
- прокси в виде строки вида 'ip:port:login:password:type' или
словаря с ключами proxy_host, proxy_port, proxy_user, proxy_password и proxy_type

Функция должна устанавливать прокси для профиля в ADS. 
Протестируйте, обратите внимание что прокси нужно устанавливать до запуска браузера.
Если прокси установить в запущенном профиле, то нужно перезапустить профиль, чтобы прокси начали
работать.

"""


def set_proxy(profile_number: int, proxy: dict | str, ) -> None:
    """
    Устанавливает прокси для профиля в ADS
    :param profile_number: номер профиля
    :param proxy: прокси в виде строки вида 'ip:port:login:password:type' или
     словаря с ключами proxy_host, proxy_port, proxy_user, proxy_password и proxy_type
    """
    url = 'http://local.adspower.com:50325'
    path = '/api/v1/user/update'
    if isinstance(proxy, str):
        ip, port, login, password, type_ = proxy.split(':')
        proxy = dict(
            proxy_type=type_,
            proxy_host=ip,
            proxy_port=port,
            proxy_user=login,
            proxy_password=password
        )
    proxy['proxy_soft'] = 'other'
    payload = dict(
        user_id=get_profile_id(profile_number),
        user_proxy_config=proxy
    )
    response = requests.post(url + path, json=payload)
    return response.json()


"""
Задание 3 - hard

Напишите функцию create_profile, которая принимает на вход:
- cookie типа list[dict], по умолчанию равный None (необязательный)
- sys_app_cate_id типа int, по умолчанию равный None (необязательный)
- proxy, типа str, dict, по умолчанию равный None (необязательный)
    - прокси может содержать строку вида 'proxy_host:proxy_port:proxy_user:proxy_password:proxy_type'
    - proxy может содержать словарь с ключами: proxy_host, proxy_port, proxy_user, proxy_password и proxy_type
-  fingerprint, типа dict, по умолчанию равный None (необязательный)
    - fingerprint должен содержать ключи:
    - версия браузера: int (по умолчанию 130)
    - операционная система: str (по умолчанию 'Windows 11')

Функция должна создавать профиль в ADS, учитывая переданные или не переданные параметры.
Если не переданы параметры, то должны быть использованы значения по умолчанию и должен
быть создан профиль с 130 версией браузера и ядром, операционной системой Windows 11 с proxy_soft=no_proxy.
Все остальные значения созданного профиля должны быть на ваше усмотрение.
"""


def create_profile(cookie: list[dict] = None, sys_app_cate_id: int = None, proxy: dict | int = None,
                   fingerprint: dict = None) -> dict:



    payload = dict(
        group_id=5497897,
        user_proxy_config=dict(
            proxy_soft='no_proxy',
        ),
        fingerprint_config=dict(
            random_ua=dict(
                ua_version=['130'],
                ua_system_version=['Windows 11']
            ),
            browser_kernel_config=dict(
                version='130',
                type='chrome'
            )

        )
    )
    if cookie:
        payload['cookie'] = json.dumps(cookie)
    if sys_app_cate_id:
        payload['sys_app_cate_id'] = sys_app_cate_id
    if proxy:
        if isinstance(proxy, str):
            ip, port, login, password, type_ = proxy.split(':')
            proxy = dict(
                proxy_type=type_,
                proxy_host=ip,
                proxy_port=port,
                proxy_user=login,
                proxy_password=password
            )
        proxy['proxy_soft'] = 'other'
        payload['user_proxy_config'] = proxy
    if fingerprint:
        version = fingerprint.get('version', '130')
        os = fingerprint.get('os', 'Windows 11')
        payload['fingerprint_config']['random_ua'] = dict(
            ua_version=[version],
            ua_system_version=[os]
        )
        payload['fingerprint_config']['browser_kernel_config'] = dict(
            version=version,
            type='chrome'
        )

    ads_local_api = 'http://local.adspower.com:50325'
    path = '/api/v1/user/create'
    response = requests.post(ads_local_api + path, json=payload)
    print(response.json())
    return response.json()
create_profile()