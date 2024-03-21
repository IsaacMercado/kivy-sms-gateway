from urllib.parse import urljoin

from aiohttp import ClientSession

from src.constants import HOST
from src.models.token import Token
from src.models.error import ApiError


async def fetch_token(session: ClientSession, email: str, password: str):
    async with session.post(
        urljoin(HOST, "/paseto_auth/token/"),
        json={"email": email, "password": password}
    ) as response:
        data = await response.json()

        if response.status == 200:
            return Token.from_json(data)

        raise ApiError(response.status, data)
