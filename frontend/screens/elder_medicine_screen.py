from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from api_client import ApiClient
from widgets.alert_box import AlertBox
import os
import requests
from kivy.clock import mainthread
from kivy.app import App
from time import time

class ElderMedicineScreen(Screen):
    medicine_list_layout = ObjectProperty(None)
    
    def on_enter(self):
        """
        โหลดข้อมูลยาใหม่ทุกครั้งที่เข้ามาที่แท็บนี้
        """
        self.load_my_medications()
        
    def load_my_medications(self):
        """
        ดึงข้อมูลยาของตัวเองจาก API และสร้าง UI แสดงผล
        """
        if not self.medicine_list_layout:
            return
        
        self.medicine_list_layout.clear_widgets()
        api = ApiClient()
        response = api.get('/medicines/my_medications')

        if response and response.status_code == 200:
            medicines = response.json().get('medications', [])
            if not medicines:
                self.medicine_list_layout.add_widget(Label(text="วันนี้ไม่มีรายการยา", font_name="THFont"))
            else:
                for med in medicines:
                    # สร้าง UI สำหรับยาแต่ละรายการ
                    item = self.create_medicine_item(med)
                    self.medicine_list_layout.add_widget(item)
        else:
            self.medicine_list_layout.add_widget(Label(text="ไม่สามารถโหลดรายการยาได้", font_name="THFont"))

    def create_medicine_item(self, med_data):
        """
        ฟังก์ชันช่วยสำหรับสร้าง Widget ของยา 1 รายการ
        """
        # Layout หลักของการ์ด
        card_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding='10dp', spacing='5dp')
        card_layout.bind(minimum_height=card_layout.setter('height'))
        
        # ส่วนบน: รูปภาพ + ข้อมูล
        top_layout = BoxLayout(size_hint_y=None, height='100dp', spacing='10dp')
        
        # ข้อมูลยา
        info_layout = BoxLayout(orientation='vertical', spacing='2dp')
        
        # แถวชื่อ + สถานะ
        name_status_layout = BoxLayout()
        name_status_layout.add_widget(Label(text=med_data.get('name', 'N/A'), font_name="THFont", font_size='22sp', bold=True, color=(0,0,0,1), halign='left', text_size=(None, None)))
        status_text = "กินแล้ว" if med_data.get('is_taken_today') else "ยังไม่กิน"
        status_color = (0.2, 0.8, 0.2, 1) if med_data.get('is_taken_today') else (1, 0.2, 0.2, 1)
        name_status_layout.add_widget(Label(text=status_text, font_name="THFont", color=status_color, halign='right', text_size=(None, None)))
        
        # เพิ่มข้อมูลย่อยๆ
        info_layout.add_widget(name_status_layout)
        info_layout.add_widget(self.create_info_row('assets/icon_time.png', f"เวลา: {med_data.get('time_to_take', '-')}"))
        info_layout.add_widget(self.create_info_row('assets/icon_dosage.png', f"ปริมาณ: {med_data.get('dosage', '-')}"))
        info_layout.add_widget(self.create_info_row('assets/icon_meal.png', f"มื้ออาหาร: {med_data.get('meal_instruction', '-')}"))

        top_layout.add_widget(info_layout)
        
        card_layout.add_widget(top_layout)

        # เพิ่มปุ่มยืนยัน ถ้ายังไม่ได้กินยา
        if not med_data.get('is_taken_today'):
            confirm_button = Button(
                text="ยืนยันว่ากินยาแล้ว",
                font_name="THFont",
                size_hint_y=None,
                height='48dp',
                background_color=(0.46, 0.85, 0.63, 1) # สีเขียวอ่อน
            )
            confirm_button.bind(on_release=lambda x, m_id=med_data.get('id'): self.log_medication(m_id))
            card_layout.add_widget(confirm_button)
            
        return card_layout

    def create_info_row(self, icon_source, text):
        """ฟังก์ชันช่วยสำหรับสร้างแถวข้อมูลที่มี ไอคอน + ข้อความ"""
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height='24dp', spacing=4)
        row.add_widget(Image(source=icon_source, size_hint_x=None, width='24dp'))
        label = Label(text=text, font_name="THFont", font_size="16sp", color=(0,0,0,1), halign='left')
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        row.add_widget(label)
        return row
        
    def log_medication(self, med_id):
        """
        ส่ง request ไป Backend เพื่อบันทึกการทานยา
        """
        api = ApiClient()
        response = api.post('/medicines/log/take', data={'medication_id': med_id})

        if response and response.status_code == 200:
            # ไม่ต้องแสดง Popup ทุกครั้ง, แค่รีเฟรชหน้าจอก็พอ
            self.load_my_medications()
        else:
            AlertBox(title="เกิดข้อผิดพลาด", message="ไม่สามารถบันทึกการกินยาได้").open()