from core.ads import Ads
from core.excel import Excel
from core.exchanges.binance import Binance
from core.exchanges.okx import Okx
from core.extenstions.metamask import Metamask
from core.extenstions.rabby import Rabby
from models.account import Account


class Bot:
    def __init__(self, account: Account):
        self.account = account
        self.ads = Ads(self.account)
        self.metamask = Metamask(self.ads)
        self.rabby = Rabby(self.ads)
        self.excel = Excel(self.account)
        self.binance = Binance(self.account)
        self.okx = Okx(self.account)

    def run(self):

