from chains import Chain, Chains

from web3 import Web3


class TokenType:
    ERC20 = 'ERC20'
    STABLE = 'STABLE'
    NATIVE = 'NATIVE'
    WRAPPED = 'WRAPPED'


class Token:
    def __init__(self, name: str, address: str, decimals: int, chain: Chain,
                 token_type: str = TokenType.ERC20):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.decimals = decimals
        self.chain = chain
        self.token_type = token_type

    def __eq__(self, other):
        return self.name == other.name and self.address == other.address and self.decimals == other.decimals and self.chain == other.chain


class Tokens:
    USDT_OP = Token('USDT', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58', 6, Chains.Optimism,
                    TokenType.STABLE)
    USDC_OP = Token('USDC', '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', 6, Chains.Optimism,
                    TokenType.STABLE)
    ETH_ARBITRUM = Token('ETH', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 18, Chains.Arbitrum,
                         TokenType.NATIVE)
    WETH_ARBITRUM = Token('WETH', '0x82af49447d8a07e3bd95bd0d56f35241523fbab1', 18, Chains.Arbitrum,
                          TokenType.WRAPPED)
    USDT_ARBITRUM = Token('USDT', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', 6, Chains.Arbitrum,
                          TokenType.STABLE)
    USDC_ARBITRUM = Token('USDC', '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', 6, Chains.Arbitrum,
                          TokenType.STABLE)

    WETH_POLYGON = Token('WETH', '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619', 18, Chains.POLYGON,
                            TokenType.WRAPPED)



    @classmethod
    def get_token_by_name(cls, name: str, chain: Chain) -> Token | None:
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.name == name and token.chain == chain:
                    return token
        return None

    @classmethod
    def get_wrapped_native_token(cls, chain: Chain):
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.chain == chain and token.token_type == TokenType.WRAPPED:
                    return token

    @classmethod
    def get_native(cls, chain: Chain):
        token_name = f'{chain.native_token}_{chain.name}'
        if hasattr(cls, token_name):
            return getattr(cls, token_name)

        native_token = Token(
            chain.native_token,
            '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            18, chain,
            TokenType.NATIVE
        )
        setattr(cls, f'{chain.native_token}_{chain.name}', native_token)
        return native_token
