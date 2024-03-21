from typing import Any


class ApiError(Exception):
    def __init__(self, status, data):
        super().__init__(f"Error api {status}")
        self.status = status
        self.data = data
        self.non_field = []
        self.fields = {}

    @classmethod
    def from_json(cls, json: dict[str, Any]):
        error = cls()
        for key, value in json.items():
            if key == "non_field_errors":
                error.non_field = list(value)
            elif key == "detail":
                error.non_field = [value]
            else:
                error.fields[key] = list(value)
        return error

    def clear(self):
        self.non_field.clear()
        self.fields.clear()
