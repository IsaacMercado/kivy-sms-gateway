import logging
from datetime import datetime

from kivy import platform
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer, BaseObserverSubclassCallable
from watchdog.observers.inotify_buffer import logger as inotify_logger

inotify_logger.setLevel(logging.WARNING)


class CustomEventHandler(RegexMatchingEventHandler):
    def on_modified(self, event: RegexMatchingEventHandler) -> None:
        print(
            f'{datetime.now().isoformat()} '
            f'- {event.event_type} - {event.src_path}'
        )


def run_observer():
    if platform == 'android':
        from android.storage import app_storage_path
        settings_path = app_storage_path()
    else:
        from plyer import storagepath
        settings_path = storagepath.get_application_dir()

    event_handler = CustomEventHandler(regexes=[r'.*service\.log$'])
    observer = Observer()
    observer.schedule(event_handler, settings_path)
    observer.start()


def stop_observer(observer: BaseObserverSubclassCallable):
    observer.stop()
    observer.join()
