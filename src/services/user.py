from typing import Callable
from urllib.parse import urljoin

import requests

from src.constants import HOST
from src.models.error import ApiError
from src.models.token import Token
from src.models.user import User
from src.services.refresh_token import fetch_refresh_token
from src.storages import Storage
from src.utils.logger import logger


def fetch_user(
    on_success: Callable[[User], None],
    on_error: Callable[[ApiError], None],
    storage: Storage | None = None
):
    def _on_success(token: Token):
        response = requests.get(
            urljoin(HOST, "/paseto_auth/users/me/"),
            headers=token.get_headers(),
        )

        if response.status_code != 200:
            logger.error("Error fetching user")
            exception = ApiError(response.status_code, {})
            on_error(exception)
            return

        logger.info("User fetched")
        data = response.json()
        user = User.from_json(data)
        on_success(user)

    fetch_refresh_token(
        storage=storage,
        on_success=_on_success,
        on_error=on_error,
    )
