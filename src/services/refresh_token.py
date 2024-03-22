from urllib.parse import urljoin


from src.constants import HOST
from src.models.error import ApiError
from src.models.token import Token
from src.storages import Storage
from src.utils.async_requests import http_post


async def fetch_refresh_token(refresh_token: str | None = None, storage: Storage | None = None):
    assert refresh_token is not None or storage is not None

    if refresh_token is None:
        token = Token.from_storage(storage)
        refresh_token = token.refresh_token

    response = await http_post(
        urljoin(HOST, "/paseto_auth/token/refresh/"),
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    data = response.json()

    if response.status_code == 200:
        data[Token.refresh_tag] = refresh_token
        return Token.from_json(data)

    raise ApiError(response.status_code, data)
