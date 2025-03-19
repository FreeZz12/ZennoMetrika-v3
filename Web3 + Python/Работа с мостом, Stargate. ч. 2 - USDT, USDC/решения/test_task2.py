# test_task_2.py
import random
from task_2 import (
    get_cached_eth_price,
    TokenWithBalance,
    check_balances,
    select_token_with_balance,
    worker,
    TokenType,
)


# Для тестирования создадим простой класс для имитации Amount.
class DummyAmount:
    def __init__(self, ether):
        self.ether = ether


# Тест для get_cached_eth_price.
def test_get_cached_eth_price(monkeypatch):
    fake_price = 123.45

    # Подменяем функцию получения цены с Binance.
    monkeypatch.setattr("task_2.get_token_price_from_binance", lambda symbol: fake_price)

    # Сбрасываем кэш, если он уже установлен.
    if hasattr(get_cached_eth_price, "price"):
        del get_cached_eth_price.price
    if hasattr(get_cached_eth_price, "last_update"):
        del get_cached_eth_price.last_update

    price = get_cached_eth_price()
    assert price == fake_price


# Тест для TokenWithBalance для токена типа STABLE.
def test_token_with_balance_stable(monkeypatch):
    fake_price = 2000
    monkeypatch.setattr("task_2.get_cached_eth_price", lambda: fake_price)

    class DummyToken:
        pass

    token = DummyToken()
    token.token_type = TokenType.STABLE

    dummy_amount = DummyAmount(500)
    twb = TokenWithBalance(token, dummy_amount)
    # Для STABLE usd_balance должно совпадать с amount.ether.
    assert twb.usd_balance == 500


# Тест для TokenWithBalance для токена типа NATIVE.
def test_token_with_balance_native(monkeypatch):
    fake_price = 2000
    monkeypatch.setattr("task_2.get_cached_eth_price", lambda: fake_price)

    class DummyToken:
        pass

    token = DummyToken()
    token.token_type = TokenType.NATIVE

    dummy_amount = DummyAmount(1)
    twb = TokenWithBalance(token, dummy_amount)
    # Для NATIVE usd_balance равен сумме умноженной на курс.
    assert twb.usd_balance == 1 * fake_price


# Тесты для функции select_token_with_balance.
def test_select_token_with_balance_two_stables(monkeypatch):
    class DummyToken:
        pass

    # Создадим два стабильных токена и один нативный.
    token1 = DummyToken()
    token1.token_type = TokenType.STABLE
    token2 = DummyToken()
    token2.token_type = TokenType.STABLE
    token3 = DummyToken()
    token3.token_type = TokenType.NATIVE

    twb1 = TokenWithBalance(token1, DummyAmount(15))  # usd_balance = 15
    twb2 = TokenWithBalance(token2, DummyAmount(20))  # usd_balance = 20
    twb3 = TokenWithBalance(token3, DummyAmount(100))  # usd_balance считается по курсу, но здесь не участвует

    selected = select_token_with_balance([twb1, twb2, twb3])
    # Должен быть выбран токен с наибольшим usd_balance среди STABLE.
    assert selected == twb2


def test_select_token_with_balance_one_stable(monkeypatch):
    class DummyToken:
        pass

    token1 = DummyToken()
    token1.token_type = TokenType.STABLE
    token2 = DummyToken()
    token2.token_type = TokenType.NATIVE
    token3 = DummyToken()
    token3.token_type = TokenType.STABLE

    twb1 = TokenWithBalance(token1, DummyAmount(12))
    twb2 = TokenWithBalance(token2, DummyAmount(50))
    twb3 = TokenWithBalance(token3, DummyAmount(5))

    selected = select_token_with_balance([twb1, twb2, twb3])
    # Если только один STABLE с балансом, он и должен быть выбран.
    assert selected == twb1


def test_select_token_with_balance_no_stable(monkeypatch):
    class DummyToken:
        pass

    token1 = DummyToken()
    token1.token_type = TokenType.STABLE
    token2 = DummyToken()
    token2.token_type = TokenType.STABLE
    token3 = DummyToken()
    token3.token_type = TokenType.NATIVE

    twb1 = TokenWithBalance(token1, DummyAmount(5))  # usd_balance = 15
    twb2 = TokenWithBalance(token2, DummyAmount(5))  # usd_balance = 20
    twb3 = TokenWithBalance(token3, DummyAmount(100))  # usd_balance считае

    selected = select_token_with_balance([twb1, twb2, twb3])
    # Если нет стабильных токенов, должен вернуться нативный.
    assert selected == twb3


