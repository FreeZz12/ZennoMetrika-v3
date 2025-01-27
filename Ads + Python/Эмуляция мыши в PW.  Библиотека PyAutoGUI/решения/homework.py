""""""
from playwright.sync_api import Locator

"""
Задание 1 - easy

Замерьте и напишите какой у вас x_offset и y_offset, смещение относительно начала окна браузера.

"""

# код пишем тут

"""
Задание 2  - medium

Напишите самостоятельно функцию scroll_to, которая будет скролить страницу при помощи
pyautoGUI пока элемент по переданному Locator не станет видимым.
Функция должна принимать на вход объект Locator из Playwright.
Если элемент уже видим, то функция ничего не делает.
Функция должна:
- учитывать смещение относительно начала окна браузера (сверху и слева)
- учитывать нижнюю границу окна браузера
- делать вкладку активной.
- наводить курсор над страницей при помощи pyautogui.moveTo в рандомное место около центра
страницы. (с учетом смещения, движение курсора должно быть с Tween и рандомной длительностью)
- определять направление скрола в зависимости от положения элемента на странице.
- делать рандомные прокрутки в сторону элемента с рандомными паузами.
- с шансом 10% прокручивать в противоположную сторону.
- с шансом 10% вставать на более длительную паузу.
- если страница прокручена до конца, а элемент не видим, прекращать процесс прокрутки.
- если элемент видим, то прекращать процесс прокрутки (в зоне координат окна браузера)

"""
import random
import time

import pyautogui
import pytweening as pt


tween_list = [
        pt.easeInQuad, pt.easeOutQuad, pt.easeInOutQuad, pt.easeInCubic, pt.easeOutCubic, pt.easeInOutCubic,
        pt.easeInQuart, pt.easeOutQuart, pt.easeInOutQuart, pt.easeInQuint, pt.easeOutQuint,
        pt.easeInOutQuint, pt.easeInSine, pt.easeOutSine, pt.easeInOutSine, pt.easeInExpo, pt.easeOutExpo,
        pt.easeInOutExpo, pt.easeInCirc, pt.easeOutCirc, pt.easeInOutCirc, pt.easeInElastic,
        pt.easeOutElastic, pt.easeInOutElastic, pt.easeInBack, pt.easeOutBack, pt.easeInOutBack,
        pt.easeInBounce, pt.easeOutBounce, pt.easeInOutBounce,
    ]
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

    # выбор поведения курсора
    random_tween = random.choice(tween_list)

    # случайное перемещение курсора над браузером
    random_x = random.randint(200, 500)
    random_y = random.randint(200, 500) + offset_y
    pyautogui.moveTo(random_x,random_y, duration=random.uniform(0.5, 1.5), tween=random_tween)

    # получение y координаты нижней границы элемента
    element_info = locator.bounding_box()
    element_point_y = int(element_info['y'])

    # получение высоты элемента
    element_height = int(element_info['height'])

    # определение координат нижней границы элемента с учетом рамки браузера
    element_footer = element_point_y + element_height + offset_y

    # определение направления прокрутки
    direction = 'down'
    if element_footer < offset_y:
        direction = 'up'

    # прокрутка страницы
    while True:

        # проверка на видимость элемента на странице
        if direction == 'down':
            # если крутим вниз, элемент должен быть выше нижней границы окна
            if element_footer < y_border:
                break
        else:
            # если крутим вверх, элемент должен быть ниже верхней границы окна
            if element_point_y > offset_y:
                break

        # случайное значение прокрутки
        y_delta = random.randint(10, 30)

        # смена направления с шансом 10%
        if random.randint(0, 100) > 90:
            y_delta = -y_delta

        # с шансом 10% вставать на более длительную паузу
        if random.randint(0, 100) > 90:
            time.sleep(random.uniform(0.5, 1.5))

        # прокрутка страницы вниз или вверх
        pyautogui.scroll(y_delta if direction == 'down' else -y_delta)

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


# код пишем тут

"""
Задание 3 - hard
Напишите самостоятельно функцию move_to, которая будет наводить курсор на элемент при помощи
pyautoGUI.
Функция должна принимать на вход объект Locator из Playwright.
Функция должна:
- прокручивать страницу при помощи функции scroll_to_el, пока элемент не станет видимым.
- учитывать смещение относительно начала окна браузера (сверху и слева)
- делать вкладку активной.
- делать рандомные 2-4 движения курсора над окном браузера с рандомными паузами.
- наводить курсор на элемент с Tween и рандомной длительностью. (в рандомную точку элемента, близко к центру)
- делать небольшую паузу после наведения курсора на элемент.
- делать микросмещение курсора в рандомную точку элемента (курсор по прежнему должен быть в пределах элемента)

"""

# код пишем тут
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

    move_counter = random.randint(2, 4)
    for _ in range(move_counter):
        # случайное перемещение курсора над браузером
        random_x = random.randint(200, 500)
        random_y = random.randint(200, 500) + offset_y
        random_tween = random.choice(tween_list)
        pyautogui.moveTo(random_x, random_y, duration=random.uniform(0.5, 1.5), tween=random_tween)
        time.sleep(random.uniform(0.5, 1.5))

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
    random_tween = random.choice(tween_list)
    # выбор случайной длительности перемещения
    duration = random.uniform(0.5, 1.5)

    pyautogui.moveTo(x_diff, y_diff, duration=duration, tween=random_tween)

    # небольшая пауза после наведения курсора на элемент
    time.sleep(random.uniform(0.5, 1.5))

    # определение координат курсора
    current_position = pyautogui.position()
    current_position_x, current_position_y = current_position.x, current_position.y + offset_y

    # координаты смещения
    random_x = random.randint(3, 5)
    random_y = random.randint(3, 5)

    # проверка на выход за границы элемента
    if element_point_x + element_width < current_position_x + random_x:
        random_x = 0
    if element_point_y + element_height < current_position_y + random_y:
        random_y = 0

    # случайное смещение курсора внутри элемента
    duration = random.uniform(0.01, 0.1)
    pyautogui.moveRel(random_x, random_y, duration=duration, tween=random_tween)

