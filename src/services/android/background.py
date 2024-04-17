import asyncio
from os import environ

from android.storage import app_storage_path

from src.models.token import Token
from src.receiver import ImcomingSmsReceiver
from src.services.send_sms import send_sms_data
from src.storages.core import CoreStorage

argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')


async def main():
    print('Python service started with argument:', argument)
    messages = []
    storage = CoreStorage()

    ImcomingSmsReceiver(messages.append).start()
    # settings_path = app_storage_path()

    while True:
        if not messages or Token.has_token(storage):
            await asyncio.sleep(1.)
            # print('Python service is running...')
            continue

        # with open(f'{settings_path}/service.log', 'a') as f:
        #     f.write('Python service is running...\n')

        try:
            token = Token.from_storage(storage)
            await asyncio.gather(*[
                send_sms_data(
                    message,
                    refresh_token=token.refresh_token,
                ) for message in messages
            ])
        except IndexError:
            continue


if __name__ == '__main__':
    asyncio.run(main())
