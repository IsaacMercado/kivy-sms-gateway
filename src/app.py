from aiohttp.client_exceptions import ClientConnectorError
from src.models.error import ApiError
import asyncio
import os

from aiohttp import ClientSession
from kivy import platform
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.utils import asynckivy as ak

from src.services.login import fetch_token
from src.utils.router import MixinAppRouter, Router, route

if platform == 'android':
    from android.permissions import Permission, request_permissions

    from src.services.register import start_service, stop_service

    SERVER_NAME = 'Myservice'


Builder.load_string("""
<MenuScreen>:
    MDBoxLayout:
        orientation: 'vertical'

        MDLabel:
            text: "You are now connected"
            font_size: 32

        MDRectangleFlatButton:
            text: "Hello world"
            font_size: 24
            on_press: root.callback(self)

        MDRectangleFlatButton:
            text: "Disconnect"
            font_size: 24
            on_press: app.route = "/login"

<SettingsScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDRectangleFlatButton:
            text: "Back"
            on_release: app.history_back()
            size_hint_y: None
            height: "48dp"

        MDLabel:
            text: "Settings"

<LoginScreen>:
    MDBoxLayout:
        id: login_layout
        orientation: 'vertical'
        padding: [10, 50, 10, 50]
        spacing: 50

        MDLabel:
            text: 'SIAC SMS Gateway'
            font_size: 32

        MDBoxLayout:
            orientation: 'vertical'

            MDLabel:
                text: 'Email'
                font_size: 18
                halign: 'left'
                text_size: root.width-20, 20

            MDTextField:
                id: login
                mode: "fill"
                multiline: False
                font_size: 28

        MDBoxLayout:
            orientation: 'vertical'

            MDLabel:
                text: 'Contraseña'
                halign: 'left'
                font_size: 18
                text_size: root.width-20, 20

            MDTextField:
                id: password
                mode: "fill"
                multiline: False
                password: True
                font_size: 28

        MDRectangleFlatButton:
            text: 'Connexion'
            font_size: 24
            on_press: root.do_login(login.text, password.text)

""")


def set_route(route: str):
    App.get_running_app().route = route


def back_route():
    App.get_running_app().history_back()


class LoginScreen(Screen):
    dialog = None

    def do_login(self, login_text, password_text):
        asyncio.ensure_future(self._do_login(login_text, password_text))

    async def _do_login(self, login_text, password_text):
        try:
            async with ClientSession() as session:
                token = await fetch_token(session, login_text, password_text)

            set_route("/")

        except ApiError as error:
            if error.non_field:
                self.show_alert_dialog("\n".join(error.non_field))

            input_maps = {
                "email": self.ids.login,
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

        except ClientConnectorError as error:
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


class MenuScreen(Screen):
    def callback(self, instance):
        print('The button is being pressed!')

        if platform == 'android':
            stop_service(SERVER_NAME)


class SettingsScreen(Screen):
    pass


class MainRouter(Router):
    @route("/")
    def index(self):
        return MenuScreen()

    @route("/login")
    def about(self):
        return LoginScreen()

    @route("/settings")
    def settings(self):
        return SettingsScreen()


class MyApp(MixinAppRouter, MDApp):
    storage = ObjectProperty()

    def build(self):
        if platform == 'android':
            request_permissions([
                Permission.RECEIVE_SMS,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
                Permission.FOREGROUND_SERVICE,
            ])
            start_service(SERVER_NAME)

        self.root = MainRouter()
        self.route = "/login"


if __name__ == '__main__':
    MyApp().run()
