""""""

"""
Задание 1 - easy

Откройте https://localapi-doc-en.adspower.com/.
Напишите XPath запрос для нахождения span с текстом "API Overview".
Протестируйте запрос в Chrome DevTools. У вас должен быть найден один элемент.
"""

# код пишем тут
xpath = "//span[text()='API Overview']"

"""
Задание 2  - medium

Откройте https://localapi-doc-en.adspower.com/.
На странице перечислены прямоугольники с названиями категорий, Overview, Browser и т.д.
Внутри каждого блока перечислены span элементы с ссылками.
Напишите XPath запрос для нахождения a элементов с ссылками, внутри которых span с названием. (API Overview, 
Connection Status, Open Browser, Close Browser, Check Browser Status и т.д.). 
Нужно найти именно a элементы, а не span.
Протестируйте запрос в Chrome DevTools. У вас должен быть найден 21 элемент. Попробуйте использовать оси.

"""

xpath = "//span[@class='line-clamp-2']/ancestor::a"
# код пишем тут

"""
Задание 3 - hard
Откройте https://pancakeswap.finance/info/v3/tokens
Напишите XPath запрос для нахождения div элемента содержащего внутри в дочерних элементах лого и название 
токена на 1 строчке списка токенов.
В запросе не должно быть названия токена.
Протестируйте запрос в Chrome DevTools. Запрос должен находить 1 элемент на странице.
Попробуйте использовать оси.
"""

xpath = "//div[text()='1']/following-sibling::div[1]"

"""
Задание 4 - hard
Откройте https://pancakeswap.finance/info/v3/tokens
Напишите XPath запрос для нахождения всех div элементов содержащих внутри в дочерних элементах название токена.
Протестируйте запрос в Chrome DevTools. Запрос должен находить 10 элементов на странице.
Попробуйте использовать оси.
"""
xpath = "//img[@alt='token logo']/parent::div/following-sibling::div"

