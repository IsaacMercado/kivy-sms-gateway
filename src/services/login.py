from urllib.parse import urljoin

from src.constants import HOST
from src.models.error import ApiError
from src.models.token import Token
from src.utils.async_requests import http_post
from src.utils.logger import logger


async def fetch_token(email: str, password: str):
    response = await http_post(
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
        return Token.from_json(data)

    logger.error("Error token received")
    raise ApiError(response.status_code, data)
