from decimal import Decimal


class Amount:
    wei: int
    ether: float
    ether_decimals: Decimal

    def __init__(self, amount: int | float, decimals: int = 18, is_wei: bool = False):
        if is_wei:
            self.wei = int(amount)
            self.ether_decimals = Decimal(str(amount)) / 10 ** decimals
            self.ether = float(self.ether_decimals)
        else:
            self.wei = int(amount * 10 ** decimals)
            self.ether_decimals = Decimal(str(amount))
            self.ether = float(self.ether_decimals)

    def __str__(self):
        return f'{self.ether}'
