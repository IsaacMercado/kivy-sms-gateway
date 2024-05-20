from urllib.parse import urljoin

from src.constants import HOST
from src.models.error import ApiError
from src.models.user import User
from src.services.refresh_token import fetch_refresh_token
from src.storages import Storage
from src.utils.async_requests import http_get
from src.utils.logger import logger


async def fetch_user(storage: Storage | None = None):
    token = await fetch_refresh_token(storage=storage)
    response = await http_get(
        urljoin(HOST, "/paseto_auth/users/me/"),
        headers=token.get_headers(),
    )

    if response.status_code != 200:
        logger.error("Error fetching user")
        raise ApiError(response.status_code, {})

    logger.info("User fetched")
    data = response.json()
    return User.from_json(data)
