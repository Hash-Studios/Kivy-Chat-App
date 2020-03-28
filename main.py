import os
import sys

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.card import MDSeparator
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.navigationdrawer import MDNavigationDrawer, NavigationLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDToolbar

import client

Window.softinput_mode = 'pan'
class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        self.chat_history = MDLabel(
            size_hint_y=None, markup=True, font_style=theme_font_styles[6], theme_text_color="Primary")
        self.scroll_to_point = MDLabel()

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    def update_chat_history(self, message):
        self.chat_history.text += '\n' + message

        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width*0.98, None)

        self.scroll_to(self.scroll_to_point)

    def update_chat_history_layout(self, _=None):
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)


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
            prev_ip = "192.168.1.9"
            prev_port = "1234"
            prev_username = ""
        self.add_widget(MDLabel())
        self.add_widget(MDLabel())
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
        Clock.schedule_once(self.connect, 0.5)

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
        self.rows = 3
        self.padding = 5

        self.add_widget(MDLabel())
        self.history = ScrollableLabel(
            height=Window.size[1]*0.788, size_hint_y=None)
        self.add_widget(self.history)

        self.new_msg = MDTextField(
            size_hint_x=None, multiline=False, pos_hint={'center_x':0,'center_y':1})
        bottom_line = GridLayout(cols=1)
        bottom_line.add_widget(self.new_msg)
        self.add_widget(bottom_line)

        Window.bind(on_key_down=self.on_key_down)

        Clock.schedule_once(self.focus_text_input, 3)
        client.start_listening(self.incoming_message, show_error)
        self.bind(size=self.adjust_fields)

    def adjust_fields(self, *_):
        if Window.size[1] * 0.1 < 70:
            new_height = Window.size[1] - 135
        else:
            new_height = Window.size[1] * 0.81
        self.history.height = new_height
        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 70
        else:
            new_width = Window.size[0] * 0.91
        self.new_msg.width = new_width
        Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:
            self.send_message(None)

    def send_message(self, _):
        msg = self.new_msg.text
        self.new_msg.text = ''
        if msg:
            self.history.update_chat_history(
                f"[color=dd2020]{chat_app.connect_page.username.text}[/color] [color=20dddd]>:[/color] {msg}")
            client.send(msg)

    def focus_text_input(self, _):
        self.new_msg.focus = True

    def incoming_message(self, username, message):
        self.history.update_chat_history(
            f"[color=20dd20]{username}[/color] [color=20dddd]>:[/color] {message}")


class SuperChatApp(MDApp):
    def build(self):
        app = MDApp.get_running_app()
        app.theme_cls = ThemeManager()
        app.theme_cls.primary_palette = "DeepPurple"
        app.theme_cls.accent_palette = "DeepPurple"
        app.theme_cls.theme_style = "Light"
        Window.borderless = False
        self.title = "Super Chat"
        Config.set('kivy', 'window_title', 'Super Chat')

        self.root_sm = ScreenManager()
        rscreen = Screen(name="Root")

        self.nav_layout = NavigationLayout()
        self.nl_sm = ScreenManager()
        nl_screen = Screen(name="nl")
        self.toolbar = MDToolbar(pos_hint={'top': 1},
                                 elevation=9, title=chat_app.title, md_bg_color=chat_app.theme_cls.primary_color)
        self.toolbar.left_action_items = [
            ["menu", lambda x: self.nav_drawer.toggle_nav_drawer()]]
        nl_screen.add_widget(self.toolbar)
        self.screen_manager = ScreenManager()

        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)
        nl_screen.add_widget(self.screen_manager)
        self.nl_sm.add_widget(nl_screen)

        self.nav_drawer = MDNavigationDrawer(elevation=0)

        self.ndbox = BoxLayout(orientation="vertical", spacing="8dp")

        self.avatar = Image(id="avatar", size_hint=(None, None), size=(
            Window.size[0]*0.65, Window.size[0]*0.55), source="icon.png")
        self.anchor = AnchorLayout(
            anchor_x="center", size_hint_y=None, height=self.avatar.height*1.3)
        self.anchor.add_widget(MDLabel())
        self.anchor.add_widget(self.avatar)
        self.ndbox.add_widget(self.anchor)

        self.fl = FloatLayout()
        self.fl.padding = 8
        self.sub_nav = OneLineAvatarIconListItem(text="Settings", theme_text_color="Primary", pos_hint={
                                                 'center_x': 0.5, 'center_y': 1}, font_style="Button")
        self.iconitem = IconLeftWidget(icon="settings", pos_hint={
                                       'center_x': 1, 'center_y': 0.55})
        self.sub_nav.add_widget(self.iconitem)
        self.fl.add_widget(self.sub_nav)
        self.settings_btn = OneLineAvatarIconListItem(
            text="Dark Mode", on_press=self.theme_change,on_release=lambda x: self.nav_drawer.toggle_nav_drawer(), pos_hint={'center_x': 0.5, 'center_y': 0.86})
        self.iconitem = IconLeftWidget(
            icon="theme-light-dark", pos_hint={'center_x': 1, 'center_y': 0.55})
        self.settings_btn.add_widget(self.iconitem)
        self.fl.add_widget(self.settings_btn)
        self.ndbox.add_widget(self.fl)
        self.toolbar = MDToolbar(
            elevation=8, title=chat_app.title, md_bg_color=chat_app.theme_cls.primary_color)
        self.toolbar.left_action_items = [
            ["close", sys.exit]]
        self.ndbox.add_widget(self.toolbar)
        self.nav_drawer.add_widget(self.ndbox)
        self.nav_layout.add_widget(self.nl_sm)
        self.nav_layout.add_widget(self.nav_drawer)

        rscreen.add_widget(self.nav_layout)
        self.root_sm.add_widget(rscreen)

        return self.root_sm

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
    
    def on_start(self):
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
    
    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            if chat_app.screen_manager.current!="Connect":
                chat_app.screen_manager.current = "Connect"
            return True


def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 3)


if __name__ == "__main__":
    chat_app = SuperChatApp()
    chat_app.run()
