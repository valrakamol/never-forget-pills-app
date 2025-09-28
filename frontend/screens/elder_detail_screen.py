from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

class ElderDetailScreen(Screen):
    elder_name = StringProperty('')

    def on_pre_enter(self, *args):
        # ดึงชื่อผู้สูงอายุจาก session หรือ property ของ WindowManager
        self.elder_name = self.manager.current_elder_name or ''

    def go_back(self):
        """
        กลับไปหน้า Dashboard ของผู้ดูแล และ "สั่งให้มันรีเฟรช"
        """
        # 1. ไปที่หน้า 'caregiver_screen'
        self.manager.current = 'caregiver_screen'
        
        # 2. เข้าถึง 'caregiver_screen' ผ่าน manager
        caregiver_screen = self.manager.get_screen('caregiver_screen')
        
        # 3. เรียกฟังก์ชัน load_managed_elders()
        caregiver_screen.load_managed_elders()