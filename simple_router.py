# coding=utf-8
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition

from utils.router import AppRouter, Router, route

Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'

        Label:
            text: "You are now connected"
            font_size: 32

        Button:
            text: "Disconnect"
            font_size: 24
            on_press: app.route = "/login"

<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"

        Button:
            text: "Back"
            on_release: app.history_back()
            size_hint_y: None
            height: "48dp"

        Label:
            text: "Settings"

<LoginScreen>:
    BoxLayout:
        id: login_layout
        orientation: 'vertical'
        padding: [10,50,10,50]
        spacing: 50

        Label:
            text: 'Welcome'
            font_size: 32

        BoxLayout:
            orientation: 'vertical'

            Label:
                text: 'Login'
                font_size: 18
                halign: 'left'
                text_size: root.width-20, 20

            TextInput:
                id: login
                multiline:False
                font_size: 28

        BoxLayout:
            orientation: 'vertical'

            Label:
                text: 'Password'
                halign: 'left'
                font_size: 18
                text_size: root.width-20, 20

            TextInput:
                id: password
                multiline:False
                password:True
                font_size: 28

        Button:
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
    pass


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


class SimpleApp(AppRouter):
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
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


if __name__ == "__main__":
    SimpleApp().run()
