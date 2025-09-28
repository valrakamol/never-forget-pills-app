from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from api_client import ApiClient, clear_auth_token, get_stored_auth_info
from widgets.alert_box import AlertBox

class ElderProfileScreen(Screen):
    # เชื่อม Widget จาก .kv เข้ากับโค้ด Python
    full_name_label = ObjectProperty(None)
    username_label = ObjectProperty(None)
    
    def on_enter(self):
        """
        ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่เข้ามาที่แท็บนี้
        """
        self.load_profile_data()
        
    def load_profile_data(self):
        """
        ดึงข้อมูลโปรไฟล์จากที่เก็บไว้ในเครื่อง (JsonStore)
        หรือจะเรียก API /users/me อีกครั้งก็ได้
        """
        # วิธีที่ 1: ดึงจากข้อมูลที่เก็บไว้ (เร็วกว่า)
        auth_info = get_stored_auth_info()
        if auth_info and self.full_name_label and self.username_label:
            user_info = auth_info.get('user_info', {})
            self.full_name_label.text = user_info.get('full_name', 'ไม่พบชื่อ')
            self.username_label.text = f"ชื่อผู้ใช้: {user_info.get('username', 'N/A')}"
        else:
            # วิธีที่ 2: เรียก API ใหม่ (ข้อมูลสดใหม่กว่า)
            self.fetch_profile_from_api()
            
    def fetch_profile_from_api(self):
        """
        ดึงข้อมูลโปรไฟล์ล่าสุดจาก Backend
        """
        api = ApiClient()
        response = api.get('/users/me')
        if response and response.status_code == 200:
            user_info = response.json()
            if self.full_name_label:
                self.full_name_label.text = user_info.get('full_name', 'ไม่พบชื่อ')
            if self.username_label:
                self.username_label.text = f"ชื่อผู้ใช้: {user_info.get('username', 'N/A')}"
        else:
            if self.full_name_label: self.full_name_label.text = "ไม่สามารถโหลดข้อมูลได้"
            if self.username_label: self.username_label.text = ""

    def logout(self):
        """
        ออกจากระบบ, ล้าง Token, และกลับไปที่หน้าเลือก Role เริ่มต้น
        """
        def on_confirm_logout(*args):
            clear_auth_token()
            self.manager.current = 'role_select_screen'
            self.manager.transition.direction = 'right'

        alert = AlertBox(
            title="ยืนยันการออกจากระบบ",
            message="คุณต้องการออกจากระบบใช่หรือไม่?",
            ok_text="ตกลง",
            cancel_text="ยกเลิก",
            show_cancel_button=True,
            on_ok_callback=on_confirm_logout,
        )
        alert.open()