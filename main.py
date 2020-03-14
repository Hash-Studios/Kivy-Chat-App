import kivy
import os
import sys
import client
from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivymd.textfields import MDTextField
from kivymd.theming import ThemeManager
from kivymd.toolbar import MDToolbar
from kivymd.label import MDLabel
from kivymd.button import MDFloatingActionButton
from kivy.uix.floatlayout import FloatLayout
from kivymd.font_definitions import theme_font_styles
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationLayout, NavigationDrawerToolbar, NavigationDrawerIconButton, NavigationDrawerSubheader
from kivymd.cards import MDSeparator

kivy.require("2.0.0")


class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        self.chat_history = MDLabel(size_hint_y=None, markup=True)
        self.scroll_to_point = MDLabel()

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    def update_chat_history(self, message):
        self.chat_history.text += '\n' + message
        
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width*0.98, None)

        self.scroll_to(self.scroll_to_point)

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
        self.connect_fab = MDFloatingActionButton(
            icon="arrow-right", pos_hint={'x': 0.68, 'y': 0})
        self.connect_fab.bind(on_release=self.connect_button)
        self.float_layout.add_widget(self.connect_fab)
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

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")

        info = f"Attempting to join {ip}:{port} as {username}"
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = "Info"
        Clock.schedule_once(self.connect, 1)

    def connect(self, _):
        ip = self.ip.text
        port = self.port.text
        port = int(port)
        username = self.username.text

        if not client.connect(ip, port, username, show_error):
            return
        chat_app.create_chat_page()
        chat_app.screen_manager.current = "Chat"


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


class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.rows = 2
        self.padding = 5
        # self.add_widget(MDLabel(text="Hey! It's working", halign="center", valign="middle",
        #                         font_style=theme_font_styles[7], theme_text_color="Primary"))
        self.history = MDLabel(height = Window.size[1]*0.788, size_hint_y=None)
        self.add_widget(self.history)

        self.new_msg = MDTextField(width=Window.size[0]*0.8, size_hint_x=None, multiline=False)
        self.send_fab = MDFloatingActionButton(
            icon="arrow-right", pos_hint={'x': 0.68, 'y': 0})
        self.send_fab.bind(on_release=self.send_message)
        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_msg)
        bottom_line.add_widget(self.send_fab)
        self.add_widget(bottom_line)

    def send_message(self, _):
        print(f"Sent {self.new_msg.text}")
        self.new_msg.text = ''

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
        self.nav_drawer = MDNavigationDrawer(
            drawer_logo=r"C:\Users\Asus\Desktop\Kivy-Chat-App\icon.png", spacing=8)

        self.toolbar = NavigationDrawerToolbar(
            elevation=8, title=chat_app.title, md_bg_color=chat_app.theme_cls.primary_color)
        self.toolbar.left_action_items = [
            ["close", lambda x: chat_app.root.toggle_nav_drawer()]]
        self.nav_drawer.add_widget(self.toolbar)
        self.sub_nav = NavigationDrawerSubheader(text="Settings")
        self.nav_drawer.add_widget(self.sub_nav)
        self.settings_btn = NavigationDrawerIconButton(
            text="Dark Mode", on_press=self.theme_change)
        self.nav_drawer.add_widget(self.settings_btn)
        self.nav_layout.add_widget(self.nav_drawer)

        self.box_layout = BoxLayout(orientation="vertical")

        self.toolbar = MDToolbar(
            elevation=9, title=chat_app.title, md_bg_color=chat_app.theme_cls.primary_color)
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

    def theme_change(self, instance):
        if chat_app.theme_cls.theme_style == "Dark":
            chat_app.theme_cls.theme_style = "Light"
        else:
            chat_app.theme_cls.theme_style = "Dark"

    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name="Chat")
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)


def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    chat_app = SuperChatApp()
    chat_app.run()
