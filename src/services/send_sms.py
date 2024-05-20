import re
from typing import Callable
from urllib.parse import urljoin

import requests

from src.constants import HOST
from src.models.error import ApiError
from src.receiver import SmsMessage
from src.services.refresh_token import fetch_refresh_token
from src.storages import Storage
from src.utils.logger import logger
from src.models.token import Token

re_sms_bank = re.compile(
    r'^[A-za-z ]+Bs\. {0,5}(?P<amount>(\d+\.){0,1}\d+,\d+) del '
    r'(?P<phone_number>\d{4}-\d{7}) Ref: (?P<number>\d+) en '
    r'fecha:{0,1} (?P<date>\d{2}-\d{2}-\d{2}) hora: (?P<hour>\d{2}:\d{2}).*$'
)


def send_sms_data(
    message: SmsMessage,
    on_success: Callable[[dict], None],
    on_error: Callable[[ApiError], None],
    storage: Storage | None = None,
    refresh_token: str | None = None
):
    assert storage is not None or refresh_token is not None
    match_sms = re_sms_bank.match(message.body)

    if match_sms:
        phone_number = match_sms.group("phone_number")
        amount = match_sms.group("amount")
        date = match_sms.group("date")
        hour = match_sms.group("hour")
        number = match_sms.group("number")

        def _on_success(token: Token):
            response = requests.post(
                urljoin(HOST, "/api/v1/deposits/mobile_payment/from_sms/"),
                headers=token.get_headers(),
                json={
                    'address': message.address,
                    'timestamp': int(message.timestamp),
                    'datetime': f"{date} {hour}",
                    'amount': amount,
                    'phone_number': phone_number,
                    'number': number[-10:],
                    'subject': message.subject or None,
                    'serviceCenterAddress': message.service_center_address,
                },
            )
            data = response.json()

            if response.status_code in {200, 201, 400, 401}:
                logger.info(
                    "SMS data sent. Status code: %s",
                    response.status_code,
                )
                on_success(data)
                return

            logger.error("Error sending SMS data")
            exception = ApiError(response.status_code, data)
            on_error(exception)

        fetch_refresh_token(
            on_success=_on_success,
            on_error=on_error,
            refresh_token=refresh_token,
            storage=storage,
        )

    else:
        logger.warning("No match found for message")
