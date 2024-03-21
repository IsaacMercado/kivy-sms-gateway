class Storage:
    def set_string(self, key: str, value: str) -> None:
        raise NotImplementedError

    def get_string(self, key: str) -> str:
        raise NotImplementedError
