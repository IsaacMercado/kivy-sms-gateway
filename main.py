import asyncio

from kivy.core.window import Window

from src.app import SMSGatewayApp

if __name__ == '__main__':
    # Window.size = (2400, 1800)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(SMSGatewayApp().async_run(async_lib='asyncio'))
    loop.close()
