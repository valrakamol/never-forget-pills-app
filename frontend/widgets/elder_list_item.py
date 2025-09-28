# frontend/widgets/elder_list_item.py
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty

# สืบทอดจาก ButtonBehavior เพื่อทำให้ BoxLayout นี้สามารถกดได้เหมือนปุ่ม
class ElderListItem(ButtonBehavior, BoxLayout):
    # ID ของผู้สูงอายุ เพื่อใช้ในการอ้างอิงเมื่อถูกกด
    elder_id = NumericProperty(0)
    
    # ชื่อเต็มของผู้สูงอายุที่จะแสดงผล
    full_name = StringProperty('')

    # ไม่จำเป็นต้องมี __init__