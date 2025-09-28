# frontend/widgets/elder_medicine_item.py
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button

class ElderMedicineItem(BoxLayout):
    # --- *** แก้ไขชื่อ Properties ทั้งหมดที่นี่ *** ---
    med_id = NumericProperty(0)
    med_name = StringProperty('ชื่อยา')
    med_time = StringProperty('00:00')
    med_dosage = StringProperty('')
    med_meal = StringProperty('')
    
    # --- Properties ที่ใช้ภายใน (ไม่ต้องแก้) ---
    is_taken_today = BooleanProperty(False)
    on_confirm_callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(is_taken_today=self.on_status_change)
        Clock.schedule_once(lambda dt: self.on_status_change(self, self.is_taken_today))

    def on_status_change(self, instance, is_taken):
        """
        ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่ is_taken_today เปลี่ยนค่า
        และจะสร้าง UI ที่ถูกต้องขึ้นมาใหม่
        """
        if 'action_area' not in self.ids:
            return

        action_area = self.ids.action_area
        action_area.clear_widgets()

        if is_taken:
            # --- *** จุดที่แก้ไข *** ---
            # สร้าง Label "ทานแล้ววันนี้" พร้อมกับ pos_hint
            taken_label = Label(
                text='ทานแล้ววันนี้',
                font_name='THFont',
                font_size='16sp',
                color=(0.1, 0.5, 0.1, 1),
                bold=True,
                # --- เพิ่มบรรทัดนี้เข้าไป ---
                pos_hint={'center_x': .5, 'center_y': .5}
            )
            action_area.add_widget(taken_label)
        else:
            # สร้าง Button "ยืนยัน" (ส่วนนี้ถูกต้องอยู่แล้ว)
            confirm_button = Button(
                text='ยืนยันการทานยา',
                font_name='THFont',
                size_hint=(None, None),
                size=('180dp', '44dp'),
                pos_hint={'center_x': .5, 'center_y': .5},
            )
            confirm_button.bind(on_release=lambda x: self.confirm_medication())
            action_area.add_widget(confirm_button)


    def confirm_medication(self):
        self.is_taken_today = True
        if self.on_confirm_callback:
            self.on_confirm_callback(self.med_id)