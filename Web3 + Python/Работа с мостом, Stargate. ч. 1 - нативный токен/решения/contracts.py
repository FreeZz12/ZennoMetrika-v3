from web3 import Web3
from web3.contract import Contract

from chains import Chain, Chains
from utils import get_abi

class ContractData:
    def __init__(self, name: str, address: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.chain = chain
        self._abi = None

    @property
    def abi(self):
        if not self._abi:
            self._abi = get_abi(self.name)
        return self._abi

    def get_contract(self, w3: Web3) -> Contract:
        return w3.eth.contract(address=self.address, abi=self.abi)


class ContractsData:
    """
    хранилище адресов контрактов для разных сетей и их ABI.
    """
    def __init__(self, name: str, contracts: dict[Chain, str]):
        self.name = name
        self._contracts = contracts


    def __getitem__(self, chain: Chain) -> ContractData:
        """
        Получить объект с данными контракта по объекту Chain.
        Чтобы можно было извлечь данные контракта как из словаря.
        """
        return self.__getattr__(chain.name.lower())

    def __getattr__(self, chain_name: str) -> ContractData:
        """
        Если не найден атрибут с данными контракта, то создаётся новый объект с данными контракта
        и добавляется в атрибуты класса.
        """
        chain_name = chain_name.lower()
        for chain, address in self._contracts.items():
            if chain.name.lower() == chain_name:
                address = Web3.to_checksum_address(address)
                contract_data = ContractData(name=self.name, address=address, chain=chain)
                self.__setattr__(chain_name.lower(), contract_data)
                return contract_data
        raise AttributeError(f"Contract '{self.name}' not found for chain '{chain_name}'")


class Contracts:
    """
    Хранилище объектов с данными контрактов.
    """
    stargate_pool_native = ContractsData('stargate_pool_native', {
        Chains.ARBITRUM: '0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F',
        Chains.OP: '0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        Chains.BASE: '0xdc181Bd607330aeeBEF6ea62e03e5e1Fb4B6F7C7',
        Chains.LINEA: '0x81F6138153d473E8c5EcebD3DC8Cd4903506B075'
    })

    stargate_pool_usdc = ContractsData('stargate_pool_usdc', {
        Chains.ARBITRUM: '0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        Chains.OP: '0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
    })

    stargate_pool_usdt = ContractsData('stargate_pool_usdt', {
        Chains.ARBITRUM: '0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
        Chains.OP: '0x19cFCE47eD54a88614648DC3f19A5980097007dD',
    })

    @classmethod
    def get_contracts_data_by_name(cls, name: str) -> ContractsData:
        """
        Получить объект с данными контракта по имени контракта.
        :param name: имя контракта
        :return: объект с данными контракта
        """
        name = name.lower()
        for contracts_data in cls.__dict__.values():
            if isinstance(contracts_data, ContractsData) and contracts_data.name.lower() == name:
                return contracts_data
        raise AttributeError(f"Contract '{name}' not found")



