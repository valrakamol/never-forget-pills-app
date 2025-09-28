# frontend/screens/appointment_list_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from api_client import ApiClient
from widgets.alert_box import AlertBox

class AppointmentListScreen(Screen):
    appointment_list_layout = ObjectProperty(None)

    def on_enter(self):
        self.load_appointments()

    def load_appointments(self):
        if not self.appointment_list_layout:
            return

        self.appointment_list_layout.clear_widgets()
        elder_id = self.manager.current_elder_id
        api = ApiClient()
        response = api.get(f'/appointments/elder/{elder_id}')

        if response and response.status_code == 200:
            appointments = response.json().get('appointments', [])
            if not appointments:
                self.appointment_list_layout.add_widget(Label(text="ยังไม่มีรายการหมอนัด", font_name="THFont", color=(0,0,0,1)))
            else:
                for app in appointments:
                    item = self.create_appointment_item(app)
                    self.appointment_list_layout.add_widget(item)
        else:
            self.appointment_list_layout.add_widget(Label(text="ไม่สามารถโหลดรายการหมอนัดได้", font_name="THFont", color=(1,0,0,1)))
            
    def create_appointment_item(self, app_data):
        # --- *** จุดที่แก้ไข 1: สร้าง UI ใหม่ทั้งหมด *** ---
        # ใช้ Layout แนวตั้งเป็นหลัก
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding='12dp', spacing='8dp')
        container.bind(minimum_height=container.setter('height'))

        # --- ส่วนข้อมูล (เหมือนของผู้สูงอายุ) ---
        full_datetime = app_data.get('datetime', ' - ')
        date_part, time_part = full_datetime.split(' ') if ' ' in full_datetime else (full_datetime, '-')
        
        header_layout = BoxLayout(size_hint_y=None, height='30dp')
        header_layout.add_widget(Label(
            text=f"[b]{app_data.get('title', 'N/A')}[/b]", 
            font_name="THFont", 
            font_size='18sp', 
            color=(0,0,0,1), 
            markup=True, 
            halign='left', 
            text_size=(None, None)
        ))
        header_layout.add_widget(Label(text="[color=ff4444]ยังไม่ไป[/color]", font_name="THFont", markup=True, halign='right'))
        container.add_widget(header_layout)
        
        container.add_widget(self.create_info_row('assets/icon_calendar.png', f"วันที่: {date_part}"))
        container.add_widget(self.create_info_row('assets/icon_time.png', f"เวลา: {time_part} น."))
        container.add_widget(self.create_info_row('assets/icon_hospital.png', f"โรงพยาบาล: {app_data.get('location', '-')}"))
        # ใช้ข้อมูล 'doctor' ที่ได้จาก API ที่แก้ไขแล้ว
        container.add_widget(self.create_info_row('assets/icon_doctor.png', f"แพทย์: {app_data.get('doctor', '-') if app_data.get('doctor') else 'ไม่ได้ระบุ'}"))

        button_layout = BoxLayout(size_hint_y=None, height='44dp', padding=('8dp',0), spacing='10dp')
        
        confirm_button = Button(text="ยืนยันไปพบแพทย์", font_name="THFont", background_color=(0.2, 0.7, 0.3, 1))
        confirm_button.bind(on_release=lambda x, a_id=app_data.get('id'): self.confirm_appointment(a_id))
        
        # ปุ่มแก้ไข (แทนที่ปุ่มเลื่อนนัด)
        edit_button = Button(text="แก้ไข", font_name="THFont", background_color=(0.9, 0.5, 0.1, 1)) # สีส้ม
        # เมื่อกดปุ่มนี้ จะเรียกฟังก์ชันใหม่ และส่งข้อมูลนัดหมายทั้งหมด (app_data) ไปด้วย
        edit_button.bind(on_release=lambda x, data=app_data: self.go_to_edit_appointment(data))

        delete_btn = Button(
            text='ลบ', font_name='THFont', size_hint_x=0.5,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_release=lambda x, a_id=app_data.get('id'), a_title=app_data.get('title'): self.confirm_delete_appointment(a_id, a_title))
        
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(edit_button) # <-- เพิ่มปุ่มแก้ไข
        button_layout.add_widget(delete_btn)
        container.add_widget(button_layout)

        return container

    def create_info_row(self, icon_source, text):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height='24dp', spacing=4)
        row.add_widget(Image(source=icon_source, size_hint_x=None, width='24dp'))
        label = Label(text=text, font_name="THFont", font_size="15sp", color=(0.2,0.2,0.2,1), halign='left')
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        row.add_widget(label)
        return row
    def go_to_edit_appointment(self, appointment_data):
        """
        เก็บข้อมูลนัดหมายที่จะแก้ไขไว้ใน ScreenManager
        แล้วเปลี่ยนไปหน้าจอแก้ไข
        """
        self.manager.current_appointment_data = appointment_data
        self.manager.current = 'edit_appointment_screen'
        
    def go_to_add_appointment(self):
        self.manager.current = 'add_appointment_screen'

    # --- *** จุดที่แก้ไข 2: ย้ายฟังก์ชันทั้งหมดมาไว้ที่นี่ *** ---
    def confirm_appointment(self, appointment_id):
        self.update_appointment_status(appointment_id, 'confirmed', "ยืนยันการไปพบแพทย์เรียบร้อย")

    def postpone_appointment(self, appointment_id):
        self.update_appointment_status(appointment_id, 'postponed', "แจ้งขอเลื่อนนัดเรียบร้อย")
        
    def update_appointment_status(self, app_id, status, success_message):
        api = ApiClient()
        response = api.post(f'/appointments/update_status/{app_id}', data={'status': status})

        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message=success_message).open()
            self.load_appointments() 
        else:
            AlertBox(title="เกิดข้อผิดพลาด", message="ไม่สามารถอัปเดตสถานะได้").open()
        
    def confirm_delete_appointment(self, app_id, app_title):
        def on_confirm(*args):
            self.delete_appointment(app_id)
        
        alert = AlertBox(
            title="ยืนยันการลบ",
            message=f"คุณต้องการลบนัดหมาย [b]{app_title}[/b] ใช่หรือไม่?",
            on_ok_callback=on_confirm
        )
        alert.open()

    def delete_appointment(self, app_id):
        api = ApiClient()
        response = api.delete(f'/appointments/delete/{app_id}')

        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message="ลบนัดหมายเรียบร้อยแล้ว").open()
            self.load_appointments()
        else:
            msg = "ไม่สามารถลบนัดหมายได้"
            if response:
                try: msg = response.json().get('msg', msg)
                except: msg = f"เกิดข้อผิดพลาด (Code: {response.status_code})"
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()