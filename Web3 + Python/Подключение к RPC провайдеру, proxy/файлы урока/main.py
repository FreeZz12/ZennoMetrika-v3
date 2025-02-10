import asyncio

from web3 import AsyncWeb3, Web3, HTTPProvider, AsyncHTTPProvider, AsyncBaseProvider
from web3.module import Module
import fake_useragent


# ноды
# RPC провайдеры
# типы подключения к RPC провайдеру
# прокси и хедеры для запросов к RPC провайдеру
# 'proxies': {'http': f'http://{config.proxy}', 'https': f'http://{config.proxy}'},

# requests proxy proxies = {'http': http://user:pass@ip:port, 'https': http://user:pass@ip:port}
# aiohttp proxy proxy = 'http://user:pass@ip:port'

class ExtraModule(Module):

    def extra_method(self):
        print('extra method, test connections:', self.w3.is_connected())

    def create_pk(self) -> str:
        return self.w3.eth.account.create().key.hex()


def main():
    rpc_provider = 'https://1rpc.io/linea'
    w3 = Web3(HTTPProvider(rpc_provider))
    print(w3.is_connected())
    print(w3.eth.get_balance('0xAC8ce8fbC80115a22a9a69e42F50713AAe9ef2F7'))
    w3.from_wei(1000000000000000000, 'ether')


    # request_kwargs = {
    #     'headers': {
    #         'User-Agent': fake_useragent.UserAgent().chrome,
    #         "Content-Type": "application/json",
    #         'accept-encoding': 'gzip, deflate, br, zstd',
    #         'accept-language': 'ru,en;q=0.9',
    #         'origin': 'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn',
    #     },
    #     'proxies': {'http': f'http://{config.proxy}', 'https': f'http://{config.proxy}'},
    # }
    # http_provider = HTTPProvider(rpc_provider, request_kwargs=request_kwargs)
    w3 = Web3(http_provider, external_modules={'extra_module': ExtraModule})
    # w3.extra_module.extra_method()
    #
    # print(w3.is_connected())
    # # http провайдер, для каждого запроса создается новое соединение
    # # websockets провайдер, создается одно соединение и используется для всех запросов
    # pass

async def amain():

    rpc_provider = 'https://1rpc.io/eth'
    request_kwargs = {
        'headers': {
            'User-Agent': fake_useragent.UserAgent().chrome,
            "Content-Type": "application/json",
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'ru,en;q=0.9',
            'origin': 'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn',
        },
        # 'proxy': f'http://{config.proxy}'
    }
    http_provider = AsyncHTTPProvider(rpc_provider, request_kwargs=request_kwargs)
    w3 = AsyncWeb3(http_provider)
    print(await w3.is_connected())
    w3.provider

    # await close_sessions(http_provider)
    await w3.provider.disconnect()
    print('done')


async def close_sessions(provider: AsyncBaseProvider):
        # Close the underlying aiohttp client sessions
        for _, session in provider._request_session_manager.session_cache.items():
            await session.close()


if __name__ == '__main__':
    asyncio.run(amain())
    # main()
