import json

from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.utils.subscriptions import LogsSubscription, LogsSubscriptionContext
import config

with open('erc20.json') as f:
    abi = json.load(f)

async def new_heads_handler(
    handler_context: LogsSubscriptionContext,
) -> None:
    log_receipt = handler_context.result
    print(f"New log: {log_receipt}\n")

    event_data = handler_context.transfer_event.process_log(log_receipt)
    print(f"Log event data: {event_data}\n")

def pad_address(addr: str) -> str:
    """
    Приводит 20-байтовый адрес к 32-байтовому формату (0x + 64 hex символа),
    дополняя его ведущими нулями.
    """
    addr_clean = addr.lower().replace("0x", "")
    return "0x" + addr_clean.rjust(64, "0")


async def context_manager_subscription_example():

    async with AsyncWeb3(WebSocketProvider(config.wss_rpc)) as w3:  # for the WebSocketProvider
        with open('wallets.txt') as f:
            wallets = f.read().splitlines()
        wallets = [pad_address(addr) for addr in wallets]

        contract_address = w3.to_checksum_address('0xdac17f958d2ee523a2206206994597c13d831ec7') # usdt
        usdt_contract = w3.eth.contract(address=contract_address, abi=abi)
        sub = LogsSubscription(
            label='USDT Transfer',
            address=usdt_contract.address,
            topics=[usdt_contract.events.Transfer().topic, wallets],
            handler=new_heads_handler,
            handler_context={"transfer_event": usdt_contract.events.Transfer()}
        )

        await w3.subscription_manager.subscribe([sub])
        await w3.subscription_manager.handle_subscriptions()

if __name__ == '__main__':
    import asyncio
    asyncio.run(context_manager_subscription_example())