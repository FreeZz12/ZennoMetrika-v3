""""""

"""
Задание 1 - easy
Придумайте реализацию функции salt_password, которая будет принимать
пароль и добавлять к нему соль.
Придумайте более сложную модель соли, чем просто добавление строки к паролю.

Отправлять в решение домашки реализацию соления не нужно.
"""

# код пишем тут

"""
Задание 2  - medium

Напишите скрипт, который возьмет из файла список паролей,
перемешает по пин коду, посолит и запишет в новый файл.

"""

# код пишем тут

with open("passwords.txt", "r") as file:
    passwords = file.read().splitlines()

for password in passwords:
    password = shuffle_seed(password)
    password = salt_password(password)
    with open("passwords_new.txt", "a") as file:
        file.write(password + "\n")




