from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.lang import Builder

# Using a KV string is more robust as it avoids external file issues
Builder.load_string('''
<MedicineCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: '10dp'
    spacing: '5dp'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]

    BoxLayout:
        size_hint_y: None
        height: '35dp'
        Label:
            text: root.name
            font_name: "THFont"
            font_size: '18sp'
            bold: True
            color: (0,0,0,1)
            halign: 'left'
            text_size: self.width, None
        Label:
            text: "กินแล้ว" if root.is_taken_today else "ยังไม่กิน"
            font_name: "THFont"
            color: (0.2, 0.8, 0.2, 1) if root.is_taken_today else (1, 0.2, 0.2, 1)
            halign: 'right'
            size_hint_x: 0.4

    InfoRow:
        icon: 'assets/icon_time.png'
        text: f"เวลา: {root.time_to_take}"

    InfoRow:
        icon: 'assets/icon_dosage.png'
        text: f"ปริมาณ: {root.dosage}"

    InfoRow:
        icon: 'assets/icon_meal.png'
        text: f"มื้ออาหาร: {root.meal_instruction}"

<InfoRow@BoxLayout>:
    icon: ''
    text: ''
    orientation: 'horizontal'
    size_hint_y: None
    height: '24dp'
    spacing: 4
    Image:
        source: root.icon
        size_hint_x: None
        width: '24dp'
    Label:
        text: root.text
        font_name: "THFont"
        font_size: "14sp"
        color: (0.2,0.2,0.2,1)
        halign: 'left'
        text_size: self.width, None

''')

class MedicineCard(BoxLayout):
    med_id = NumericProperty(0)
    name = StringProperty('')
    time_to_take = StringProperty('')
    dosage = StringProperty('')
    meal_instruction = StringProperty('')
    is_taken_today = BooleanProperty(False)

    def __init__(self, med_data, **kwargs):
        super().__init__(**kwargs)
        self.med_id = med_data.get('id', 0)
        self.name = med_data.get('name', 'N/A')
        self.time_to_take = med_data.get('time_to_take', '-')
        self.dosage = med_data.get('dosage', '-')
        self.meal_instruction = med_data.get('meal_instruction', '-')
        self.is_taken_today = med_data.get('is_taken_today', False)
