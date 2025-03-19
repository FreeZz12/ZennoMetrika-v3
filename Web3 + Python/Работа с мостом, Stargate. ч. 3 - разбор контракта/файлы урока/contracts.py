from web3 import Web3
from web3.contract import Contract

from chains import Chain, Chains
from utils import get_abi

class ContractRaw:
    def __init__(self, name: str, address: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.chain = chain
        self._contract: Contract | None = None
        self._abi: dict | None = None

    @property
    def abi(self):
        if self._abi is None:
            self._abi = get_abi(self.name)
        return self._abi

    def get_contract(self, w3: Web3) -> Contract:
        if self._contract is None:
            self._contract = w3.eth.contract(address=self.address, abi=self.abi)
        return self._contract

    def print_contract_functions(self):
        contract = Web3().eth.contract(address=self.address, abi=self.abi)
        functions = contract.all_functions()
        for func in functions:
            print(f'name: {func.fn_name}')
            inputs = func.abi['inputs']

            for i, input in enumerate(inputs):
                print(f'    input {i}: {input["name"]} ({input["type"]})')

            outputs = func.abi['outputs']
            for i, output in enumerate(outputs):
                print(f'    output {i}: {output["name"]} ({output["type"]})')

            print('-----------------')


class Contracts:
    uniswap_router_v4_ethereum = ContractRaw(
        name='uniswap_router_v4',
        address='0x66a9893cc07d91d95644aedd05d03f95e1dba8af',
        chain=Chains.Ethereum
    )

    uniswap_router_v4_arbitrum = ContractRaw(
        name='uniswap_router_v4',
        address='0xA51afAFe0263b40EdaEf0Df8781eA9aa03E381a3',
        chain=Chains.Arbitrum
    )
    uniswap_router_v4_optimism = ContractRaw(
        name='uniswap_router_v4',
        address='0x851116d9223fabed8e56c0e6b8ad0c31d98b3507',
        chain=Chains.Optimism
    )

    uniswap_router_v4_sepolia = ContractRaw(
        name='uniswap_router_v4',
        address='0x3a9d48ab9751398bbfa63ad67599bb04e4bdf98b',
        chain=Chains.SEPOLIA
    )

    stargate_pool_usdc_optimism = ContractRaw(
        name='stargate_pool_usdc',
        address='0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
        chain=Chains.Optimism
    )

    stargate_pool_usdt_optimism = ContractRaw(
        name='stargate_pool_usdt',
        address='0x19cFCE47eD54a88614648DC3f19A5980097007dD',
        chain=Chains.Optimism
    )

    stargate_pool_eth_optimism = ContractRaw(
        name='stargate_pool_native',
        address='0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        chain=Chains.Optimism
    )

    stargate_pool_usdc_arb = ContractRaw(
        name='stargate_pool_usdc',
        address='0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        chain=Chains.Arbitrum
    )

    stargate_pool_usdt_arb = ContractRaw(
        name='stargate_pool_usdt',
        address='0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
        chain=Chains.Arbitrum
    )

    stargate_pool_eth_arb = ContractRaw(
        name='stargate_pool_native',
        address='0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F',
        chain=Chains.Arbitrum
    )

    @classmethod
    def get_contract_raw_by_name_and_chain(cls, name: str, chain: Chain) -> ContractRaw | None:
        for contract in cls.__dict__.values():
            if isinstance(contract, ContractRaw) and contract.name == name and contract.chain == chain:
                return contract
        raise ValueError(f"Contract {name} not found for chain {chain.name}.")

    @classmethod
    def __getitem__(cls, item):
        if hasattr(cls, item):
            return getattr(cls, item)
        raise KeyError(f"Contract {item} not found.")



if __name__ == '__main__':
    # Example usage
    Contracts.stargate_pool_usdc_optimism.print_contract_functions()