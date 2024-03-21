from urllib.parse import urljoin

from aiohttp import ClientSession

from src.constants import HOST
from src.models.user import User
from src.storages import Storage
from src.services.refresh_token import fetch_refresh_token


async def fetch_user(session: ClientSession, storage: Storage | None = None):
    token = await fetch_refresh_token(session, storage=storage)

    async with session.get(
        urljoin(HOST, "/paseto_auth/users/me/"),
        headers=token.get_headers(),
    ) as response:
        data = await response.json()
        return User.from_json(data)
