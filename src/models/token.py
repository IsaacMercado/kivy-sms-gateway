from src.storages import Storage


class ErrorToken(Exception):
    pass


class Token:
    access_tag = 'access_token'
    refresh_tag = 'refresh_token'

    def __init__(self, access_token: str, refresh_token: str) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token

    @classmethod
    def from_json(cls, json: dict[str, any]) -> "Token":
        return cls(
            access_token=json["access_token"],
            refresh_token=json["refresh_token"]
        )

    def to_storage(self, storage: Storage) -> None:
        storage.set_string(self.access_tag, self.access_token)
        storage.set_string(self.refresh_tag, self.refresh_token)

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    @staticmethod
    def has_token(storage: Storage) -> bool:
        return storage.has_refresh_token()

    @classmethod
    def from_storage(cls, storage: Storage) -> "Token":
        access_token = storage.get_string(cls.access_tag)
        refresh_token = storage.get_string(cls.refresh_tag)

        if access_token is None or refresh_token is None:
            raise ErrorToken("Failed to load token from storage")

        return cls(
            access_token=access_token,
            refresh_token=refresh_token
        )
