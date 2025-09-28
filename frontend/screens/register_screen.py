#frontend/screens/register_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox

class RegisterScreen(Screen):
    # เชื่อม Widget จากไฟล์ .kv
    username_input = ObjectProperty(None)
    first_name_input = ObjectProperty(None)
    last_name_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    role_spinner = ObjectProperty(None)

    def on_enter(self, *args):
        """
        เคลียร์ข้อมูลในฟอร์มทุกครั้งที่เข้ามาหน้านี้
        """
        self.username_input.text = ""
        self.first_name_input.text = ""
        self.last_name_input.text = ""
        self.password_input.text = ""
        # ตั้งค่าเริ่มต้นให้ Spinner
        self.role_spinner.text = 'เลือกบทบาท'

    def register_user(self):
        """
        จัดการการสมัครสมาชิก และแสดงผลลัพธ์ที่ได้จาก Backend
        """
        # 1. แปลงข้อความจาก Spinner เป็นค่า Role ที่จะส่งไป Backend
        role_text = self.role_spinner.text
        if role_text == 'ผู้ดูแล (ดูแลผู้สูงอายุ, เพิ่มยา)':
            role = 'caregiver'
        elif role_text == 'อสม. (บันทึกข้อมูลสุขภาพ)':
            role = 'osm'
        else:
            alert = AlertBox(title="ข้อมูลไม่ครบ", message="กรุณาเลือกบทบาทของคุณ")
            alert.open()
            return
            
        # 2. รวบรวมข้อมูลจากฟอร์ม
        data = {
            "username": self.username_input.text.strip(),
            "first_name": self.first_name_input.text.strip(),
            "last_name": self.last_name_input.text.strip(),
            "password": self.password_input.text.strip(),
            "role": role
        }

        # 3. ตรวจสอบว่ากรอกข้อมูลครบหรือไม่
        if not all([data['username'], data['first_name'], data['last_name'], data['password']]):
            alert = AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกข้อมูลให้ครบทุกช่อง")
            alert.open()
            return

        # 4. ส่ง request ไปยัง Backend
        api = ApiClient()
        response = api.post('/auth/register', data=data)

        # 5. จัดการ Response ที่ได้รับกลับมา
        if response is None:
            alert = AlertBox(title="การเชื่อมต่อล้มเหลว", message="ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้")
            alert.open()
            return
        
        # --- *** ส่วนที่สำคัญ *** ---
        if response.status_code == 201:
            # กรณีที่ Backend สร้าง User สำเร็จ (Status 201 Created)
            
            # สร้าง callback function เพื่อนำทางผู้ใช้ไปหน้า Login
            def go_to_login_on_success(*args):
                self.manager.current = 'login_screen'

            # ดึงข้อความตอบกลับจาก Backend มาแสดงโดยตรง
            # ซึ่งควรจะเป็น "การลงทะเบียนสำเร็จ! บัญชีของคุณกำลังรอการอนุมัติ..."
            success_message = response.json().get('msg', 'ลงทะเบียนสำเร็จ!')

            alert = AlertBox(
                title="ลงทะเบียนสำเร็จ", 
                message=success_message, # แสดงข้อความ "รอการอนุมัติ"
                on_ok_callback=go_to_login_on_success
            )
            alert.open()
        else:
            # กรณีที่ Backend ตอบกลับมาด้วย Error อื่นๆ (เช่น 409 Username ซ้ำ)
            try:
                error_msg = response.json().get('msg', 'เกิดข้อผิดพลาดที่ไม่รู้จัก')
            except:
                error_msg = "เกิดข้อผิดพลาดจากเซิร์ฟเวอร์"
            alert = AlertBox(title="ลงทะเบียนล้มเหลว", message=error_msg)
            alert.open()

    def go_to_login(self):
        """
        นำทางไปยังหน้า Login สำหรับผู้ที่มีบัญชีอยู่แล้ว
        """
        self.manager.current = 'login_screen'