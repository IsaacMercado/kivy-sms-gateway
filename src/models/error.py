from typing import Any


class ApiError(Exception):
    def __init__(self, status: int, data: dict[str, Any]):
        super().__init__(f"Error api {status}")
        self.status = status
        self.data = data
        self.non_field = []
        self.fields = {}

        for key, value in data.items():
            if key == "non_field_errors":
                self.non_field = list(value)
            elif key == "detail":
                self.non_field = [value]
            else:
                self.fields[key] = list(value)

    def clear(self):
        self.non_field.clear()
        self.fields.clear()
