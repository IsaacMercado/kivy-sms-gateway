import os

from kivy import platform
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextFieldRect

from src.utils.router import Router, route, MixinAppRouter

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
            on_press: self.callback()

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
        padding: [10,50,10,50]
        spacing: 50

        MDLabel:
            text: 'Welcome'
            font_size: 32

        MDBoxLayout:
            orientation: 'vertical'

            MDLabel:
                text: 'Login'
                font_size: 18
                halign: 'left'
                text_size: root.width-20, 20

            MDTextFieldRect:
                id: login
                multiline:False
                font_size: 28

        MDBoxLayout:
            orientation: 'vertical'

            MDLabel:
                text: 'Password'
                halign: 'left'
                font_size: 18
                text_size: root.width-20, 20

            MDTextFieldRect:
                id: password
                multiline:False
                password:True
                font_size: 28

        MDRectangleFlatButton:
            text: 'Connexion'
            font_size: 24
            on_press: root.do_login(login.text, password.text)
""")


class LoginScreen(Screen):
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        app.config.read(app.get_application_config())
        app.config.write()

        app.route = "/"


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


from kivymd.app import MDApp


class MyApp(MixinAppRouter, MDApp):
    username = StringProperty(None)
    password = StringProperty(None)

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

    def get_application_config(self):
        if not self.username:
            return super().get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if not os.path.exists(conf_directory):
            os.makedirs(conf_directory)

        return super().get_application_config(
            '%s/config.cfg' % (conf_directory)
        )


if __name__ == '__main__':
    MyApp().run()
