import asyncio
from os import environ
from time import sleep

from android.storage import app_storage_path

from src.models.token import Token
from src.receiver import ImcomingSmsReceiver, SmsMessage
from src.services.send_sms import send_sms_data
from src.storages import Storage

argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')


async def send_all_sms(messages: list[SmsMessage], storage: Storage):
    token = Token.from_storage(storage)

    await asyncio.gather(*[
        send_sms_data(message, refresh_token=token.refresh_token)
        for message in messages
    ])


def on_sms_received(messages: list[SmsMessage]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_all_sms(messages))


def loop():
    print('Python service started with argument:', argument)

    # ImcomingSmsReceiver(on_sms_received).start()
    # settings_path = app_storage_path()

    while True:
        print('Python service is running...')
        # with open(f'{settings_path}/service.log', 'a') as f:
        #     f.write('Python service is running...\n')
        sleep(10.)


if __name__ == '__main__':
    loop()
