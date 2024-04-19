import asyncio

from kivy import platform
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.utils import asynckivy as ak
from requests.exceptions import ConnectionError

from src.models.error import ApiError
from src.models.token import Token
from src.services.login import fetch_token
from src.storages.core import CoreStorage
from src.utils.router import MixinAppRouter, Router, route

SERVER_NAME = 'Myservice'

if platform == 'android':
    from android.permissions import Permission, request_permissions

    from src.services.register import start_service, stop_service


Builder.load_string("""
<LoginScreen>:
    MDCard:
        size_hint: None, None
        size: 650, 900
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 10
        padding: dp(10)
        spacing: dp(10)
        orientation: 'vertical'

        MDLabel:
            id: welcome_label
            text: "SIAC SMS Gateway"
            font_size: 70
            haling: 'center'
            size_hint_y: None
            height: self.texture_size[1]
            padinng_y: 25

        MDTextField:
            id: email
            hint_text: 'email'
            icon_right: 'account'
            size_hint_x: None
            width: 450
            pos_hint: {'center_x': 0.5}

        MDTextField:
            id: password
            hint_text: 'password'
            icon_right: 'eye-off'
            size_hint_x: None
            width: 450
            pos_hint: {'center_x': 0.5}
            password: True

        Widget:
            size_hint_y: None
            height: 20

        MDRoundFlatButton:
            text: 'LOG IN'
            pos_hint: {'center_x': 0.5}
            on_press: root.do_login(email.text, password.text)

        Widget:
            size_hint_y: None
            height: 20

<MainScreen>:
    MDCard:
        size_hint: None, None
        size: 650, 900
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 10
        padding: dp(10)
        spacing: dp(10)
        orientation: 'vertical'

        MDLabel:
            text: "You are now connected"
            adaptive_size: True
            color: "grey"
            pos: "12dp", "12dp"
            bold: True
            pos_hint: {'center_x': 0.5}

        MDRoundFlatButton:
            text: "Logout"
            pos_hint: {'center_x': 0.5}
            on_press: root.logout()

""")


def set_route(route: str):
    App.get_running_app().route = route


def back_route():
    App.get_running_app().history_back()


class LoginScreen(Screen):
    dialog = None

    def do_login(self, login_text, password_text):
        print(login_text, password_text)
        asyncio.ensure_future(self._do_login(login_text, password_text))

    async def _do_login(self, login_text, password_text):
        try:
            token = await fetch_token(login_text, password_text)
            token.to_storage(App.get_running_app().storage)
            set_route("/")
        except ApiError as error:
            if error.non_field:
                self.show_alert_dialog("\n".join(error.non_field))

            input_maps = {
                "email": self.ids.email,
                "password": self.ids.password,
            }

            for key, widget in input_maps.items():
                value = error.fields.get(key)

                if value:
                    widget.helper_text_mode = "on_error"
                    widget.helper_text = "\n".join(value)
                    widget.error = True
                else:
                    widget.helper_text_mode = "on_focus"
                    widget.helper_text = ""
                    widget.error = False

        except ConnectionError as error:
            self.show_alert_dialog("No hay conexión a internet")

    def show_alert_dialog(self, content):
        if not self.dialog:
            self.dialog = MDDialog(
                buttons=[
                    MDFlatButton(
                        text="CERRAR",
                        on_release=self.close_alert_dialog
                    ),
                ],
            )
        self.dialog.text = content
        self.dialog.open()

    def close_alert_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()


class MainScreen(Screen):
    def callback(self, instance):
        print('The button is being pressed!')

        if platform == 'android':
            # stop_service(SERVER_NAME)
            from src.utils.android.notification import show_notification
            show_notification()

    def logout(self):
        storage = App.get_running_app().storage
        storage.clear()
        set_route("/login")


class MainRouter(Router):
    @route("/")
    def index(self):
        return MainScreen()

    @route("/login")
    def about(self):
        return LoginScreen()


class SMSGatewayApp(MixinAppRouter, MDApp):
    storage = ObjectProperty()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.storage = CoreStorage()

        if platform == 'android':
            request_permissions([
                Permission.RECEIVE_SMS,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
                Permission.FOREGROUND_SERVICE,
                Permission.POST_NOTIFICATIONS,
            ])
            start_service(SERVER_NAME)

        self.root = MainRouter()
        self.route = "/" if Token.has_token(self.storage) else "/login"
