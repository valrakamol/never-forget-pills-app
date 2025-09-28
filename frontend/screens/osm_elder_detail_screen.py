# frontend/screens/osm_elder_detail_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty # <-- เพิ่ม ObjectProperty

class OsmElderDetailScreen(Screen):
    # --- *** แก้ไข/เพิ่ม Properties *** ---
    # เราจะใช้ StringProperty เหมือนเดิมสำหรับชื่อ
    # และเพิ่ม ObjectProperty สำหรับเชื่อมกับ Label
    elder_name = StringProperty('')
    full_name_label = ObjectProperty(None)
    
    def on_pre_enter(self):
        """
        ตั้งค่าเริ่มต้นเมื่อเข้ามาที่หน้านี้
        """
        self.elder_name = self.manager.current_elder_name or "ผู้สูงอายุ"
        # อัปเดต Label ที่เราเชื่อมไว้
        if self.full_name_label:
            self.full_name_label.text = f"ชื่อ: {self.elder_name}"
    
    def go_back(self):
        """
        กลับไปหน้า Dashboard ของ อสม. (หน้ารายชื่อ)
        """
        self.manager.current = 'osm_screen'