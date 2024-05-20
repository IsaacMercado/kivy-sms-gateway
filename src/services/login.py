from typing import Callable
from urllib.parse import urljoin

import requests

from src.constants import HOST
from src.models.error import ApiError
from src.models.token import Token
from src.utils.logger import logger


def fetch_token(
    email: str,
    password: str,
    on_success: Callable[[Token], None],
    on_error: Callable[[ApiError], None],
):
    response = requests.post(
        urljoin(HOST, "/paseto_auth/token/"),
        json={
            "email": email,
            "password": password,
            "remember": True,
        },
    )
    data = response.json()

    if response.status_code == 200:
        logger.info("Token received")
        token = Token.from_json(data)
        on_success(token)
        return

    logger.error("Error token received")
    exception = ApiError(response.status_code, data)
    on_error(exception)
