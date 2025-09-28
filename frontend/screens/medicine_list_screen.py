from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from api_client import ApiClient
from widgets.alert_box import AlertBox

class MedicineListScreen(Screen):
    medicine_list_layout = ObjectProperty(None)

    def on_enter(self):
        self.load_medications()

    def load_medications(self):
        if not self.medicine_list_layout:
            return
            
        self.medicine_list_layout.clear_widgets()
        elder_id = self.manager.current_elder_id
        api = ApiClient()
        response = api.get(f'/medicines/elder/{elder_id}')

        if response and response.status_code == 200:
            medicines = response.json().get('medicines', [])
            if not medicines:
                self.medicine_list_layout.add_widget(Label(text="ยังไม่มีรายการยา", font_name="THFont", color=(0,0,0,1)))
            else:
                for med in medicines:
                    item = self.create_medicine_item(med)
                    self.medicine_list_layout.add_widget(item)
        else:
            self.medicine_list_layout.add_widget(Label(text="ไม่สามารถโหลดรายการยาได้", font_name="THFont", color=(1,0,0,1)))

    def create_medicine_item(self, med_data):
        """
        ฟังก์ชันสำหรับสร้าง Widget ของยา 1 รายการ (ไม่มีรูปภาพ)
        """
        # Layout หลักของการ์ด (แนวตั้ง)
        card_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding='10dp', spacing='5dp')
        card_layout.bind(minimum_height=card_layout.setter('height'))
        
        # --- ส่วนข้อมูลยา ---
        # แถวบน: ชื่อยา และ สถานะ
        name_status_layout = BoxLayout(size_hint_y=None, height='30dp')
        name_label = Label(text=med_data.get('name', 'N/A'), font_name="THFont", font_size='18sp', bold=True, color=(0,0,0,1), halign='left')
        name_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        
        # TODO: ต้องมี Logic การดึงสถานะจริงจาก Backend
        status_text = "กินแล้ว" if med_data.get('is_taken_today', False) else "ยังไม่กิน"
        status_color = (0.2, 0.8, 0.2, 1) if status_text == "กินแล้ว" else (1, 0.2, 0.2, 1)
        status_label = Label(text=status_text, font_name="THFont", color=status_color, halign='right', size_hint_x=0.4)

        name_status_layout.add_widget(name_label)
        name_status_layout.add_widget(status_label)
        
        card_layout.add_widget(name_status_layout)
        
        # เพิ่มข้อมูลย่อยๆ
        card_layout.add_widget(self.create_info_row(f"เวลา: {med_data.get('time_to_take', '-')}"))
        card_layout.add_widget(self.create_info_row(f"ปริมาณ: {med_data.get('dosage', '-')}"))
        card_layout.add_widget(self.create_info_row(f"มื้ออาหาร: {med_data.get('meal_instruction', '-')}"))
        
        # ส่วนปุ่มลบ (อยู่ล่างสุด)
        delete_button = Button(
            text='ลบ', 
            font_name='THFont', 
            size_hint=(1, None), # เต็มความกว้าง
            height='40dp',
            background_color=(1,0.3,0.3,1) # สีแดง
        )
        delete_button.bind(on_release=lambda x: self.confirm_delete_medication(med_data.get('id'), med_data.get('name')))
        card_layout.add_widget(delete_button)
        
        return card_layout
        
    def create_info_row(self, text):
        """ฟังก์ชันช่วยสำหรับสร้างแถวข้อมูล (ไม่มีไอคอน)"""
        label = Label(text=text, font_name="THFont", font_size="14sp", color=(0.2,0.2,0.2,1), halign='left', size_hint_y=None)
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        label.bind(texture_size=label.setter('size'))
        return label
        
    def go_to_add_medicine(self):
        """นำทางไปยังหน้าจอเพิ่มยา"""
        self.manager.current = 'add_medicine_screen'

    def confirm_delete_medication(self, med_id, med_name):
        """แสดง Popup เพื่อยืนยันการลบยา"""
        def on_confirm(*args):
            self.delete_medication(med_id)
        
        alert = AlertBox(
            title="ยืนยันการลบ",
            message=f"คุณต้องการลบยา [b]{med_name}[/b] ใช่หรือไม่?",
            on_ok_callback=on_confirm
        )
        alert.open()

    def delete_medication(self, med_id):
        """ส่ง request ลบยาไปที่ Backend"""
        api = ApiClient()
        response = api.delete(f'/medicines/delete/{med_id}')

        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message="ลบยาเรียบร้อยแล้ว").open()
            self.load_medications() # รีเฟรชรายการ
        else:
            msg = "ไม่สามารถลบยาได้"
            if response:
                try: 
                    msg = response.json().get('msg', msg)
                except: 
                    msg = f"เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ (Code: {response.status_code})"
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()