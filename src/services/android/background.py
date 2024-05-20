from os import environ
from threading import Thread
from time import sleep

from jnius import autoclass

from src.models.token import Token
from src.receiver import ImcomingSmsReceiver
from src.services.send_sms import send_sms_data
from src.storages.core import CoreStorage
from src.utils.logger import logger


def main():
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)
    argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')

    logger.info('Python service started with argument: %s', argument)
    messages = []

    ImcomingSmsReceiver(messages.extend).start()

    while True:
        storage = CoreStorage()

        if not messages or not Token.has_token(storage):
            print("Not logger in or no messages to send...")
            sleep(1.)
            continue

        logger.info("Sending messages...")

        try:
            token = Token.from_storage(storage)

            while messages:
                message = messages.pop(0)
                thread = Thread(
                    target=send_sms_data,
                    args=(message, print, print),
                    kwargs={'refresh_token': token.refresh_token},
                )
                thread.start()
        except IndexError:
            continue


if __name__ == '__main__':
    main()
