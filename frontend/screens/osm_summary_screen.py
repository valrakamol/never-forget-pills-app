# frontend/screens/osm_summary_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from api_client import ApiClient
from kivy.clock import Clock

class OsmSummaryScreen(Screen):
    summary_layout = ObjectProperty(None)
    risky_list_layout = ObjectProperty(None)

    def on_enter(self):
        # ใช้ Clock.schedule_once เพื่อให้ UI มีเวลาวาดตัวเองก่อนโหลด
        Clock.schedule_once(self.load_summary_data)
    
    def load_summary_data(self, *args):
        self.summary_layout.clear_widgets()
        self.risky_list_layout.clear_widgets()

        api = ApiClient()
        response = api.get('/stats/osm_monthly_summary')

        if not response or response.status_code != 200:
            self.summary_layout.add_widget(Label(text="ไม่สามารถโหลดข้อมูลได้", font_name="THFont"))
            return

        data = response.json()
        summary_data = data.get('summary', {})
        
        # --- *** จุดที่แก้ไข 1: ดึงข้อมูลจาก Key ใหม่ที่ Backend ส่งมา *** ---
        follow_up_elders = data.get('follow_up_elders', [])
        at_risk_elders = data.get('at_risk_elders', [])

        # สร้าง UI สรุป (ส่วนนี้เหมือนเดิม)
        self.summary_layout.add_widget(self.create_stat_box("ปกติ", summary_data.get('normal', 0), (0.2, 0.7, 0.3, 1)))
        self.summary_layout.add_widget(self.create_stat_box("กลุ่มเสี่ยง", summary_data.get('at_risk', 0), (1, 0.6, 0, 1)))
        self.summary_layout.add_widget(self.create_stat_box("ต้องติดตาม", summary_data.get('follow_up', 0), (0.8, 0.2, 0.2, 1)))

        # --- *** จุดที่แก้ไข 2: สร้าง UI รายชื่อของทั้งสองกลุ่ม *** ---
        has_risky_people = False
        
        # 1. แสดงกลุ่มที่ต้องติดตามก่อน (ถ้ามี)
        if follow_up_elders:
            has_risky_people = True
            for elder in follow_up_elders:
                # ทำให้ข้อความเด่นขึ้นด้วยสีแดง
                message = f"[color=dd2222]{elder.get('full_name')} (พบค่าผิดปกติ {elder.get('risk_count')} ครั้ง)[/color]"
                item = Label(
                    text=message,
                    font_name="THFont",
                    font_size='16sp',
                    size_hint_y=None,
                    height='40dp',
                    markup=True # <-- เปิดใช้งาน markup เพื่อให้ [color] ทำงาน
                )
                self.risky_list_layout.add_widget(item)
        
        # 2. แสดงกลุ่มเสี่ยง (ถ้ามี)
        if at_risk_elders:
            has_risky_people = True
            for elder in at_risk_elders:
                 # ใช้สีส้มสำหรับกลุ่มเสี่ยง
                message = f"[color=ff8800]{elder.get('full_name')} (พบค่าผิดปกติ {elder.get('risk_count')} ครั้ง)[/color]"
                item = Label(
                    text=message,
                    font_name="THFont",
                    font_size='16sp',
                    size_hint_y=None,
                    height='40dp',
                    markup=True # <-- เปิดใช้งาน markup
                )
                self.risky_list_layout.add_widget(item)

        # 3. ถ้าไม่มีใครในทั้งสองกลุ่มเลย ให้แสดงข้อความ
        if not has_risky_people:
            no_one_label = Label(
                text="ไม่มีผู้สูงอายุในกลุ่มเสี่ยงหรือกลุ่มที่ต้องติดตาม", 
                font_name="THFont",
                color=(0.5, 0.5, 0.5, 1) # สีเทา
            )
            self.risky_list_layout.add_widget(no_one_label)

    def create_stat_box(self, title, value, color):
        box = BoxLayout(orientation='vertical', padding='10dp')
        with box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(rgba=color)
            box._bg_rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[10])

        def update_rect(instance, value):
            instance._bg_rect.pos = instance.pos
            instance._bg_rect.size = instance.size

        box.bind(pos=update_rect, size=update_rect)
        
        # ข้อความเป็นสีขาว
        box.add_widget(Label(text=str(value), font_name="THFont", font_size='32sp', bold=True, color=(1,1,1,1)))
        box.add_widget(Label(text=title, font_name="THFont", font_size='16sp', color=(1,1,1,1)))

        return box