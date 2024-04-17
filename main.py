import asyncio

from src.app import MyApp

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyApp().async_run(async_lib='asyncio'))
    loop.close()
