import time

from web3 import Web3
from eth_abi import encode

from amount import Amount
from chains import Chains, Chain
from config import config
from tokens import Token, Tokens, TokenType
from utils import get_abi, get_tx_params, sing_send_tx, approve


class CotractData:
    def __init__(self, name: str, address: str, chain: Chain):
        self.name = name
        self.address = Web3.to_checksum_address(address)
        self.chain = chain


class Contracts:
    fee_collector_arb = CotractData(
        name='fee_collector',
        address='0x89f30783108e2f9191db4a44ae2a516327c99575',
        chain=Chains.Arbitrum
    )

    fee_collector_usdc_arb = CotractData(
        name='fee_collector_usdc',
        address='0x7ffc3dbf3b2b50ff3a1d5523bc24bb5043837b14',
        chain=Chains.Arbitrum
    )

    fee_collector_op = CotractData(
        name='fee_collector',
        address='0x3d83ec320541ae96c4c91e9202643870458fb290',
        chain=Chains.Optimism
    )

    fee_collector_usdc_op = CotractData(
        name='fee_collector_usdc',
        address='0x7ffc3dbf3b2b50ff3a1d5523bc24bb5043837b14',
        chain=Chains.Optimism
    )

    uniswap_quoter_op = CotractData(
        name='uniswap_quoter',
        address='0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6',
        chain=Chains.Optimism
    )

    uniswap_quoter_arb = CotractData(
        name='uniswap_quoter',
        address='0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6',
        chain=Chains.Arbitrum
    )

    uniswap_router_op = CotractData(
        name='uniswap_router',
        address='0x851116d9223fabed8e56c0e6b8ad0c31d98b3507',
        chain=Chains.Optimism
    )

    uniswap_router_arb = CotractData(
        name='uniswap_router',
        address='0xa51afafe0263b40edaef0df8781ea9aa03e381a3',
        chain=Chains.Arbitrum
    )

    uniswap_permit2_arbitrum = CotractData(
        name='uniswap_permit2',
        address='0x000000000022d473030f116ddee9f6b43ac78ba3',
        chain=Chains.Arbitrum)

    uniswap_permit2_op = CotractData(
        name='uniswap_permit2',
        address='0x000000000022D473030F116dDEE9F6B43aC78BA3',
        chain=Chains.Optimism)

    @classmethod
    def get_contract_data_by_name(cls, name: str, chain: Chain) -> CotractData:
        for contract in cls.__dict__.values():
            if isinstance(contract, CotractData):
                if contract.name == name and contract.chain == chain:
                    return contract
        raise ValueError(f"Contract {name} not found for chain {chain.name}")


class Commands:
    PERMIT2PERMIT = '0a'
    WRAP_ETH = '0b'
    SWAP_EXACT_IN = '00'
    PAY_PORTION = '06'
    SWEEP = '04'
    UNWRAP_WETH = '0c'


class Addresses:
    ADDRESS_THIS = '0x0000000000000000000000000000000000000002'


def get_wrap_data(amount: Amount):
    return '0x' + encode(['address', 'uint256'], [Addresses.ADDRESS_THIS, amount.wei]).hex()


def get_swap_data(path: str, amount: Amount, from_token: Token):
    recipient = Addresses.ADDRESS_THIS
    amount_in = amount.wei
    amount_out_min = 0
    payer_is_user = False if from_token.token_type == TokenType.NATIVE else True
    swap_input = encode(
        ['address', 'uint256', 'uint256', 'bytes', 'bool'],
        [
            recipient,
            amount_in,
            amount_out_min,
            bytes.fromhex(path),
            payer_is_user
        ]
    )
    return '0x' + swap_input.hex()


def get_pay_portion_data(to_token: Token):
    fee_collector = Contracts.get_contract_data_by_name('fee_collector', to_token.chain)
    usdc_fee_collector = Contracts.get_contract_data_by_name('fee_collector_usdc', to_token.chain)
    if to_token.name == 'USDC':
        fee_collector = usdc_fee_collector

    wrap_token = Tokens.get_wrapped_native_token(to_token.chain)
    _to_token = wrap_token if to_token.token_type == TokenType.NATIVE else to_token

    token_address = _to_token.address
    recipient = fee_collector.address
    bips = 25
    return '0x' + encode(['address', 'address', 'uint256'], [token_address, recipient, bips]).hex()


def get_amount_out(w3: Web3, chain: Chain, path: str, amount: Amount):
    quoter_data = Contracts.get_contract_data_by_name('uniswap_quoter', chain)
    contract = w3.eth.contract(address=quoter_data.address, abi=get_abi('uniswap_quoter'))
    amount_out = contract.functions.quoteExactInput(
        bytes.fromhex(path),
        amount.wei
    ).call()

    return amount_out


def get_sweep_data(w3: Web3, path: str, amount: Amount, to_token: Token):
    amount_out = get_amount_out(w3, to_token.chain, path, amount)
    min_amount_out = int(amount_out * 0.945)
    sweep_data = encode(['address', 'address', 'uint256'],
                        [to_token.address, w3.eth.default_account, min_amount_out]).hex()
    return '0x' + sweep_data


def get_path(from_token: Token, to_token: Token) -> str:
    wrap_token = Tokens.get_wrapped_native_token(from_token.chain)
    _from_token = wrap_token if from_token.token_type == TokenType.NATIVE else from_token
    _to_token = wrap_token if to_token.token_type == TokenType.NATIVE else to_token
    fee = hex(500)[2:].zfill(6)
    return _from_token.address[2:] + fee + _to_token.address[2:]


