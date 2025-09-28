#frontend/screens/login_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
# Import ฟังก์ชันและคลาสที่จำเป็นทั้งหมดจาก api_client
from api_client import ApiClient, save_auth_token, jwt_decode
from widgets.alert_box import AlertBox

class LoginScreen(Screen):
    # เชื่อม Widget จากไฟล์ .kv
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)

    def on_enter(self, *args):
        """
        ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่เข้ามาที่หน้านี้
        เพื่อให้แน่ใจว่าช่องกรอกข้อมูลจะว่างเปล่าเสมอ
        """
        if self.username_input: self.username_input.text = ""
        if self.password_input: self.password_input.text = ""

    def login_user(self):
        """
        จัดการกระบวนการล็อกอินทั้งหมด ตั้งแต่การรับข้อมูล, ส่ง API,
        และจัดการกับผลลัพธ์ที่ได้กลับมา
        """
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        # 1. ตรวจสอบข้อมูลฝั่ง Client ก่อนส่ง
        if not all([username, password]):
            alert = AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
            alert.open()
            return

        # 2. ส่ง request ไปยัง Backend
        api = ApiClient()
        response = api.post('/auth/login', data={'username': username, 'password': password})

        # 3. ตรวจสอบว่าการเชื่อมต่อสำเร็จหรือไม่
        if response is None:
            alert = AlertBox(title="การเชื่อมต่อล้มเหลว", message="ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้")
            alert.open()
            return

        # 4. ตรวจสอบผลลัพธ์จาก status code
        if response.status_code == 200:
            # กรณีที่ Login สำเร็จ
            try:
                result = response.json()
                token = result.get('access_token')

                if not token:
                    alert = AlertBox(title="เกิดข้อผิดพลาด", message="ไม่ได้รับ Token จากเซิร์ฟเวอร์")
                    alert.open()
                    return
                
                # --- *** นี่คือ Logic ใหม่ที่ถูกต้อง *** ---
                # 4.1 ถอดรหัส Token เพื่อเอา Custom Claims (ข้อมูลผู้ใช้) ออกมา
                decoded_token = jwt_decode(token)
                if not decoded_token:
                    alert = AlertBox(title="เกิดข้อผิดพลาด", message="ไม่สามารถถอดรหัสข้อมูล Token ได้")
                    alert.open()
                    return

                # 4.2 สร้าง object user_info จากข้อมูลที่ถอดรหัสแล้ว
                user_info = {
                    'id': decoded_token.get('sub'),
                    'role': decoded_token.get('role'),
                    'full_name': decoded_token.get('full_name'),
                    'username': decoded_token.get('username')
                }

                # 4.3 บันทึก Token และ user_info ที่สร้างขึ้น
                save_auth_token(token, user_info)
                
                # 4.4 นำทางไปยังหน้าจอที่ถูกต้องตาม role
                role = user_info.get('role')
                if role == 'caregiver':
                    self.manager.current = 'caregiver_screen'
                elif role in ['osm', 'volunteer']:
                    self.manager.current = 'osm_screen'
                else:
                    # กรณีนี้จะเกิดขึ้นถ้า login ด้วยบัญชีผู้สูงอายุในหน้านี้
                    alert = AlertBox(title="เข้าสู่ระบบล้มเหลว", message="บัญชีนี้ไม่ใช่สำหรับผู้ดูแลหรือ อสม.")
                    alert.open()
                    return
                
                self.manager.transition.direction = 'left'

            except Exception as e:
                # กรณีที่ response.json() หรือ jwt_decode() ทำงานผิดพลาด
                alert = AlertBox(title="ข้อผิดพลาดในการประมวลผล", message=f"ไม่สามารถอ่านข้อมูลที่ได้รับ: {e}")
                alert.open()
        
        else:
            # กรณีที่ Login ไม่สำเร็จ (เช่น รหัสผิด, user ไม่มี)
            try:
                error_msg = response.json().get('msg', 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
            except:
                error_msg = "เกิดข้อผิดพลาดที่ไม่รู้จักจากเซิร์ฟเวอร์"
            alert = AlertBox(title="เข้าสู่ระบบล้มเหลว", message=error_msg)
            alert.open()
            
    def go_to_register(self):
        """
        นำทางไปยังหน้าสมัครสมาชิก
        """
        self.manager.current = 'register_screen'

    def go_back(self):
        """
        นำทางกลับไปยังหน้าเลือก Role
        """
        self.manager.current = 'role_select_screen'