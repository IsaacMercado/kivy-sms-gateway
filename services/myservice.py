from os import environ
from time import sleep

import requests
from android.storage import app_storage_path

from receiver import ImcomingSmsReceiver

argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')


def on_sms_received(messages):
    print('Received SMS:', messages)

    for message in messages:
        try:
            response = requests.post('http://127.0.0.1:8080/', json=message)
            print('Response:', response.status_code, response.text)
        except Exception as e:
            print('Error:', e)


def loop():
    print('Python service started with argument:', argument)
    receiver = ImcomingSmsReceiver(on_sms_received)
    receiver.start()

    settings_path = app_storage_path()

    while True:
        print('Python service is running...')
        with open(f'{settings_path}/service.log', 'a') as f:
            f.write('Python service is running...\n')
        sleep(10.)


if __name__ == '__main__':
    loop()
