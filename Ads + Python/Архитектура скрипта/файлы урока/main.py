
"""

Клейм токенов:

выбрать номер профиля
запустить браузер по определенному профилю в адс
зайти на сайт
подключить метамаск
нажать кнопку клейм
подтвердить транзакцию в метамаске
дождаться пока транзакция подтвердится
проверить успешность клейма
вывести токены на биржу

"""
import time

from config.chains import Chains
from models.account import Account
from utils.utils import get_list_from_file
from core.ads import Ads
from core.bot import Bot



def activity(account: Account):

    bot = Bot(account)


    try:
        bot.metamask.auth()
        bot.metamask.set_chain(Chains.bsc)

        bot.rabby.auth()

        bot.binance.withdaw(100, 'BNB', 'BSC')
        # переход на сайт для клейма
        bot.ads.page.goto('https://claim.com/')

        # клейм токенов
        bot.metamask.confirm(bot.ads.page.get_by_test_id('connect-wallet'))
        bot.metamask.confirm(bot.ads.page.get_by_test_id('claim-btn'))

        # дожидаемся пока транзакция подтвердится
        time.sleep(10)

        # проверяем успешность клейма
        claim_status = bot.ads.page.get_by_test_id('claim-status').inner_text()
        if claim_status == 'Success':
            print('Клейм успешен')
        else:
            print('Клейм не успешен')

        bot.excel.save_data()

        # выводим токены на биржу
        bot.metamask.send_token(account.sub_address_cex)

        print('Токены выведены на биржу')
    except Exception as e:
        print(e)
    finally:
        # закрываем браузер
        bot.ads.browser.close()

def main():
    profile_numbers = get_list_from_file('config/profile_numbers.txt')
    passwords_mm = get_list_from_file('config/metamask_passwords.txt')
    passwords_rabby = get_list_from_file('config/rabby_passwords.txt')
    sub_addresses_cex = get_list_from_file('config/sub_addresses_cex.txt')
    addresses = get_list_from_file('config/addresses.txt')

    for profile_number, password_mm, passwords_rabby, sub_address_cex, address in zip(profile_numbers, passwords_mm, passwords_rabby, sub_addresses_cex, addresses):
        account = Account(profile_number, password_mm, passwords_rabby, sub_address_cex, address)
        activity(account)



if __name__ == '__main__':
    main()













