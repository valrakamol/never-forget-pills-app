# frontend/screens/elder_appointment_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from api_client import ApiClient

class ElderAppointmentScreen(Screen):
    appointment_list_layout = ObjectProperty(None)
    
    def on_enter(self):
        self.load_my_appointments()
        
    def load_my_appointments(self):
        if not self.appointment_list_layout:
            return
        
        self.appointment_list_layout.clear_widgets()
        api = ApiClient()
        response = api.get('/appointments/my_appointments')

        if response and response.status_code == 200:
            appointments = response.json().get('appointments', [])
            if not appointments:
                no_app_label = Label(text="ไม่มีนัดหมายเร็วๆ นี้", font_name="THFont", color=(0,0,0,1))
                self.appointment_list_layout.add_widget(no_app_label)
            else:
                for app_data in appointments:
                    item = self.create_appointment_item(app_data)
                    self.appointment_list_layout.add_widget(item)
        else:
            error_label = Label(text="ไม่สามารถโหลดข้อมูลนัดหมายได้", font_name="THFont", color=(1,0,0,1))
            self.appointment_list_layout.add_widget(error_label)

    def create_appointment_item(self, app_data):
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding='12dp', spacing='8dp')
        container.bind(minimum_height=container.setter('height'))

        full_datetime = app_data.get('datetime', ' - ')
        date_part, time_part = full_datetime.split(' ') if ' ' in full_datetime else (full_datetime, '-')
        
        # --- *** จุดที่แก้ไข *** ---
        # 1. สร้าง Layout แนวนอนสำหรับแถวบนสุด (Header)
        header_layout = BoxLayout(size_hint_y=None, height='30dp')

        # 2. สร้าง Label ของ Title พร้อมกำหนดการจัดตำแหน่ง
        title_label = Label(
            text=f"[b]{app_data.get('title', 'N/A')}[/b]",
            font_name="THFont",
            font_size='22sp',
            color=(0,0,0,1),
            markup=True,
            halign='left',       # <--- จัดชิดซ้าย
            valign='middle'
        )
        # 3. บรรทัดนี้สำคัญมาก: ทำให้ halign ทำงานได้อย่างถูกต้อง
        title_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))

        # 4. เพิ่ม Title Label เข้าไปใน Header Layout
        header_layout.add_widget(title_label)
        container.add_widget(header_layout)
        # --- ******************** ---
        
        # เพิ่มข้อมูลย่อยๆ (เหมือนเดิม)
        container.add_widget(self.create_info_row('assets/icon_calendar.png', f"วันที่: {date_part}"))
        container.add_widget(self.create_info_row('assets/icon_time.png', f"เวลา: {time_part} น."))
        container.add_widget(self.create_info_row('assets/icon_hospital.png', f"สถานที่: {app_data.get('location', '-')}"))
        container.add_widget(self.create_info_row('assets/icon_doctor.png', f"แพทย์: {app_data.get('doctor', '-') if app_data.get('doctor') else 'ไม่ได้ระบุ'}"))

        return container

    def create_info_row(self, icon_source, text):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height='24dp', spacing=10)
        row.add_widget(Image(source=icon_source, size_hint_x=None, width='24dp'))
        label = Label(text=text, font_name="THFont", font_size="16sp", color=(0.2,0.2,0.2,1), halign='left')
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        row.add_widget(label)
        return row