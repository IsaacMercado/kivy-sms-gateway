from android.broadcast import BroadcastReceiver
from jnius import autoclass

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
SmsIntents = autoclass("android.provider.Telephony$Sms$Intents")


class ImcomingSmsReceiver(BroadcastReceiver):
    def __init__(self, callback):
        super().__init__(
            lambda context, intent: callback(self.on_receive(context, intent)),  # noqa
            actions=[SmsIntents.SMS_RECEIVED_ACTION]
        )

    def on_receive(self, context, intent):
        return [
            {
                'display_message_body': message.getDisplayMessageBody(),
                'display_originating_address': message.getDisplayOriginatingAddress(),
                'email_body': message.getEmailBody(),
                'email_from': message.getEmailFrom(),
                'index_on_icc': message.getIndexOnIcc(),
                'message_body': message.getMessageBody(),
                'originating_address': message.getOriginatingAddress(),
                'protocol_identifier': message.getProtocolIdentifier(),
                'pseudo_subject': message.getPseudoSubject(),
                'service_center_address': message.getServiceCenterAddress(),
                'status': message.getStatus(),
                'status_on_icc': message.getStatusOnIcc(),
                'timestamp_millis': message.getTimestampMillis(),
                'is_email': message.isEmail(),
                'is_mwi_clear_message': message.isMWIClearMessage(),
                'is_mwi_set_message': message.isMWISetMessage(),
                'is_mwi_dont_store': message.isMwiDontStore(),
                'is_replace': message.isReplace(),
                'is_reply_path_present': message.isReplyPathPresent(),
                'is_status_report_message': message.isStatusReportMessage()
            } for message in SmsIntents.getMessagesFromIntent(intent)
        ]
