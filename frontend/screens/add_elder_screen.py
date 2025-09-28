from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox

class AddElderScreen(Screen):
    # เชื่อม Widget จากไฟล์ .kv เข้ากับโค้ด Python
    username_input = ObjectProperty(None)
    first_name_input = ObjectProperty(None)
    last_name_input = ObjectProperty(None)
    password_input = ObjectProperty(None)

    def on_pre_enter(self, *args):
        """
        ฟังก์ชันนี้จะถูกเรียกก่อนที่หน้าจอจะแสดง
        ทำหน้าที่เคลียร์ฟอร์มทุกครั้งที่เข้ามาหน้านี้
        """
        # ตรวจสอบว่า Widget ถูกเชื่อมต่อแล้วหรือยังก่อนใช้งาน
        if self.username_input: self.username_input.text = ""
        if self.first_name_input: self.first_name_input.text = ""
        if self.last_name_input: self.last_name_input.text = ""
        if self.password_input: self.password_input.text = ""

    def add_elder(self):
        """
        รวบรวมข้อมูลจากฟอร์ม, ตรวจสอบ, และส่งไปสร้างบัญชีผู้สูงอายุที่ Backend
        """
        username = self.username_input.text.strip()
        first_name = self.first_name_input.text.strip()
        last_name = self.last_name_input.text.strip()
        password = self.password_input.text.strip()

        # Input Validation: ตรวจสอบว่ากรอกข้อมูลครบถ้วน
        if not all([username, first_name, last_name, password]):
            alert = AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกข้อมูลให้ครบทุกช่อง")
            alert.open()
            return

        # เตรียมข้อมูลที่จะส่งไป Backend
        data_to_send = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "password": password
        }

        api = ApiClient()
        # เรียกใช้ Endpoint สำหรับ "สร้าง" บัญชีผู้สูงอายุ
        response = api.post('/users/add_elder', data=data_to_send)
        
        if response and response.status_code == 201:
            # กรณีสำเร็จ
            def on_success_close(*args):
                self.go_back()
            
            alert = AlertBox(
                title="สำเร็จ", 
                message=response.json().get('msg', "เพิ่มผู้สูงอายุเรียบร้อยแล้ว"), 
                on_ok_callback=on_success_close
            )
            alert.open()
        else:
            # กรณีเกิดข้อผิดพลาด
            msg = "ไม่สามารถเพิ่มผู้สูงอายุได้"
            if response:
                try: 
                    msg = response.json().get('msg', msg)
                except: 
                    pass
            alert = AlertBox(title="เกิดข้อผิดพลาด", message=msg)
            alert.open()
            
    def switch_to_caregiver_screen(self):
        self.manager.current = 'caregiver_screen'

    def go_to_add_elder(self):
        self.manager.current = 'add_elder_screen'

    def go_to_caregiver_profile(self):
        self.manager.current = 'caregiver_profile_screen'

    def go_back(self):
        """
        นำทางกลับไปยังหน้า Dashboard ของผู้ดูแล
        """
        self.manager.current = 'caregiver_screen'