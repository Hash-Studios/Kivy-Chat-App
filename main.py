import kivy
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

kivy.require("2.0.0")

class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2

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

        self.add_widget(Label(text="IP : "))
        self.ip = TextInput(text=prev_ip, multiline=False)
        self.add_widget(self.ip)

        self.add_widget(Label(text="Port : "))
        self.port = TextInput(text=prev_port, multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text="Username : "))
        self.username = TextInput(text=prev_username, multiline=False)
        self.add_widget(self.username)

        self.connect = Button(text="Connect")
        self.connect.bind(on_release=self.connect_button)
        self.add_widget(Label())
        self.add_widget(self.connect)
    
    def connect_button(self, instance):
        ip = self.ip.text
        port = self.port.text
        username = self.username.text

        print(f"Attempting to join {ip}:{port} as {username}")

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")

class SuperChatApp(App):
    def build(self):
        Window.size = (300,200)
        return ConnectPage()

if __name__ == "__main__":
    SuperChatApp().run()