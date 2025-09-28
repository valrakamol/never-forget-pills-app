# frontend/screens/add_elder_volunteer_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox

class AddElderVolunteerScreen(Screen):
    # เชื่อม Widget จาก .kv
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    
    def on_pre_enter(self, *args):
        """เคลียร์ฟอร์มทุกครั้งที่เข้ามาหน้านี้"""
        self.username_input.text = ""
        self.password_input.text = ""
        
    def link_elder(self):
        """รวบรวมข้อมูลและส่งไป Backend เพื่อเชื่อมโยงบัญชี"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not all([username, password]):
            AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกชื่อผู้ใช้และรหัสผ่านของผู้สูงอายุ").open()
            return
            
        api = ApiClient()
        response = api.post('/users/link_elder', data={'username': username, 'password': password})
        
        if response and response.status_code == 200:
            def on_success(*args):
                self.go_back()
            AlertBox(title="สำเร็จ", message="เชื่อมโยงกับผู้สูงอายุเรียบร้อยแล้ว", on_ok_callback=on_success).open()
        else:
            msg = "ไม่สามารถเชื่อมโยงได้"
            if response:
                try: msg = response.json().get('msg', 'ชื่อผู้ใช้หรือรหัสผ่านของผู้สูงอายุไม่ถูกต้อง')
                except: pass
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()

    def go_back(self, *args):
        """กลับไปหน้าจอหลักของ อสม."""
        self.manager.current = 'osm_screen'