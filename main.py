import asyncio

from src.app import SMSGatewayApp

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SMSGatewayApp().async_run(async_lib='asyncio'))
    loop.close()
