""""""
import os

"""
Задание 1 - easy

Напишите программу, которая выводит текущую дату и время в форматах в терминале:
- ДД/ММ/ГГ ЧЧ:ММ:СС
- ЧЧ:ММ:СС ДД/ММ/ГГ
- ГГГГ-ММ-ДД ЧЧ:ММ:СС
- ЧЧ:ММ:СС ГГ-ММ-ДД
"""

from datetime import datetime

now = datetime.now()
print(now.strftime('%d/%m/%y %H:%M:%S'))
print(now.strftime('%H:%M:%S %d/%m/%y'))
print(now.strftime('%Y-%m-%d %H:%M:%S'))
print(now.strftime('%H:%M:%S %Y-%m-%d'))

# код пишем тут

"""
Задание 2  - medium

Напишите программу, которая генерирует случайную дату в диапазоне от 2 до 10 дней
вперед.
Рандомными должны быть день, час, минута и секунда, но в пределах диапазона даты.
При этом даже если через год запустить программу, дата должна быть в пределах 10 дней от завтра дня запуска.
Формат вывода в терминале: ДД/ММ/ГГ ЧЧ:ММ:СС
"""
import random
from datetime import datetime, timedelta

now = datetime.now()  # текущая дата
two_days = now + timedelta(days=2)  # два дня вперед
random_date = two_days + timedelta(days=random.randint(0, 8))  # случайная дата в пределах от 2 до 10 дней
# рандомизация времени
random_time = random_date.replace(
    hour=random.randint(0, 23),
    minute=random.randint(0, 59),
    second=random.randint(0, 59)
)

print(random_time.strftime('%d/%m/%y %H:%M:%S'))
print('Разница даты от сегодня: ', random_time - now)

# код пишем тут

"""
Задание 3 - hard

Напишите функцию set_date(profile_number), которая записывает в текстовый файл profile.txt дату и время в формате:
"Профиль номер: <profile_number>-<ДД/ММ/ГГ ЧЧ:ММ:СС>"
где <profile_number> - это передаваемый параметр функции.
Если файл не существует, он должен быть создан.
Если строка в файле уже существует, она должна быть заменена.
Напишите функцию get_date(profile_number), которая возвращает дату и время из файла для переданного profile_number,
в формате объекта datetime, если запись существует, и 1 января 1970 года, если записи нет.
Напишите функцию is_check_date(profile_number: int, days: int), которая принимает номер профиля и количество дней.
Функция находит дату в файле для переданного profile_number с помощью функции get_date и проверяет, что
дата профиля была раньше чем сегодня - days дней. Если да, то возвращает True, иначе False.
Например в файле profile.txt записана дата "Профиль номер: 15/11/24 12:00:00", а сегодня 25/11/24.
Мы вызываем функцию is_check_date(profile_number=15, days=1), она должна вернуть True,
так как 15/11/24 было раньше чем 24/11/24. (25/11/24 - 1 день). Если вызвать is_check_date(profile_number=15, days=20),
то функция вернет False, так как 15/11/24 было позже чем 5/11/24 (25/11/24 - 20 дней).
"""

# код пишем тут
from datetime import datetime, timedelta

from typing import Optional


def set_time(profile_number: int) -> None:
    """
    Метод для записи даты и времени в файл. Если запись существует, она заменяется.
    :param profile_number: Номер профиля
    :return: None
    """
    today = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    file_path = 'profile.txt'

    # если файла не существует, создаем его
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(f'Профиль номер: {profile_number}-{today}\n')
        return

    # если файл существует, записываем дату
    with open('profile.txt', 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if f'Профиль номер: {profile_number}' in line:
                lines[i] = f'Профиль номер: {profile_number}-{today}\n'
                break
        else:
            lines.append(f'Профиль номер: {profile_number}-{today}\n')
        file.seek(0)
        file.writelines(lines)


def get_date(profile_number: int) -> Optional[datetime]:
    """
    Метод для получения даты из файла. Если запись существует, возвращает дату, иначе 1 января 1970 года.
    :param profile_number: Номер профиля
    :return: Дата профиля
    """
    file_path = 'profile.txt'

    if not os.path.exists(file_path):
        return datetime(1970, 1, 1)

    with open(file_path) as file:
        for line in file:
            if f'Профиль номер: {profile_number}-' in line:
                date_str = line.split('-')[1].strip()
                return datetime.strptime(date_str, '%d/%m/%y %H:%M:%S')
    return datetime(1970, 1, 1)


def is_check_date(profile_number: int, days: int) -> bool:
    """
    Метод для проверки даты профиля. Проверяет, что дата профиля была раньше чем сегодня - days дней.
    :param profile_number: Номер профиля
    :param days: Количество дней
    :return: Результат проверки
    """
    profile_date = get_date(profile_number)
    return profile_date < datetime.now() - timedelta(days=days)