def get_permit2_allowance(w3: Web3, from_token: Token, spender: str) -> tuple[int, int, int]:
    permit2_data = Contracts.get_contract_data_by_name('uniswap_permit2', from_token.chain)
    contract = w3.eth.contract(address=permit2_data.address, abi=get_abi('uniswap_permit2'))
    allowance, expiration, nonce = contract.functions.allowance(
        w3.eth.default_account,
        from_token.address,
        spender
    ).call()
    return allowance, expiration, nonce


def permit2(w3: Web3, from_token: Token, permit_address: str, expiration: int, nonce: int, spender: str,
            sig_deadline: int, private_key: str) -> bytes:
    full_message = {
        "types": {
            "PermitSingle": [
                {
                    "name": "details",
                    "type": "PermitDetails"
                },
                {
                    "name": "spender",
                    "type": "address"
                },
                {
                    "name": "sigDeadline",
                    "type": "uint256"
                }
            ],
            "PermitDetails": [
                {
                    "name": "token",
                    "type": "address"
                },
                {
                    "name": "amount",
                    "type": "uint160"
                },
                {
                    "name": "expiration",
                    "type": "uint48"
                },
                {
                    "name": "nonce",
                    "type": "uint48"
                }
            ],
            "EIP712Domain": [
                {
                    "name": "name",
                    "type": "string"
                },
                {
                    "name": "chainId",
                    "type": "uint256"
                },
                {
                    "name": "verifyingContract",
                    "type": "address"
                }
            ]
        },
        "domain": {
            "name": "Permit2",
            "chainId": from_token.chain.chain_id,
            "verifyingContract": permit_address
        },
        "primaryType": "PermitSingle",
        "message": {
            "details": {
                "token": from_token.address,
                "amount": 2 ** 160 - 1,
                "expiration": expiration,
                "nonce": nonce
            },
            "spender": spender,
            "sigDeadline": sig_deadline
        }
    }
    singed_permit = w3.eth.account.sign_typed_data(full_message=full_message, private_key=private_key)
    return singed_permit['signature']


def get_permit2_data(w3: Web3, amount: Amount, from_token: Token, spender: str, permit_address: str, private_key: str) -> str | None:
    allowance, expiration, nonce = get_permit2_allowance(w3, from_token, spender)
    if allowance > amount.wei and expiration > int(time.time()):
        return None
    expiration = int(time.time() + 60 * 60 * 24 * 30)
    sig_deadline = int(time.time() + 60 * 30)
    data = permit2(w3, from_token, permit_address, expiration, nonce, spender, sig_deadline, private_key)
    permit_details = (
        from_token.address,
        2 ** 160 - 1,
        expiration,
        nonce
    )
    permit_single = (
        permit_details,
        spender,
        sig_deadline
    )
    permit2_data = encode(
        ['((address,uint160,uint48,uint48),address,uint256)', 'bytes'],
        [permit_single, data]
    )
    return '0x' + permit2_data.hex()

def get_unwrap_data(w3: Web3, to_token: Token, path: str, amount: Amount):
    amount_out = get_amount_out(w3, to_token.chain, path, amount)
    min_amount_out = int(amount_out * 0.945)
    unwrap_data = encode(['address', 'uint256'], [w3.eth.default_account, min_amount_out])
    return '0x' + unwrap_data.hex()

def swap(w3: Web3, amount: Amount, from_token: Token, to_token: Token, private_key: str):
    commands = '0x'
    inputs = list()

    contract_data = Contracts.get_contract_data_by_name('uniswap_router', from_token.chain)

    if from_token.token_type != TokenType.NATIVE:
        permit2_data = Contracts.get_contract_data_by_name('uniswap_permit2', from_token.chain)
        approve(
            w3,
            from_token,
            permit2_data.address,
            amount,
            private_key,
            is_max=True
        )

        input_permit2 = get_permit2_data(w3, amount, from_token, contract_data.address, permit2_data.address, private_key)
        if input_permit2:
            commands += Commands.PERMIT2PERMIT
            inputs.append(input_permit2)


    if from_token.token_type == TokenType.NATIVE:
        commands += Commands.WRAP_ETH
        encoded = get_wrap_data(amount)
        inputs.append(encoded)

    path = get_path(from_token, to_token)

    commands += Commands.SWAP_EXACT_IN
    swap_input = get_swap_data(path, amount, from_token)
    inputs.append(swap_input)

    commands += Commands.PAY_PORTION
    pay_portion_input = get_pay_portion_data(to_token)
    inputs.append(pay_portion_input)

    if to_token.token_type == TokenType.NATIVE:
        commands += Commands.UNWRAP_WETH
        unwrap_data = get_unwrap_data(w3, to_token, path, amount)
        inputs.append(unwrap_data)
    else:
        sweep_data = get_sweep_data(w3, path, amount, to_token)
        commands = commands + Commands.SWEEP
        inputs.append(sweep_data)

    deadline = int(time.time() + 60 * 30)

    contract = w3.eth.contract(address=contract_data.address, abi=get_abi('uniswap_router'))

    value = amount.wei if from_token.token_type == TokenType.NATIVE else 0

    tx_params = get_tx_params(w3, value=value)
    tx_params = contract.functions.execute(
        commands,
        inputs,
        deadline
    ).build_transaction(tx_params)

    tx_params['data'] = tx_params['data'] + '0c'

    tx_hash = sing_send_tx(w3, tx_params, private_key)
    print(f"Transaction hash: {tx_hash}")


def main():
    work_chain = Chains.Optimism
    w3 = Web3(Web3.HTTPProvider(work_chain.rpc))
    w3.eth.default_account = w3.eth.account.from_key(config.private_key).address
    from_token = Tokens.get_native(work_chain)
    to_token = Tokens.get_token_by_name('USDT', work_chain)
    amount = Amount(0.00005, decimals=from_token.decimals)
    swap(w3, amount, from_token, to_token, config.private_key)


if __name__ == '__main__':
    main()
