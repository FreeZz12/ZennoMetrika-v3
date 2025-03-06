""""""

"""
Задание 1 - medium
Напишите функцию bridge, которая будет отправлять токены через мост https://www.memebridge.xyz/bridge
Функция должна отправлять токены ETH из стартовой сети в целевую сеть.
Функция должна работать если токен ETH является нативным токеном в стартовой сети. (перевод нативного токена)
Функция должна работать если токен ETH не является нативным токеном в стартовой сети. (erc20 перевод токена WETH)
Проверьте работоспособность функции на сетях:

из Arbitrum в Polygon
из Arbitrum в Optimism
из Optimism в Arbitrum
из Polygon в Arbitrum


Внимание!

Если вы столкнетесь с ошибкой "web3.exceptions.ExtraDataLengthError: The field extraData is 234 bytes, b
ut should be 32. It is quite likely that you are connected to a POA chain. 
Refer to http://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority for more details.
The full extraData is: HexBytes"

Добавьте строчку кода сразу после инициализации w3 объекта.

w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
с добавлением импорта

from web3.middleware import ExtraDataToPOAMiddleware
Данная ошибка может возникать в PoA блокчeйенами (polygon, bsc)
"""


