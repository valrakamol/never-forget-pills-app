#frontend/screens/role_select_screen.py
from kivy.uix.screenmanager import Screen

class RoleSelectScreen(Screen):
    def select_role(self, role_type):
        """
        นำทางไปยังหน้าจอ Login ที่เหมาะสมตาม Role ที่เลือก
        """
        if role_type == 'elder':
            # ไปหน้า Login ของผู้สูงอายุ
            self.manager.current = 'elder_login_screen'
        elif role_type == 'manager':
            # ไปหน้า Login ของผู้ดูแล/อสม.
            self.manager.current = 'login_screen'
        
        # ตั้งค่าทิศทางการเปลี่ยนหน้าจอ (optional)
        self.manager.transition.direction = 'left'