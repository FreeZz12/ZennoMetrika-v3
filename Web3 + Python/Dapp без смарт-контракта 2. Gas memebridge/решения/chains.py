
class Chain:
    def __init__(self, name: str, rpc: str, native_token: str, chain_id: int, multiplier: float = 1.0):
        self.name = name
        self.rpc = rpc
        self.native_token = native_token
        self.chain_id = chain_id
        self.multiplier = multiplier

    def __eq__(self, other):
        return self.name == other.name and self.rpc == other.rpc and self.native_token == other.native_token and self.multiplier == other.multiplier

    def hash(self):
        return hash((self.name, self.rpc, self.native_token, self.chain_id, self.multiplier))



class Chains:
    EVM = Chain('EVM', 'evm', 'EVM', 0)
    Ethereum = Chain('Ethereum', 'https://1rpc.io/eth', 'ETH', 1)
    Arbitrum = Chain('Arbitrum', 'https://1rpc.io/arb', 'ETH', 42161)
    Optimism = Chain('Optimism', 'https://1rpc.io/op', 'ETH', 10)
    BSC = Chain('BSC', 'https://1rpc.io/bnb', 'BNB', 56)
    LINEA = Chain('LINEA', 'https://1rpc.io/linea', 'ETH', 59144, 1.3)
    BASE = Chain('LINEA', 'https://1rpc.io/base', 'ETH', 8453)
    POLYGON = Chain('POLYGON', 'https://1rpc.io/matic', 'MATIC', 137)
    MONAD = Chain('MONAD', 'https://testnet-rpc.monad.xyz', 'MON', 10143)
