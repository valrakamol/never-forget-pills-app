from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from api_client import ApiClient, clear_auth_token
from widgets.alert_box import AlertBox
from kivy.graphics import Color, RoundedRectangle

class ElderDashboardScreen(Screen):
    # เชื่อม Widget จากไฟล์ .kv
    medicine_list_layout = ObjectProperty(None)
    appointment_list_layout = ObjectProperty(None)
    welcome_label = ObjectProperty(None)

    def on_enter(self, *args):
        """
        โหลดข้อมูลใหม่ทุกครั้งที่เข้ามาที่หน้านี้
        """
        # ตั้งค่าข้อความต้อนรับแบบคงที่
        if self.welcome_label:
            self.welcome_label.text = "ยินดีต้อนรับ"
            
        self.load_my_medications()
        self.load_my_appointments() 
    
    def load_my_medications(self):
        """
        โหลดรายการยาและสร้าง UI ด้วยโค้ด Python
        """
        layout = self.medicine_list_layout
        layout.clear_widgets()
        api = ApiClient()
        response = api.get('/medicines/my_medications')

        if response and response.status_code == 200:
            meds = response.json().get('medications', [])
            if not meds:
                layout.add_widget(Label(text='วันนี้ไม่มีรายการยา', font_name="THFont"))
            else:
                for med in meds:
                    card = self.create_medicine_card(med)
                    layout.add_widget(card)
        else:
            layout.add_widget(Label(text="ไม่สามารถโหลดข้อมูลยาได้", font_name="THFont", color=(1,0,0,1)))

    def load_my_appointments(self):
        """
        โหลดรายการนัดหมายและสร้าง UI ด้วยโค้ด Python
        """
        layout = self.appointment_list_layout
        layout.clear_widgets()
        api = ApiClient()
        response = api.get('/appointments/my_appointments')

        if response and response.status_code == 200:
            appointments = response.json().get('appointments', [])
            if not appointments:
                layout.add_widget(Label(text="ไม่มีนัดหมายเร็วๆ นี้", font_name="THFont", color=(.7,.7,.7,1)))
            else:
                for app_data in appointments:
                    card = self.create_appointment_card(app_data)
                    layout.add_widget(card)
        else:
            layout.add_widget(Label(text="ไม่สามารถโหลดข้อมูลนัดหมายได้", font_name="THFont", color=(1,0,0,1)))
    
    def create_medicine_card(self, med_data):
        """
        สร้าง Widget Card สำหรับยา 1 รายการ พร้อมพื้นหลังที่สามารถอัปเดตได้
        """
        from kivy.graphics import Color, RoundedRectangle
        from kivy.properties import BooleanProperty

        # --- *** จุดที่แก้ไขทั้งหมด *** ---
        # 1. สร้าง Custom BoxLayout ที่มี property 'is_taken_today' ของตัวเอง
        class MedicineCardLayout(BoxLayout):
            is_taken_today = BooleanProperty(False)

        # 2. สร้าง instance ของ Custom Layout และส่งค่า is_taken_today เข้าไป
        card = MedicineCardLayout(
            orientation='vertical', padding='12dp', spacing='8dp', 
            size_hint_y=None, height='130dp',
            is_taken_today=med_data.get('is_taken_today', False)
        )
        
        # 3. สร้างฟังก์ชันสำหรับวาดพื้นหลัง
        def draw_background(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                # ใช้ instance.is_taken_today ในการตัดสินใจเลือกสี
                if instance.is_taken_today:
                    Color(0.9, 0.98, 0.9, 1) # สีเขียวอ่อน (ทานแล้ว)
                else:
                    Color(1, 1, 1, 1) # สีขาว (ยังไม่ทาน)
                RoundedRectangle(pos=instance.pos, size=instance.size, radius=[10,])
        
        # 4. ผูกการวาดพื้นหลังเข้ากับ event การเปลี่ยนแปลงที่จำเป็น
        card.bind(pos=draw_background, size=draw_background, is_taken_today=draw_background)
        # เรียกใช้ครั้งแรกเพื่อวาด
        draw_background(card, None)
        # --- ************************* ---
        
        # --- (ส่วนที่เหลือของการสร้าง UI เหมือนเดิม) ---
        row1 = BoxLayout(size_hint_y=None, height='30dp')
        row1.add_widget(Label(text=med_data.get('name', ''), font_name='THFont', font_size='20sp', bold=True, halign='left', color=(0,0,0,1)))
        row1.add_widget(Label(text=med_data.get('time_to_take', ''), font_name='THFont', font_size='20sp', halign='right', color=(0,0,0,1)))
        card.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height='20dp')
        row2.add_widget(Label(text=f"ปริมาณ: {med_data.get('dosage', '')}", font_name='THFont', font_size='14sp', halign='left', color=(.3,.3,.3,1)))
        row2.add_widget(Label(text=med_data.get('meal_instruction', ''), font_name='THFont', font_size='14sp', halign='right', color=(.3,.3,.3,1)))
        card.add_widget(row2)

        action_area = BoxLayout(size_hint_y=None, height='44dp', padding=('8dp', 0))
        if med_data.get('is_taken_today'):
            action_area.add_widget(Label(text='ทานแล้ววันนี้', font_name='THFont', color=(0.1, 0.5, 0.1, 1), bold=True))
        else:
            button = Button(text='ยืนยันการทานยา', font_name='THFont')
            # --- *** แก้ไข: ปุ่มจะเรียกฟังก์ชันใหม่ *** ---
            button.bind(on_release=lambda x, c=card, m_id=med_data.get('id'): self.log_medication_and_update_ui(c, m_id))
            action_area.add_widget(button)
        card.add_widget(action_area)

        return card

    def create_appointment_card(self, app_data):
        """
        สร้าง Widget Card สำหรับนัดหมาย 1 รายการ พร้อมพื้นหลังสีขาว
        """
        from kivy.graphics import Color, RoundedRectangle
        card = BoxLayout(orientation='vertical', padding='12dp', spacing='8dp', size_hint_y=None, height='160dp')
        
        with card.canvas.before:
            Color(0.95, 0.95, 1, 1) # สีฟ้าอ่อน
            RoundedRectangle(pos=card.pos, size=card.size, radius=[10,])
        
        def update_rect(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.95, 0.95, 1, 1)
                RoundedRectangle(pos=instance.pos, size=instance.size, radius=[10,])
        card.bind(pos=update_rect, size=update_rect)
        
        # ข้อมูล (ทำให้เป็นสีดำ)
        card.add_widget(Label(text=app_data.get('title', ''), font_name='THFont', font_size='18sp', bold=True, halign='left', text_size=(250, None), color=(0,0,0,1)))
        card.add_widget(Label(text=f"วันที่: {app_data.get('datetime', '')}", font_name='THFont', halign='left', text_size=(250, None), color=(0,0,0,1)))
        card.add_widget(Label(text=f"สถานที่: {app_data.get('location', '')}", font_name='THFont', halign='left', text_size=(250, None), color=(0,0,0,1)))
        
        card.add_widget(BoxLayout(size_hint_y=1)) # Spacer
        
        # ปุ่ม
        button_layout = BoxLayout(size_hint_y=None, height='44dp', spacing='10dp')
        confirm_btn = Button(text='ไปพบแพทย์แล้ว', font_name='THFont', background_color=(0.2, 0.7, 0.3, 1))
        confirm_btn.bind(on_release=lambda x, a_id=app_data.get('id'): self.confirm_appointment(a_id))
        postpone_btn = Button(text='แจ้งเลื่อนนัด', font_name='THFont', background_color=(1, 0.6, 0, 1))
        postpone_btn.bind(on_release=lambda x, a_id=app_data.get('id'): self.postpone_appointment(a_id))
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(postpone_btn)
        card.add_widget(button_layout)
        
        return card
    
    def confirm_appointment(self, appointment_id):
        """ส่ง request ยืนยันการไปพบแพทย์"""
        self.update_appointment_status(appointment_id, 'confirmed', "ยืนยันการไปพบแพทย์เรียบร้อย")

    def postpone_appointment(self, appointment_id):
        """ส่ง request แจ้งเลื่อนนัด"""
        self.update_appointment_status(appointment_id, 'postponed', "แจ้งขอเลื่อนนัดเรียบร้อย")
        
    def update_appointment_status(self, app_id, status, success_message):
        """ฟังก์ชันกลางสำหรับอัปเดตสถานะ"""
        api = ApiClient()
        response = api.post(f'/appointments/update_status/{app_id}', data={'status': status})
        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message=success_message).open()
            self.load_my_appointments() 
        else:
            AlertBox(title="เกิดข้อผิดพลาด", message="ไม่สามารถอัปเดตสถานะได้").open()

    def log_medication_and_update_ui(self, card_instance, med_id):
        """
        ฟังก์ชันใหม่: อัปเดต UI ทันที และส่ง request ไป Backend
        """
        # 1. อัปเดต UI ทันที (Optimistic Update)
        # ล้าง action_area แล้วเพิ่ม Label "ทานแล้ว" เข้าไป
        action_area = card_instance.children[0] # action_area คือลูกตัวสุดท้ายที่เพิ่มเข้าไป
        action_area.clear_widgets()
        action_area.add_widget(Label(text='ทานแล้ววันนี้', font_name='THFont', color=(0.1, 0.5, 0.1, 1), bold=True))
        # เปลี่ยนสถานะของ Card เพื่อให้พื้นหลังเปลี่ยนสี
        card_instance.is_taken_today = True

        # 2. ส่ง request ไป Backend ในเบื้องหลัง
        api = ApiClient()
        response = api.post('/medicines/log/take', data={'medication_id': med_id})
        
        # 3. จัดการกรณีที่ API ล้มเหลว (Rollback UI)
        if not response or response.status_code != 200:
            AlertBox(title="เกิดข้อผิดพลาด", message="ไม่สามารถบันทึกข้อมูลได้ กรุณาลองอีกครั้ง").open()
            # โหลดข้อมูลใหม่ทั้งหมดเพื่อย้อนสถานะกลับ
            self.load_my_medications()
            
    def logout(self):
        """ออกจากระบบ"""
        clear_auth_token()
        self.manager.current = 'role_select_screen'
        self.manager.transition.direction = 'right'