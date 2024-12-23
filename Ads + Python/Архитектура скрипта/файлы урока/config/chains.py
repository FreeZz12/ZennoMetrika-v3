from models import Chain
class Chains:

    ethereum = Chain(
        name='Ethereum',
        rpc='https://mainnet.infura.io/v3/8f5d0e3f7f4d4a1d8f3f2d4b0b2f8b1a',
        chain_id='1',
        native_token='ETH'
    )
    bsc = Chain(
        name='Binance Smart Chain',
        rpc='https://bsc-dataseed.binance.org/',
        chain_id='56',
        native_token='BNB')