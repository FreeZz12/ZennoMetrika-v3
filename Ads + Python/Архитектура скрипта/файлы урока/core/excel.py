from models.account import Account


class Excel:
    def __init__(self, account: Account):
        self.account = account


    def get_data(self, path: str) -> list:
        pass

    def save_data(self, path: str, data: list) -> None:
        pass

