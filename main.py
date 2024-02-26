import logging
from datetime import datetime

from android.storage import app_storage_path
from kivy import platform
from kivy.app import App
from kivy.uix.button import Button
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer
from watchdog.observers.inotify_buffer import logger as inotify_logger
from services.register import start_service, stop_service
from plyer import storagepath


inotify_logger.setLevel(logging.WARNING)


if platform == 'android':
    from android.permissions import Permission, request_permissions


class CustomEventHandler(RegexMatchingEventHandler):
    def on_modified(self, event: RegexMatchingEventHandler) -> None:
        print(
            f'{datetime.now().isoformat()} '
            f'- {event.event_type} - {event.src_path}'
        )


class MyApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([
                Permission.RECEIVE_SMS,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
                Permission.FOREGROUND_SERVICE,
            ])

            start_service('Myservice', 'Hola mundo')
            # self.run_observer()

        return Button(text='Hello world', on_press=self.callback)

    def on_sms_received(self, messages):
        print('Received SMS:', messages)

    def run_observer(self):
        if platform == 'android':
            settings_path = app_storage_path()
        else:
            settings_path = storagepath.get_application_dir()

        event_handler = CustomEventHandler(regexes=[r'.*service\.log$'])
        self.observer = Observer()
        self.observer.schedule(event_handler, settings_path)
        self.observer.start()

    def stop_observer(self):
        self.observer.stop()
        self.observer.join()

    def callback(self, instance):
        print('The button is being pressed!')
        if platform == 'android':
            stop_service('Myservice')
            # self.receiver.stop()
            # self.stop_observer()

    # def on_stop(self):
    #     if platform == 'android':
    #         self.receiver.stop()


if __name__ == '__main__':
    MyApp().run()
