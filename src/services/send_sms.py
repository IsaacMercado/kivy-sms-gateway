import re
from urllib.parse import urljoin

from src.constants import HOST
from src.models.error import ApiError
from src.receiver import SmsMessage
from src.services.refresh_token import fetch_refresh_token
from src.storages import Storage
from src.utils.async_requests import http_post

re_sms_bank = re.compile(
    r'^[A-za-z ]+Bs\. {0,5}(?<amount>(\d+\.){0,1}\d+,\d+) del '
    r'(?<phone_number>\d{4}-\d{7}) Ref: (?<number>\d+) en '
    r'fecha:{0,1} (?<date>\d{2}-\d{2}-\d{2}) hora: (?<hour>\d{2}:\d{2}).*$'
)


async def send_sms_data(
    message: SmsMessage,
    storage: Storage | None = None,
    refresh_token: str | None = None
):
    assert storage is not None or refresh_token is not None
    match_sms = re_sms_bank.match(message.body)

    if match_sms:
        named_group = match_sms.groupdict()
        phone_number = named_group.get("phoneNumber")
        amount = named_group.get("amount")
        date = named_group.get("date")
        hour = named_group.get("hour")
        number = named_group.get("number")

        try:
            token = await fetch_refresh_token(
                refresh_token=refresh_token,
                storage=storage,
            )
        except ApiError as error:
            print(error)

        response = await http_post(
            urljoin(HOST, "/api/v1/deposits/mobile_payment/from_sms/"),
            headers=token.get_headers(),
            json={
                'address': message.address,
                'timestamp': message.date,
                'datetime': f"{date} {hour}",
                'amount': amount,
                'phone_number': phone_number,
                'number': number[-10:],
                'subject': message.subject,
                'serviceCenterAddress': message.service_center_address,
            },
        )
        data = response.json()

        if response.status_code in {200, 201, 400, 401}:
            return data

        raise ApiError(response.status_code, data)

    else:
        print("No match found for message")
