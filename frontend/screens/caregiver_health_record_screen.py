# frontend/screens/caregiver_health_record_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from datetime import datetime
from api_client import ApiClient

class CaregiverHealthRecordScreen(Screen):
    record_list_layout = ObjectProperty(None)
    filter_button = ObjectProperty(None)
    header_label = ObjectProperty(None) # เพิ่ม Label สำหรับ Header

    def on_enter(self):
        # ตั้งชื่อ Header ตามผู้สูงอายุที่เลือก
        elder_name = self.manager.current_elder_name
        if self.header_label:
            self.header_label.text = f"สุขภาพ: {elder_name}"

        self.load_health_records()
        self.setup_filter_dropdown()

    def load_health_records(self, month=None, year=None):
        self.record_list_layout.clear_widgets()
        elder_id = self.manager.current_elder_id

        if not elder_id:
            self.record_list_layout.add_widget(Label(text="กรุณาเลือกผู้สูงอายุก่อน", font_name="THFont"))
            return

        api = ApiClient()
        
        # --- *** จุดที่แก้ไขสำคัญ *** ---
        # เราไม่ต้อง get list ผู้สูงอายุอีกแล้ว เพราะเรารู้ ID จาก self.manager.current_elder_id
        url = f"/health/records/elder/{elder_id}"
        params = []
        if month and year:
            params.append(f"month={month}")
            params.append(f"year={year}")
        if params:
            url += '?' + '&'.join(params)
            
        rec_resp = api.get(url)
        if rec_resp and rec_resp.status_code == 200:
            records = rec_resp.json().get('records', [])
            if not records:
                self.record_list_layout.add_widget(Label(
                    text="ยังไม่มีบันทึกสุขภาพ",
                    font_name="THFont", color=(.5,.5,.5,1)))
            else:
                for rec in records:
                    item = self.create_health_record_item(rec)
                    self.record_list_layout.add_widget(item)
        else:
            self.record_list_layout.add_widget(Label(
                text="โหลดข้อมูลผิดพลาด",
                font_name="THFont", color=(1,0,0,1)))

    def create_health_record_item(self, rec_data):
        # โค้ดส่วนนี้เหมือนเดิมได้เลย
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding='12dp', spacing='8dp')
        container.bind(minimum_height=container.setter('height'))
        header = BoxLayout(size_hint_y=None, height='30dp')
        header.add_widget(Label(text=rec_data.get('recorded_at'), font_name='THFont', font_size='14sp', color=(.5,.5,.5,1), halign='right', text_size=(None, None)))
        container.add_widget(header)
        info_grid = GridLayout(cols=1, spacing='5dp', size_hint_y=None)
        info_grid.bind(minimum_height=info_grid.setter('height'))
        info_grid.add_widget(self.create_info_row('assets/icon_health_active.png', f"บน {rec_data.get('systolic_bp', '-')} มม.ปรอท"))
        info_grid.add_widget(self.create_info_row('assets/icon_health_active.png', f"ล่าง {rec_data.get('diastolic_bp', '-')} มม.ปรอท"))
        info_grid.add_widget(self.create_info_row('assets/icon_weight.png', f"{rec_data.get('weight', '-')} กก."))
        info_grid.add_widget(self.create_info_row('assets/icon_pulse.png', f"{rec_data.get('pulse', '-')} ครั้ง/นาที"))
        info_grid.add_widget(self.create_info_row('assets/icon_note.png', f"{rec_data.get('notes', 'ไม่มีหมายเหตุ')}"))
        container.add_widget(info_grid)
        return container

    def create_info_row(self, icon_source, text):
        # โค้ดส่วนนี้เหมือนเดิมได้เลย
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height='24dp', spacing=4)
        row.add_widget(Image(source=icon_source, size_hint_x=None, width='24dp'))
        label = Label(text=text, font_name="THFont", font_size="14sp", color=(0.2,0.2,0.2,1), halign='left')
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        row.add_widget(label)
        return row

    def setup_filter_dropdown(self):
        # โค้ดส่วนนี้เหมือนเดิมได้เลย
        self.dropdown = DropDown()
        thai_month_abbr = {1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.", 7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."}
        today = datetime.today()
        all_btn = Button(text="แสดงทั้งหมด", size_hint_y=None, height=44, font_name="THFont")
        all_btn.bind(on_release=lambda btn: self.select_month(None, None))
        self.dropdown.add_widget(all_btn)
        month = today.month
        year = today.year
        for i in range(5):
            m, y = (month - i - 1) % 12 + 1, year + (month - i - 1) // 12
            month_str = f"{thai_month_abbr.get(m, '')} {str(y + 543)[2:]}"
            btn = Button(text=month_str, size_hint_y=None, height=44, font_name="THFont")
            btn.bind(on_release=lambda btn, m=m, y=y: self.select_month(m, y))
            self.dropdown.add_widget(btn)
        if self.filter_button:
            self.filter_button.bind(on_release=self.dropdown.open)

    def select_month(self, month, year):
        # โค้ดส่วนนี้เหมือนเดิมได้เลย
        self.load_health_records(month=month, year=year)
        self.dropdown.dismiss()