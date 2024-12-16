import random
import time


class Browser:
    """ Класс браузера """
    def __init__(self, profile: int):
        self.profile = profile
        self._open_browser()

    def _open_browser(self) -> None:
        """
        Запуск профиля
        :return:
        """
        for _ in range(3):
            try:
                print('Делаем попытку запуска профиля')
                if random.choice([True, False]):
                    raise ValueError("Ошибка при запуске профиля")
                print(f"Запуск профиля {self.profile}")
                break
            except ValueError as e:
                print(f"Ошибка при запуске профиля {self.profile}: {e}")
                time.sleep(5)
                continue
        else:
            raise ValueError("Не удалось запустить профиль")


    def close_browser(self) -> None:
        """
        Закрытие профиля
        :return:
        """
        print(f"Закрытие профиля {self.profile}")


def activity(browser: Browser) -> None:
    """
    Активность в профиле браузера
    :param browser: запущенный браузер
    :return: None
    """
    print(f"Активность в профиле {browser.profile}")
    print("Получение данных")
    if random.choice([True, False]):
        print('в функции activity, произошла ошибка получения данных')
        raise ValueError("Ошибка при получении данных")
    print('Завершение активности')


def main():
    """
    Главная функция, основная логика программы
    :return:
    """
    profiles = [590, 591, 592, 593, 594, 595, 596, 597, 598, 599]
    for profile_number in profiles:
        try:
            browser = Browser(profile_number)  # запускаем профиль по номеру, без прокси
        except ValueError as e:
            print(f"Ошибка в профиле {profile_number}: {e}")
            continue
        number = 5
        try:
            activity(browser)
        except ValueError as e:
            print(f"Ошибка в профиле {profile_number}: {e}")
            continue
        else:
            print('Дополнительная логика, если все хорошо')
            print('Дополнительная логика, если все хорошо')
            print('Дополнительная логика, если все хорошо')
            print('Дополнительная логика, если все хорошо')
        finally:
            browser.close_browser()
            print(number)







if __name__ == '__main__':
    main()
