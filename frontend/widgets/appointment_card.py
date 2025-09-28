# frontend/widgets/appointment_card.py
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty # <-- เพิ่ม NumericProperty

class AppointmentCard(BoxLayout):
    # --- *** เพิ่ม ID *** ---
    appointment_id = NumericProperty(0)
    
    title = StringProperty('')
    datetime = StringProperty('')
    location = StringProperty('')
    
    # --- *** เพิ่ม Callbacks *** ---
    on_confirm_callback = ObjectProperty(None)
    on_postpone_callback = ObjectProperty(None)