import logging
from datetime import datetime

from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import BaseObserverSubclassCallable, Observer
from watchdog.observers.inotify_buffer import logger as inotify_logger

from src.utils.path import get_app_path

inotify_logger.setLevel(logging.WARNING)


class CustomEventHandler(RegexMatchingEventHandler):
    def on_modified(self, event: RegexMatchingEventHandler) -> None:
        print(
            f'{datetime.now().isoformat()} '
            f'- {event.event_type} - {event.src_path}'
        )


def run_observer():
    settings_path = get_app_path()
    event_handler = CustomEventHandler(regexes=[r'.*service\.log$'])
    observer = Observer()
    observer.schedule(event_handler, settings_path)
    observer.start()


def stop_observer(observer: BaseObserverSubclassCallable):
    observer.stop()
    observer.join()
