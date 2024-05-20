import asyncio
from os import environ

from jnius import autoclass

from src.models.token import Token
from src.receiver import ImcomingSmsReceiver
from src.services.send_sms import send_sms_data
from src.storages.core import CoreStorage
from src.utils.logger import logger


async def main():
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)
    argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')

    await asyncio.to_thread(logger.info, 'Python service started with argument: %s', argument)
    messages = []

    ImcomingSmsReceiver(messages.append).start()

    while True:
        storage = CoreStorage()

        if not messages or not Token.has_token(storage):
            print("Not logger in or no messages to send...")
            await asyncio.sleep(1.)
            continue

        await asyncio.to_thread(logger.info, "Sending messages...")

        try:
            token = Token.from_storage(storage)

            await asyncio.gather(*[
                send_sms_data(
                    message,
                    refresh_token=token.refresh_token,
                ) for message in messages.pop(0)
            ])
        except IndexError:
            continue


if __name__ == '__main__':
    asyncio.run(main())
