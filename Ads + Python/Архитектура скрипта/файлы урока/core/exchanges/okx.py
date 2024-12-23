from models.account import Account


class Okx:
    def __init__(self, account: Account):
        self.account = account


    def withdaw(self, amount: int, token: str, chain: str):
        print(f'Withdraw {amount} {token} to {self.account.address} on {chain}')
