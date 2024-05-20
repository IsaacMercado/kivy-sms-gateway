from datetime import datetime
from threading import Thread

from kivy import platform
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.properties import (BooleanProperty, ListProperty, ObjectProperty,
                             StringProperty)
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineIconListItem
from requests.exceptions import ConnectionError

from src.models.error import ApiError
from src.models.token import Token
from src.services.login import fetch_token
from src.storages.core import CoreStorage
from src.utils.logger import DATE_FORMAT, LogObserver
from src.utils.router import MixinAppRouter, Router, route

SERVER_NAME = 'Myservice'

if platform == 'android':
    from android.permissions import Permission, request_permissions

    from src.services.register import start_service, stop_service

Builder.load_string("""
<LogListItem>:
    IconLeftWidget:
        icon: root.icon

<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: "50dp"
        
        MDBoxLayout:
            orientation: 'vertical'

            MDLabel:
                id: welcome_label
                text: "SIAC SMS Gateway"
                font_size: 72
                haling: 'center'
                size_hint_y: None
                height: self.texture_size[1]
                padinng_y: 25
                
        MDBoxLayout:
            # md_bg_color: 'red'
            orientation: 'vertical'
        
            MDTextField:
                id: email
                hint_text: 'email'
                icon_right: 'account'

            MDTextField:
                id: password
                hint_text: 'password'
                icon_right: 'eye-off'
                password: True

            Widget:
                size_hint_y: None
                height: 20

            MDRoundFlatButton:
                text: 'LOG IN'
                pos_hint: {'center_x': 0.5}
                on_press: root.do_login(email.text, password.text)

        Widget:

<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: "50dp"

        MDLabel:
            text: "You are now connected"
            adaptive_size: True
            color: "grey"
            bold: True
            pos_hint: {'center_x': 0.5}

        MDRecycleView:
            viewclass: 'LogListItem'
            data: root.data

            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                    
        BoxLayout:
            size_hint_y: None

            MDRoundFlatButton:
                text: "Clear"
                pos_hint: {'center_x': 0.5}
                on_press: root.clear()

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
        thread = Thread(
            target=fetch_token,
            args=(
                login_text,
                password_text,
                self.on_success_login,
                self.on_error_login,
            )
        )
        thread.start()

    @mainthread
    def on_success_login(self, token: Token):
        token.to_storage(App.get_running_app().storage)
        set_route("/")

        # except ConnectionError as error:
        #     self.show_alert_dialog("No hay conexión a internet")

    @mainthread
    def on_error_login(self, error: ApiError):
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


class LogListItem(TwoLineIconListItem):
    icon = StringProperty('information')


LOG_ICONS = {
    "DEBUG": "bug",
    "INFO": "information",
    "WARNING": "alert",
    "ERROR": "close",
    "CRITICAL": "exclamation",
    "LOG": "file-document",
}


class MainScreen(Screen):
    data = ListProperty([])
    is_running = BooleanProperty(False)
    logs: LogObserver | None = ObjectProperty()

    def init_logs(self):
        if self.logs:
            self.logs.stop()
        self.logs = LogObserver(self.on_logs_added)
        self.logs.start()

    def on_pre_enter(self, *args):
        self.init_logs()

    def on_logs_added(self, logs):
        self.data.extend([
            {
                "text": message,
                "secondary_text": datetime.strptime(asctime, DATE_FORMAT).ctime(),
                "icon": LOG_ICONS.get(levelname, 'information'),
            } for asctime, name, levelname, message in map(
                lambda log: log.split(' - ', 3),
                logs
            )
        ])

    def on_enter(self, *args):
        if platform == 'android':
            from src.services.register import is_service_running

            def check_servive_running(dt):
                self.is_running = is_service_running(SERVER_NAME)

            Clock.schedule_interval(check_servive_running, 1.0)

    def on_leave(self, *args):
        self.logs.stop()
        if platform == 'android':
            self.is_running = False

    def logout(self):
        storage = App.get_running_app().storage
        storage.clear()
        set_route("/login")

    def clear(self):
        self.data.clear()
        self.logs.clear()
        self.init_logs()


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
