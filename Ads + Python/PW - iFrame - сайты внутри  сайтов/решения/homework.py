""""""

"""
Задание 1 - easy

Напишите код, который найдет iframe, если HTML страница содержит структуру:

<iframe src="https://www.hamster.com/embed/4iQhxfej2h0"></iframe>

"""
from playwright.sync_api import Page, Frame
import re

page.frame(url=re.compile('^https://www.hamster.com/.*'))

# или так


"""
Задание 2  - medium
Напишите код, который найдет внутренний iframe, если HTML страница содержит структуру:

<iframe src="https://www.telegram.org/">
    <iframe src="https://www.hamster.com/game">
        <button>Farm</button>
    </iframe>
</iframe>

Напишите код, который кликнет по кнопке 'Farm'
"""

page.frame(url='https://www.hamster.com/game').get_by_role('button', name='Farm').first.click()
