from urllib.parse import urljoin

from aiohttp import ClientSession

from src.constants import HOST
from src.storages import Storage
from src.models.token import Token


async def fetch_refresh_token(
    session: ClientSession,
    refresh_token: str | None = None,
    storage: Storage | None = None,
):
    assert refresh_token is not None or storage is not None

    if refresh_token is None:
        token = Token.from_storage(storage)
        refresh_token = token.refresh_token

    async with session.post(
        urljoin(HOST, "/paseto_auth/token/refresh/"),
        headers={"Authorization": f"Bearer {refresh_token}"},
    ) as response:
        data = await response.json()
        data[Token.refresh_tag] = refresh_token
        return Token.from_json(data)
