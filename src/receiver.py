from datetime import datetime
from typing import Any, Callable

from android.broadcast import BroadcastReceiver
from jnius import autoclass

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
SmsIntents = autoclass("android.provider.Telephony$Sms$Intents")


class SmsMessage:
    def __init__(
        self,
        address: str,
        subject: str,
        body: str,
        timestamp: int,
        service_center_address: int | None = None
    ):
        self.address = address
        self.subject = subject
        self.body = body
        self.timestamp = timestamp
        self.service_center_address = service_center_address

    @property
    def date(self):
        if not hasattr(self, '_date'):
            self._date = datetime.fromtimestamp(self.timestamp / 1000)
        return self._date

    @classmethod
    def from_android_instance(cls, instance: Any):
        return cls(
            address=instance.getOriginatingAddress(),
            subject=instance.getPseudoSubject(),
            body=instance.getMessageBody(),
            timestamp=instance.getTimestampMillis(),
            service_center_address=instance.getServiceCenterAddress()
        )


class ImcomingSmsReceiver(BroadcastReceiver):
    def __init__(self, callback: Callable[[list[SmsMessage]], None]):
        super().__init__(
            lambda context, intent: callback(self.on_receive(context, intent)),  # noqa
            actions=[SmsIntents.SMS_RECEIVED_ACTION]
        )

    def on_receive(self, context, intent):
        return [
            SmsMessage.from_android_instance(message)
            for message in SmsIntents.getMessagesFromIntent(intent)
            if not message.isEmail()
        ]
