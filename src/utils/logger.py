import logging
from typing import Callable

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from watchdog.observers.inotify_buffer import logger as inotify_logger

from src.utils.path import get_app_path

inotify_logger.setLevel(logging.WARNING)

LEVEL = logging.INFO
FILENAME = 'service.log'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

formatter = logging.Formatter(
    (
        '%(asctime)s - '
        '%(name)s - '
        '%(levelname)s - '
        '%(message)s'
    ),
    datefmt=DATE_FORMAT,
)

handler = logging.FileHandler(
    filename=f'{get_app_path()}/{FILENAME}',
    encoding='utf-8',
)
handler.setLevel(LEVEL)
handler.setFormatter(formatter)

logger = logging.getLogger("kivy_sms_gateway")
logger.setLevel(LEVEL)
logger.addHandler(handler)


class LogEventHandler(PatternMatchingEventHandler):
    def __init__(self, on_modified: Callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__on_modified = on_modified

    def on_modified(self, event: FileSystemEvent) -> None:
        self.__on_modified(event)


class LogObserver(object):
    def __init__(self, on_added: Callable[[list[str]], None], filename: str = FILENAME, **kwargs):
        super().__init__(**kwargs)
        self.__on_added = on_added
        self.__logs = []
        self.__filename = filename
        self.__path = get_app_path()
        self.__file = open(f'{self.__path}/{self.__filename}', 'r+')
        self.__observer = Observer()
        self.__event_handler = LogEventHandler(
            on_modified=self.__on_event,
            patterns=[self.__filename],
        )
        self.__observer.schedule(
            self.__event_handler,
            self.__path,
        )
        self.update()

    @property
    def logs(self) -> list[str]:
        return self.__logs

    def clear(self):
        self.__logs.clear()
        self.__file.truncate(0)

    def update(self):
        temp = []
        for line in self.__file.readlines():
            line = line.strip()
            temp.append(line)
            self.__logs.append(line)

        self.__on_added(temp)

    def __on_event(self, event: FileSystemEvent):
        self.update()

    def start(self):
        self.__observer.start()

    def stop(self):
        self.__observer.stop()
        self.__observer.join()
