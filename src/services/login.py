from urllib.parse import urljoin

from src.constants import HOST
from src.models.token import Token
from src.models.error import ApiError
from src.utils.async_requests import http_post


async def fetch_token(email: str, password: str):
    response = await http_post(
        urljoin(HOST, "/paseto_auth/token/"),
        json={"email": email, "password": password}
    )
    data = response.json()

    if response.status_code == 200:
        return Token.from_json(data)

    raise ApiError(response.status_code, data)
