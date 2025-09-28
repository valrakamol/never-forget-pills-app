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

class ElderHealthRecordScreen(Screen):
    record_list_layout = ObjectProperty(None)
    filter_button = ObjectProperty(None)  # เพิ่ม property สำหรับปุ่ม filter

    def on_enter(self):
        self.load_health_records()
        self.setup_filter_dropdown()

    def load_health_records(self, month=None, year=None):
        self.record_list_layout.clear_widgets()
        api = ApiClient()
        # ดึงข้อมูลผู้สูงอายุของตัวเอง (มีแค่ 1 คน)
        elders_resp = api.get('/users/my_managed_elders')
        if not elders_resp or elders_resp.status_code != 200:
            self.record_list_layout.add_widget(Label(
                text="ไม่สามารถโหลดรายชื่อผู้สูงอายุได้",
                font_name="THFont", color=(1,0,0,1)))
            return
        elders = elders_resp.json().get('elders', [])
        if not elders:
            self.record_list_layout.add_widget(Label(
                text="ยังไม่มีผู้สูงอายุในความดูแล",
                font_name="THFont", color=(0,0,0,1)))
            return
        for elder in elders:
            # --- เพิ่ม query string สำหรับกรองเดือน/ปี ---
            url = f"/health/records/elder/{elder['id']}"
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
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding='12dp', spacing='8dp')
        container.bind(minimum_height=container.setter('height'))
        header = BoxLayout(size_hint_y=None, height='30dp')
        header.add_widget(Label(text=rec_data.get('recorded_at'), font_name='THFont', font_size='14sp', color=(.5,.5,.5,1), halign='right', text_size=(None, None)))
        container.add_widget(header)
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
            month_str = f"{thai_month_abbr.get(m, '')} {str(y + 543)[2:]}"
            btn = Button(text=month_str, size_hint_y=None, height=44, font_name="THFont")
            btn.bind(on_release=lambda btn, m=m, y=y: self.select_month(m, y))
            self.dropdown.add_widget(btn)

        if self.filter_button:
            self.filter_button.bind(on_release=self.dropdown.open)

    def select_month(self, month, year):
        self.load_health_records(month=month, year=year)
        self.dropdown.dismiss()