from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from plyer import gps
from kivy.utils import platform
import requests

# Main App API URL
API_URL = 'http://localhost:5000/api/'

class MainApp(App):

    def build(self):
        self.title = 'Main App'
        self.root = RootWidget()
        return self.root

class RootWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [10, 50, 10, 10]

        self.find_button = Button(text='Find Nearest', on_press=self.find_nearest)
        self.result_label = Label(text='', size_hint_y=None, height=100)

        self.add_widget(self.find_button)
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

    def find_nearest(self, instance):
        if not self.gps_location:
            self.show_popup('Error', 'GPS location not available.')
            return

        latitude = self.gps_location['lat']
        longitude = self.gps_location['lon']

        data = {'latitude': latitude, 'longitude': longitude}
        response = requests.get(API_URL + 'find_nearest', params=data)

        if response.status_code == 200:
            nearest_phone = response.json()
            self.result_label.text = f"Nearest Phone Number:\n{nearest_phone['number']}\nDistance: {nearest_phone['distance']:.2f} meters"
        else:
            self.show_popup('Error', 'Failed to find nearest phone number.')

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
    MainApp().run()