from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from api_client import ApiClient
from datetime import datetime, timedelta
# from calendar import month_name # อาจจะต้องใช้ library อื่นสำหรับเดือนไทย

class HealthRecordScreen(Screen):
    record_list_layout = ObjectProperty(None)
    filter_button = ObjectProperty(None)

    def on_enter(self):
        self.load_health_records()
        self.setup_filter_dropdown()

    def load_health_records(self, month=None, year=None):
        self.record_list_layout.clear_widgets()
        elder_id = self.manager.current_elder_id

        api = ApiClient()
        # --- สร้าง query string เอง ---
        url = f'/health/records/elder/{elder_id}'
        if month and year:
            url += f'?month={month}&year={year}'
        response = api.get(url)
        
        if response and response.status_code == 200:
            records = response.json().get('records', [])
            if not records:
                self.record_list_layout.add_widget(Label(text="ยังไม่มีบันทึกสุขภาพ", font_name="THFont", color=(0,0,0,1)))
            else:
                for i, rec in enumerate(records):
                    # สร้าง UI ของรายการบันทึก
                    item = self.create_health_record_item(rec)
                    self.record_list_layout.add_widget(item)
                    
                    # เพิ่มเส้นคั่น (ถ้าไม่ใช่รายการสุดท้าย)
                    if i < len(records) - 1:
                        from kivy.uix.widget import Widget
                        separator = Widget(size_hint_y=None, height='1dp')
                        with separator.canvas:
                            from kivy.graphics import Color, Rectangle
                            Color(0.8, 0.8, 0.8, 1) # สีเทา
                            self.rect = Rectangle(pos=separator.pos, size=separator.size)
                        def update_rect(instance, value):
                            self.rect.pos = instance.pos
                            self.rect.size = instance.size
                        separator.bind(pos=update_rect, size=update_rect)
                        self.record_list_layout.add_widget(separator)

        else:
            self.record_list_layout.add_widget(Label(text="ไม่สามารถโหลดข้อมูลได้", font_name="THFont", color=(1,0,0,1)))

    def create_health_record_item(self, rec_data):
        """
        ฟังก์ชันสำหรับสร้าง Widget ของบันทึกสุขภาพ 1 รายการ (แบบไม่มี Card)
        """
        # --- *** จุดที่แก้ไข *** ---
        # ใช้ BoxLayout ธรรมดาที่ไม่มี canvas
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding='12dp', spacing='8dp')
        container.bind(minimum_height=container.setter('height'))

        # แถวบน: Title และ Date
        header = BoxLayout(size_hint_y=None, height='30dp')
        header.add_widget(Label(text=rec_data.get('title', 'ตรวจสุขภาพ'), font_name='THFont', font_size='18sp', bold=True, color=(0,0,0,1), halign='left', text_size=(None, None)))
        header.add_widget(Label(text=rec_data.get('recorded_at'), font_name='THFont', font_size='14sp', color=(.5,.5,.5,1), halign='right', text_size=(None, None)))
        container.add_widget(header)

        # ข้อมูลสุขภาพ
        info_grid = GridLayout(cols=1, spacing='5dp', size_hint_y=None)
        info_grid.bind(minimum_height=info_grid.setter('height'))

        info_grid.add_widget(self.create_info_row('assets/icon_health_active.png', f"บน {rec_data.get('systolic_bp', '-')} มิลลิเมตรปรอท"))
        info_grid.add_widget(self.create_info_row('assets/icon_health_active.png', f"ล่าง {rec_data.get('diastolic_bp', '-')} มิลลิเมตรปรอท"))
        info_grid.add_widget(self.create_info_row('assets/icon_weight.png', f"{rec_data.get('weight', '-')} กิโลกรัม"))
        info_grid.add_widget(self.create_info_row('assets/icon_pulse.png', f"{rec_data.get('pulse', '-')} ครั้ง/นาที"))
        info_grid.add_widget(self.create_info_row('assets/icon_note.png', f"{rec_data.get('notes', 'ไม่มีหมายเหตุ')}"))
        container.add_widget(info_grid)
        
        return container

    def create_info_row(self, icon_source, text):
        """ฟังก์ชันช่วยสำหรับสร้างแถวข้อมูลที่มี ไอคอน + ข้อความ"""
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height='24dp', spacing=4)
        row.add_widget(Image(source=icon_source, size_hint_x=None, width='24dp'))
        label = Label(text=text, font_name="THFont", font_size="14sp", color=(0.2,0.2,0.2,1), halign='left')
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        row.add_widget(label)
        return row

    def setup_filter_dropdown(self):
        self.dropdown = DropDown()
        thai_month_abbr = {
            1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.",
            5: "พ.ค.", 6: "มิ.ย.", 7: "ก.ค.", 8: "ส.ค.",
            9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."
        }
        today = datetime.today()
        all_btn = Button(text="แสดงทั้งหมด", size_hint_y=None, height=44, font_name="THFont")
        all_btn.bind(on_release=lambda btn: self.select_month(None, None))
        self.dropdown.add_widget(all_btn)

        # วนลูปย้อนหลัง 5 เดือน (รวมเดือนนี้)
        month = today.month
        year = today.year
        for i in range(5):
            m = month - i
            y = year
            if m <= 0:
                m += 12
                y -= 1
            month_str = f"{thai_month_abbr.get(m, '')} {str(y + 543)[2:]}" # เอาแค่ 2 ตัวท้ายของปี พ.ศ.
            btn = Button(text=month_str, size_hint_y=None, height=44, font_name="THFont")
            btn.bind(on_release=lambda btn, m=m, y=y: self.select_month(m, y))
            self.dropdown.add_widget(btn)

        self.filter_button.bind(on_release=self.dropdown.open)

    def select_month(self, month, year):
        """
        เมื่อเลือกเดือนจาก Dropdown, ให้โหลดข้อมูลใหม่
        ถ้า month และ year เป็น None, ให้โหลดข้อมูลทั้งหมด
        """
        self.load_health_records(month=month, year=year)
        self.dropdown.dismiss()

    def go_to_add_record(self):
        self.manager.current = 'edit_health_screen'