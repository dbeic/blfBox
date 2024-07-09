from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from plyer import gps
from kivy.utils import platform
import requests

# Main App API URL
API_URL = 'http://localhost:5000/api/'

class HelperApp(App):

    def build(self):
        self.title = 'Helper App'
        self.root = RootWidget()
        return self.root

class RootWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [10, 50, 10, 10]

        self.number_input = TextInput(hint_text='Enter Phone Number', multiline=False)
        self.name_input = TextInput(hint_text='Enter Name', multiline=False)
        self.register_button = Button(text='Register Phone Number', on_press=self.register_phone_number)
        self.result_label = Label(text='', size_hint_y=None, height=100)

        self.add_widget(Label(text='Phone Number:', size_hint_y=None, height=50))
        self.add_widget(self.number_input)
        self.add_widget(Label(text='Name:', size_hint_y=None, height=50))
        self.add_widget(self.name_input)
        self.add_widget(self.register_button)
        self.add_widget(self.result_label)

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION])
        
        gps.configure(on_location=self.on_location, on_status=self.on_status)
        gps.start()

        self.gps_location = None

    def on_location(self, **kwargs):
        self.gps_location = kwargs

    def on_status(self, stype, status):
        pass

    def register_phone_number(self, instance):
        number = self.number_input.text.strip()
        name = self.name_input.text.strip()

        if not number or not name:
            self.show_popup('Error', 'Please fill in all fields.')
            return

        if not self.gps_location:
            self.show_popup('Error', 'GPS location not available.')
            return

        latitude = self.gps_location['lat']
        longitude = self.gps_location['lon']

        data = {'number': number, 'name': name, 'latitude': latitude, 'longitude': longitude}
        response = requests.post(API_URL + 'register_phone_number', json=data)

        if response.status_code == 201:
            self.show_popup('Success', 'Phone number registered successfully.')
            self.result_label.text = 'Phone number registered successfully.'
        else:
            self.show_popup('Error', 'Failed to register phone number.')

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
    HelperApp().run()