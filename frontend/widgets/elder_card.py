from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty

class ElderCard(BoxLayout):
    avatar_source = StringProperty('')
    elder_name = StringProperty('')
    elder_id = StringProperty('')
    root_screen = ObjectProperty(None)