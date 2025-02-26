""""""
"""
Задание 1 - medium

Напишите функцию:
bridge_relay(
    to_chain: Chain,
    amount: float,
    from_token: Token | None = None,
    to_token: Token | None = None
    ) -> str

Функция должна отправлять токены из сети указанной в объекте w3 в сеть to_chain.
Должна минимально работать в сети Arbitrum и Optimism с токенами ETH, USDT, USDC.

1. Если from_token и to_token не указаны, то отправляются и получаются нативные токены
2. Если from_token не указан, а to_token указан, то отправляются нативные токены,
а получаются токены указанные в to_token
3. Если from_token указан, а to_token не указан, то отправляются токены указанные в from_token,
а получаются нативные токены
4. Если from_token и to_token указаны указаны, то отправляются токены указанные в from_token,
а получаются токены указанные в to_token

Функция должна возвращать хеш транзакции.
Выясните как нужно изменить логику скрипта, чтобы можно было отправлять ERC20 токены через Bridge,
для этого изучите запросы на https://api.relay.link/quote, ответ от сервера и то что лежит в data, а так же
транзакцию в кошельке, которая отправляется если from_token это адрес ERC20 токен.

Используйте объекты Chain и Token для передачи параметров в функцию.

@dataclass
class Chain:
    name: str
    rpc: str
    native_token: str
    chain_id: int
    multiplier: int = 1


class Chains:
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH', 42161)
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH', 10)

@dataclass
class Token:
    name: str
    address: ChecksumAddress | str
    decimals: int
    chain: Chain

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)

class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6, Chains.Optimism)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6, Chains.Optimism)
    ETH_ARBITRUM = Token('ETH', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 18, Chains.Arbitrum)
    WETH_ARBITRUM = Token('WETH', '0x82af49447d8a07e3bd95bd0d56f35241523fbab1', 18, Chains.Arbitrum)
    USDT_ARBITRUM = Token('USDT', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', 6, Chains.Arbitrum)
    USDC_ARBITRUM = Token('USDC', '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', 6, Chains.Arbitrum)

!ПОДСКАЗКА!

Сравните транзакции, которые формируются в кошельке если исходящие токены разные USDT / USDC и т.д.
Обратите внимание на получателя токенов.
Обратите внимание на data в транзакции.
Обратите внимание на последний аргумент в data в транзакции.
Все данные можно получить из запроса к https://api.relay.link/quote.
Для нативного токена и для ERC20 токенов нужно отправить разные транзакции на разные адреса.

"""

# пишите код тут

"""
"""


"""
Задание 2  - medium

Скрипт для отправки рандомных токенов из рандомной сети в рандомную сеть на рандомную сумму.
Для работы используются сети Arbitrum, Optimism, Base, Linea.

Напишите скрипт, который выбирает рандомную сеть из списка сетей, подключает w3 к выбранной сети,
выбирает следующую рандомную сеть, которая не равна текущей сети и делает отправку в нее пересылку
токенов.
Для отправки используются токены ETH, USDT, USDC, приоритет отдается стейблкоинам,
если есть оба токена, то выбирается тот у кого больше баланс, если нет стейблкоинов, то отправляется ETH.

Сумма определяется рандомно в пределах баланса токена на кошельке, оставляйте нативный токен
на комиссии.

"""

# пишите код тут


"""
Задание 3 - hard

Напишите класс Onchain:
В init класса должны быть переданы Chain и приватный ключ.
Методы: send_token, get_fee, get_balance, _get_abi, _prepare_tx_params, allowance, approve,
Допишите методы в класс Onchain:
_get_relay_request_id(self, to_chain: Chain, amount: float, from_token: Token | None = None, to_token: Token | None = None) -> str
метод bridge_relay(self, to_chain: Chain, amount: float, from_token: Token | None = None, to_token: Token | None = None) -> str

Методы должны работать с объектами Token и Chain.

Напишите скрипт, который получает список приватных ключей из файла private_keys.txt,
перемешивает их, берет рандомную сеть из списка сетей, создает объект Onchain.
Далее проверяет были ли у данного кошелька за последние 24 часа транзакции с bridge_relay, если да, то пропускает
если нет, делает отправку ETH / USDT / USDC в рандомную сеть из списка сетей.
Скрипт должен работать в бесконечном цикле и делать транзакцию по отправке токенов для каждого
кошелька раз в сутки. Сделайте рандомную паузу между транзакциями, чтобы они равномерно распределялись
в течении суток.
Порядок кошельков должен каждый день меняться, чтобы не было паттерна в транзакциях.

!Подсказка!
Для проверки наличия транзакций используйте https://www.ankr.com/docs/advanced-api/query-methods/#ankr_gettransactionsbyaddress
1. запросите транзакции в нужных сетях за последние 24 часа
3. проверьте наличие транзакций с bridge_relay по нативным токенам или ERC20 токенам
"""

# пишите код тут

