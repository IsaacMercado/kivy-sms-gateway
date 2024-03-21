from src.storages import Storage


class ErrorUser(Exception):
    pass


class User:
    def __init__(
        self,
        username: str,
        first_name: str,
        last_name: str,
        person_id: str,
        birthday: str | None,
        affiliated_phone_number: str | None,
        alternative_phone_number: str | None,
    ) -> None:
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.person_id = person_id
        self.birthday = birthday
        self.affiliated_phone_number = affiliated_phone_number
        self.alternative_phone_number = alternative_phone_number

    @classmethod
    def from_json(cls, json: dict[str, any]) -> "User":
        return cls(
            username=json["username"],
            first_name=json["first_name"],
            last_name=json["last_name"],
            person_id=json["person_id"],
            birthday=json.get("birthday"),
            affiliated_phone_number=json.get("affiliated_phone_number"),
            alternative_phone_number=json.get("alternative_phone_number"),
        )

    def to_preferences(self, storage: Storage) -> None:
        storage.set_string("username", self.username)
        storage.set_string("first_name", self.first_name)
        storage.set_string("last_name", self.last_name)
        storage.set_string("person_id", self.person_id)

        if self.birthday is not None:
            storage.set_string("birthday", self.birthday)

        if self.affiliated_phone_number is not None:
            storage.set_string(
                "affiliated_phone_number",
                self.affiliated_phone_number
            )

        if self.alternative_phone_number is not None:
            storage.set_string(
                "alternative_phone_number",
                self.alternative_phone_number
            )

    @classmethod
    def from_preferences(cls, storage: Storage) -> "User":
        username = storage.get_string("username")
        first_name = storage.get_string("first_name")
        last_name = storage.get_string("last_name")
        person_id = storage.get_string("person_id")
        birthday = storage.get_string("birthday")
        affiliated_phone_number = storage.get_string(
            "affiliated_phone_number"
        )
        alternative_phone_number = storage.get_string(
            "alternative_phone_number"
        )

        if None in (username, first_name, last_name, person_id):
            raise ErrorUser("Failed to load user from storage")

        return cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            person_id=person_id,
            birthday=birthday,
            affiliated_phone_number=affiliated_phone_number,
            alternative_phone_number=alternative_phone_number,
        )