# Тест для функции check_balances.
def test_check_balances(monkeypatch):
    # Определим dummy-объект для цепочки.
    class DummyChain:
        def __init__(self, rpc):
            self.rpc = rpc

    dummy_chain = DummyChain("http://dummy")

    # Dummy-аккаунт с полем address.
    class DummyAccount:
        address = "0xdummy"

    dummy_account = DummyAccount()

    # Подменяем методы получения токенов.
    class DummyToken:
        pass

    def dummy_get_token_by_name(name, chain):
        token = DummyToken()
        token.token_type = TokenType.STABLE  # пусть для USDC и USDT это будет STABLE
        token.name = name
        token.address = "0xdummy"
        token.decimals = 18
        return token

    def dummy_get_native(chain):
        token = DummyToken()
        token.token_type = TokenType.NATIVE
        token.name = "NATIVE"
        token.address = "0xdummy"
        token.decimals = 18
        return token

    monkeypatch.setattr("task_2.Tokens.get_token_by_name", dummy_get_token_by_name)
    monkeypatch.setattr("task_2.Tokens.get_native", dummy_get_native)

    # Подменяем get_balance так, чтобы для STABLE возвращалась сумма больше 10,
    # а для NATIVE — меньше 10.
    def dummy_get_balance(w3, token):
        if token.token_type == TokenType.STABLE:
            return DummyAmount(20)
        else:
            return DummyAmount(0.01)

    monkeypatch.setattr("task_2.get_balance", dummy_get_balance)

    balances = check_balances(dummy_account, dummy_chain)
    # Должно вернуться 3 токена: USDC, USDT и нативный.
    assert len(balances) == 3
    assert balances[0].token.token_type == TokenType.STABLE
    assert balances[1].token.token_type == TokenType.STABLE
    assert balances[2].token.token_type == TokenType.NATIVE
    assert balances[0].amount.ether == 20
    assert balances[1].amount.ether == 20
    assert balances[2].amount.ether == 0.01


# Тест для функции worker (успешный сценарий).
def test_worker_success(monkeypatch):
    dummy_private_key = "0xdummykey"

    # Создадим dummy-объекты для аккаунта.
    class DummyEthAccount:
        @staticmethod
        def from_key(key):
            class DummyAccount:
                address = "0xdummy"

            return DummyAccount()

    class DummyWeb3:
        def __init__(self, provider=None):
            self.eth = type("DummyEth", (), {})()
            self.eth.default_account = "0xdummy"
            self.eth.account = DummyEthAccount()


    monkeypatch.setattr("task_2.Web3", lambda provider: DummyWeb3(provider))
    monkeypatch.setattr("task_2.Account", DummyEthAccount)

    # Подменяем check_balances так, чтобы возвращался токен с балансом больше 10.
    class DummyToken:
        pass

    token1 = DummyToken()
    token1.token_type = TokenType.STABLE
    token1_balance = TokenWithBalance(token1, DummyAmount(15))
    token2 = DummyToken()
    token2.token_type = TokenType.STABLE
    token2_balance = TokenWithBalance(token2, DummyAmount(20))
    token3 = DummyToken()
    token3.token_type = TokenType.NATIVE
    token3_balance = TokenWithBalance(token3, DummyAmount(0.01))
    dummy_balance = [token1_balance, token2_balance, token3_balance]

    def dummy_check_balances(account, chain):
        return dummy_balance

    monkeypatch.setattr("task_2.check_balances", dummy_check_balances)

    # Флаг для проверки вызова bridge.
    bridge_called = {"flag": False}

    def dummy_bridge(w3, private_key, chain, to_chain, amount, token=None):
        assert chain != to_chain
        if token:
            assert isinstance(w3, DummyWeb3)
            assert isinstance(token, DummyToken)
            assert amount.ether == 15.0 or amount.ether == 20.0
        else:
            assert isinstance(w3, DummyWeb3)
            assert amount == 0.01 - (3 / 2000)
        bridge_called["flag"] = True

    monkeypatch.setattr("task_2.bridge", dummy_bridge)
    monkeypatch.setattr("task_2.get_cached_eth_price", lambda: 2000)
    # Подменяем random.shuffle и random.choice для детерминированности.
    monkeypatch.setattr(random, "shuffle", lambda x: None)
    monkeypatch.setattr(random, "uniform", lambda x, y: 3)
    monkeypatch.setattr(random, "choice", lambda x: x[0])

    for token_index in range(3):
        monkeypatch.setattr("task_2.select_token_with_balance", lambda tokens: dummy_balance[token_index])

        status = worker(dummy_private_key)
        assert status is True
        assert bridge_called["flag"] is True

