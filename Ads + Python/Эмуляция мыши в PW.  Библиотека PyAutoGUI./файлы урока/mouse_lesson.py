from __future__ import annotations

import random
import time
from pprint import pprint
import re

import pyautogui
import pytweening as pt
import requests
from playwright.sync_api import sync_playwright, Page, Frame, Browser, Playwright, Locator

from playwright.sync_api import sync_playwright
from typing_extensions import TypedDict


def start_browser(profile_number: int) -> Page:
    profile_data = open_browser(profile_number)
    url_connect = profile_data.get('data').get('ws').get('puppeteer')
    time.sleep(2)
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(url_connect, slow_mo=random.randint(800, 1200))
    if not browser.is_connected():
        print("Browser not connected")
        exit(1)
    context = browser.contexts[0]
    return context.new_page()


def open_browser(profile_number: int) -> dict:
    params = dict(serial_number=profile_number,
                  launch_args='["--window-position=0,0", "--start-maximized"]'
                  )
    url = "http://local.adspower.net:50325/api/v1/browser/start"
    response = requests.get(url, params=params)
    data = response.json()
    return data


def close_browser(profile_number: int) -> dict:
    params = dict(serial_number=profile_number)
    url = "http://local.adspower.net:50325/api/v1/browser/stop"
    response = requests.get(url, params=params)
    data = response.json()
    return data


def move_to_el(locator: Locator) -> None:
    """
    Перемещение курсора к элементу.
    Если элемент находится вне видимой области, то прокручивает страницу до него.
    :param locator: локатор элемента
    :return: None
    """
    # прокрутка страницы до элемента
    scroll_to_el(locator)

    # сдвиг от края экрана
    offset_y = 144  # сдвиг по y

    # активация страницы
    locator.page.bring_to_front()

    # координаты элемента и его размеры
    element_point = locator.bounding_box()
    element_point_x, element_point_y = int(element_point['x']), int(element_point['y'])
    element_width, element_height = int(element_point['width']), int(element_point['height'])

    # вычисление точки внутри элемента
    random_x = random.randint(3 if element_width > 3 else 0, element_width - 3 if element_width > 3 else 0)
    random_y = random.randint(3 if element_height > 3 else 0, element_height - 3 if element_height > 3 else 0)

    # вычисление разницы между координатами мыши и элемента
    x_diff = element_point_x + random_x
    y_diff = element_point_y + offset_y + random_y

    # выбор поведения курсора
    random_tween = random.choice([
        pt.easeInQuad, pt.easeOutQuad, pt.easeInOutQuad, pt.easeInCubic, pt.easeOutCubic, pt.easeInOutCubic,
        pt.easeInQuart, pt.easeOutQuart, pt.easeInOutQuart, pt.easeInQuint, pt.easeOutQuint,
        pt.easeInOutQuint, pt.easeInSine, pt.easeOutSine, pt.easeInOutSine, pt.easeInExpo, pt.easeOutExpo,
        pt.easeInOutExpo, pt.easeInCirc, pt.easeOutCirc, pt.easeInOutCirc, pt.easeInElastic,
        pt.easeOutElastic, pt.easeInOutElastic, pt.easeInBack, pt.easeOutBack, pt.easeInOutBack,
        pt.easeInBounce, pt.easeOutBounce, pt.easeInOutBounce,
    ])
    # выбор случайной длительности перемещения
    duration = random.uniform(0.5, 1.5)
    pyautogui.moveTo(x_diff, y_diff, duration=duration, tween=random_tween)


def click_on_el(locator: Locator) -> None:
    """
    Клик по элементу. Если элемент находится вне видимой области,
    то прокручивает страницу до него. Перед кликом перемещает курсор к элементу.
    :param locator:  локатор элемента
    :return: None
    """
    move_to_el(locator)
    pyautogui.click()


def scroll_to_el(locator: Locator, ) -> None:
    """
    Прокрутка страницы до элемента. Если элемент находится вне видимой области,
    то прокручивает страницу до него.
    Координаты элемента определяются через Playwright.
    Работает только с прокруткой вниз.
    :param locator: локатор элемента
    :return: None
    """

    # параметры для правильного расчета координат
    offset_y = 144  # рамка от начала экрана до браузера
    y_border = 900 + offset_y  # нижняя граница браузера

    # активация страницы

    locator.page.bring_to_front()
    # получение y координаты нижней границы элемента
    element_info = locator.bounding_box()
    element_point_y = int(element_info['y'])

    # получение высоты элемента
    element_height = int(element_info['height'])

    # определение координат нижней границы элемента с учетом рамки браузера
    element_footer = element_point_y + element_height + offset_y

    # прокрутка страницы, пока элемент не окажется в видимой области
    while element_footer > y_border:
        # случайное значение прокрутки
        y_delta = random.randint(10, 30)

        # смена направления с шансом 10%
        if random.randint(0, 100) > 90:
            y_delta = -y_delta

        # прокрутка страницы
        pyautogui.scroll(y_delta)

        # задержка для прокрутки
        time.sleep(random.uniform(0.1, 0.3))

        old_element_footer = element_footer
        # обновление координат элемента
        element_footer = locator.bounding_box()['y'] + element_height + offset_y

        # если элемент не прокрутился, то выход из цикла
        if old_element_footer == element_footer:
            break

    # докрутка до элемента от Playwright на случай, если элемент не влез в видимую область
    locator.scroll_into_view_if_needed()


def main():
    page = start_browser(949)

    page.goto('https://loneti.ru/draw ')
    el = page.get_by_role('link', name='Read the Docs')

    pyautogui.size()
    pyautogui.PAUSE = 0.5
    pyautogui.position()

    y_offset = 144

    pyautogui.scroll(10)
    pyautogui.moveTo(100, 100, duration=1, tween=pt.easeInOutQuad)
    pyautogui.moveRel(200, 0, duration=1, tween=pt.easeInOutQuad)
    pyautogui.click()
    pyautogui.dragTo(100, 100, duration=1, tween=pt.easeInOutQuad)
    pyautogui.dragRel(200, 0, duration=1, tween=pt.easeInOutQuad)


if __name__ == '__main__':
    main()
