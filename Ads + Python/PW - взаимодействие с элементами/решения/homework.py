""""""

"""
Задание 1 - easy

Прочитайте за что отвечает параметр slow_mo в методе connect_over_cdp 
https://playwright.dev/python/docs/next/api/class-browsertype#browser-type-connect-over-cdp

Будьте осторожны с вкладкой у которой в url offscreen, данную вкладку нельзя закрывать и нельзя
использовать для перехода по ссылкам, это техническая вкладка, игнорируйте ее. Некоторые
расширения имеют технические скрытые вкладки.

"""

# код пишем тут

"""
Задание 2  - medium

Напишите метод keyboard_input для класса ADS, у класса есть аттрибут page, который хранит страницу,
данный метод должен принимать:
- локатор текстового поля
- текст который нужно ввести в поле

Метод должен вводить текст в поле посимвольно с паузой от 0.01 до 0.1 секунды.
Пауза между каждым символом должна быть случайной.

"""


def keyboard_input(self, locator: Locator, text: str) -> None:
    """
    Вводит текст в поле посимвольно с паузой от 0.01 до 0.1 секунды.
    :param locator: локатор текстового поля
    :param text: текст который нужно ввести в поле
    :return: None
    """
    for symbol in text:
        locator.press_sequentially(symbol)
        random_sleep(0.01, 0.1)


"""
Задание 3  - hard

Напишите метод keyboard_input для класса ADS, данный метод должен принимать:
- локатор текстового поля
- текст который нужно ввести в поле

Метод должен вводить текст в поле посимвольно с паузой от 0.01 до 0.1 секунды.
Пауза между каждым символом должна быть случайной.
Метод должен иногда допускать ошибки, вводя случайные символы вместо нужных,
после чего должен удалять ошибочный символ и вводить правильный.

"""


def keyboard_input(self, locator: Locator, text: str, mistake: bool = False) -> None:
    """
    Вводит текст в поле посимвольно с паузой от 0.01 до 0.1 секунды.
    :param mistake: допускать ли ошибки при вводе
    :param locator: локатор текстового поля
    :param text: текст который нужно ввести в поле
    :return: None
    """
    for symbol in text:
        if mistake and random.randint(0, 10) > 8:
            random_symbol = random.choice('abcdefghijklmnopqrstuvwxyz')
            locator.press_sequentially(random_symbol)
            random_sleep(0.01, 0.1)
            locator.press('Backspace')
        locator.press_sequentially(symbol)
        random_sleep(0.01, 0.1)



"""

Задание 4  - hard

Напишите скрипт, который будет открывать страницу https://pancakeswap.finance,
Открывать всплывающее окно выбора сетей и выбирать рандомную сеть.

"""

page.goto('https://pancakeswap.finance')
# получаем локаторы содержащие сети
chain_block = page.locator('nav').locator('div', has_text='Select a Network', has_not_text='English')
# наводимся на блок с сетями
chain_block.first.hover()
# получаем все кнопки с сетями
chains = chain_block.get_by_role('button').all()
# выбираем рандомную сеть
random_chain = random.choice(chains)
# кликаем по сети
random_chain.click()





