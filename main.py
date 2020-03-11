import kivy
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.textfields import MDTextField
from kivymd.theming import ThemeManager
from kivymd.toolbar import MDToolbar
from kivymd.label import MDLabel
from kivymd.button import MDFloatingActionButton
from kivy.uix.floatlayout import FloatLayout
from kivymd.font_definitions import theme_font_styles
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationLayout
from kivymd.cards import MDSeparator

kivy.require("2.0.0")


class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.padding = 10

        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]
        else:
            prev_ip = ""
            prev_port = ""
            prev_username = ""

        self.add_widget(MDLabel(text="IP : ", halign="center",
                                theme_text_color="Primary"))
        self.float = FloatLayout()
        self.ip = MDTextField(text=prev_ip, multiline=False,
                              pos_hint={'x': 0, 'y': 0.2})
        self.float.add_widget(self.ip)
        self.add_widget(self.float)

        self.add_widget(MDLabel(text="Port : ", halign="center",
                                theme_text_color="Primary"))
        self.float = FloatLayout()
        self.port = MDTextField(
            text=prev_port, multiline=False, pos_hint={'x': 0, 'y': 0.2})
        self.float.add_widget(self.port)
        self.add_widget(self.float)

        self.add_widget(MDLabel(text="Username : ",
                                halign="center", theme_text_color="Primary"))
        self.float = FloatLayout()
        self.username = MDTextField(
            text=prev_username, multiline=False, pos_hint={'x': 0, 'y': 0.2})
        self.float.add_widget(self.username)
        self.add_widget(self.float)

        self.float_layout = FloatLayout()
        self.connect = MDFloatingActionButton(
            icon="arrow-right", pos_hint={'x': 0.68, 'y': 0})
        self.connect.bind(on_release=self.connect_button)
        self.float_layout.add_widget(self.connect)
        self.add_widget(MDLabel())
        self.add_widget(MDLabel())
        self.add_widget(MDLabel())
        self.add_widget(MDLabel())
        self.add_widget(MDLabel())
        self.add_widget(self.float_layout)

    def connect_button(self, instance):
        ip = self.ip.text
        port = self.port.text
        username = self.username.text

        info = f"Attempting to join {ip}:{port} as {username}"
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = "Info"
        #chat_app.theme_cls.theme_style = "Light"

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")


class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1

        self.message = MDLabel(halign="center", valign="middle",
                               font_style=theme_font_styles[7], theme_text_color="Primary")
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)

    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width*0.9, None)


class SuperChatApp(App):
    def build(self):
        app = App.get_running_app()
        app.theme_cls = ThemeManager()
        app.theme_cls.primary_palette = "DeepPurple"
        app.theme_cls.accent_palette = "DeepPurple"
        app.theme_cls.theme_style = "Light"
        Window.size = (360, 640)
        Window.borderless = False
        self.title = "Super Chat"
        Config.set('kivy', 'window_title', 'Hello')

        self.nav_layout = NavigationLayout()
        self.nav_drawer = MDNavigationDrawer()
        self.toolbar = MDToolbar(
            elevation=10, title=chat_app.title, md_bg_color=chat_app.theme_cls.primary_color)
        self.toolbar.left_action_items = [
            ["close", lambda x: chat_app.root.toggle_nav_drawer()]]
        self.nav_drawer.add_widget(self.toolbar)
        self.nav_layout.add_widget(self.nav_drawer)

        self.box_layout = BoxLayout(orientation="vertical")

        self.toolbar = MDToolbar(
            elevation=10, title=chat_app.title, md_bg_color=chat_app.theme_cls.primary_color)
        self.toolbar.left_action_items = [
            ["menu", lambda x: chat_app.root.toggle_nav_drawer()]]
        self.box_layout.add_widget(self.toolbar)

        self.screen_manager = ScreenManager()

        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        self.box_layout.add_widget(self.screen_manager)

        self.nav_layout.add_widget(self.box_layout)

        return self.nav_layout


if __name__ == "__main__":
    chat_app = SuperChatApp()
    chat_app.run()
