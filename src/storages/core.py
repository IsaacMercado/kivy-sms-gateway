from os import path

from kivy.storage.dictstore import DictStore

from src.storages import Storage
from src.utils.path import get_app_path


class CoreStorage(Storage):
    def __init__(self) -> None:
        self._storage = DictStore(path.join(
            get_app_path(),
            'custom_storage.pickle',
        ))

    def set_string(self, key: str, value: str) -> None:
        self._storage.put(key, value=value)

    def get_string(self, key: str) -> str:
        return self._storage.get(key).get("value")
