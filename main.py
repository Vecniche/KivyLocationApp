import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from pymongo import MongoClient
from kivy.utils import platform
import geocoder
import re
if platform == 'android':
    import os
    os.environ['APP_ANDROID_MIN_API'] = '21'


class MapScreen(BoxLayout):
    name_input = ObjectProperty()
    category_input = ObjectProperty()
    coordinate_input = ObjectProperty()
    popup = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lat = None
        self.lon = None
        self.client = MongoClient('mongodb+srv://onwukaobinna001:Obinna1993@cluster0.3k4emni.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client['locations']
        self.collection = self.db['coordinates']


    def get_location(self, instance):
        try:
            g = geocoder.ip('me')
            if g.latlng is None:
                raise Exception("Unable to get location")
            self.lat = g.latlng[0]
            self.lon = g.latlng[1]
        except:
            popup = Popup(title='Error', content=Label(text='Unable to get location. Please check your internet '
                                                            'connection and try again'), size_hint=(None, None),
                          size=(200, 100))
            popup.open()
            return

        if self.lat and self.lon:
            lat, lon = self.lat, self.lon
            self.popup = Popup(title='Coordinates', size_hint=(None, None), size=(400, 200))
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text='Latitude: {}'.format(lat)))
            content.add_widget(Label(text='Longitude: {}'.format(lon)))
            self.name_input = TextInput(multiline=False, hint_text='Enter Name', size_hint=(1, 2))
            self.category_input = TextInput(multiline=False, hint_text='Enter Category', size_hint=(1, 2))
            self.coordinate_input = TextInput(multiline=False, hint_text='Enter Coordinate', size_hint=(1, 2))
            save_button = Button(text='Save', size_hint=(1, 2), font_size=15, background_color=(0, 0.25, 0, 1),
                                 on_press=self.save_location, bold=True, font_name='Roboto-Bold.ttf')
            content.add_widget(self.name_input)
            content.add_widget(self.category_input)
            content.add_widget(self.coordinate_input)
            content.add_widget(save_button)
            self.popup.content = content
            self.popup.open()
        else:
            popup = Popup(title='Error', content=Label(text='Unable to get location'), size_hint=(None, None),
                          size=(200, 100))
            popup.open()

    def save_location(self, instance):
        name = self.name_input.text.strip()
        category = self.category_input.text.strip()
        coordinate = self.coordinate_input.text.strip()
        lat, lon = self.lat, self.lon

        if not name or not category or not coordinate:
            popup = Popup(title='Error', content=Label(text='Please fill all the fields'), size_hint=(None, None),
                          size=(200, 100))
            popup.open()
            return

        if not re.match(r'^\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)$', coordinate):
            popup = Popup(title='Error', content=Label(text='Invalid coordinate format'), size_hint=(None, None),
                          size=(200, 100))
            popup.open()
            return

        try:
            lat, lon = map(float, coordinate[1:-1].split(','))
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError
        except ValueError:
            popup = Popup(title='Error', content=Label(text='Invalid latitude/longitude values'),
                          size_hint=(None, None), size=(200, 100))
            popup.open()
            return

        data = {
            'name': name,
            'category': category,
            'coordinate': coordinate,
            'lat': lat,
            'lon': lon
        }
        self.collection.insert_one(data)
        self.popup.dismiss()


class MapApp(App):
    def build(self):
        self.icon = "App 256.png"
        screen = MapScreen()
        button = Button(text="Click to get this Location Coordinate", on_press=screen.get_location,
                        background_color= (0, 0.25, 0, 1), bold= True, font_size= 20, font_name= 'Roboto-Bold.ttf')
        screen.add_widget(button)
        return screen

if __name__ == '__main__':
    MapApp().run()