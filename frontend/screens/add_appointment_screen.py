from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox
from datetime import date

class AddAppointmentScreen(Screen):
    # เชื่อม Widget จาก .kv
    title_field = ObjectProperty(None)
    doctor_field = ObjectProperty(None)
    location_field = ObjectProperty(None)
    notes_field = ObjectProperty(None)
    day_spinner = ObjectProperty(None)
    month_spinner = ObjectProperty(None)
    year_spinner = ObjectProperty(None)
    time_spinner = ObjectProperty(None)
    
    year_options = ListProperty([])
    
    def on_pre_enter(self, *args):
        """เคลียร์ฟอร์มและตั้งค่าเริ่มต้นให้ Spinner"""
        current_buddhist_year = date.today().year + 543
        self.year_options = [str(y) for y in range(current_buddhist_year, current_buddhist_year + 5)]

        self.title_field.text = ""
        self.doctor_field.text = ""
        self.location_field.text = ""
        self.notes_field.text = ""
        
        self.year_spinner.text = str(current_buddhist_year)
        self.month_spinner.text = "เดือน"
        self.day_spinner.text = "วัน"
        self.time_spinner.text = "เลือกเวลา"

    def save_appointment(self):
        """รวบรวมข้อมูลและส่งไปที่ Backend"""
        elder_id = self.manager.current_elder_id
        
        appointment_date = self.assemble_date(
            self.year_spinner.text, self.month_spinner.text, self.day_spinner.text
        )
        appointment_time = self.time_spinner.text if self.time_spinner.text != "เลือกเวลา" else ""

        # ประกอบร่าง datetime string
        datetime_str = f"{appointment_date} {appointment_time}" if appointment_date and appointment_time else ""

        data = {
            "elder_id": elder_id,
            "title": self.title_field.text.strip(),
            "doctor_name": self.doctor_field.text.strip(),
            "location": self.location_field.text.strip(),
            "appointment_datetime": datetime_str,
            "notes": self.notes_field.text.strip()
        }
        
        if not all([data['title'], data['location'], data['appointment_datetime']]):
            AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกหัวข้อ, สถานที่, และวันเวลาที่นัดหมายให้ครบถ้วน").open()
            return
            
        api = ApiClient()
        response = api.post('/appointments/add', data=data)
        
        if response and response.status_code == 201:
            AlertBox(title="สำเร็จ", message="เพิ่มนัดหมายเรียบร้อยแล้ว", on_ok_callback=self.go_back).open()
        else:
            msg = "ไม่สามารถเพิ่มนัดหมายได้"
            if response:
                try: msg = response.json().get('msg', msg)
                except: pass
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()

    def assemble_date(self, year_buddhist_str, month_str, day_str):
        if year_buddhist_str.isdigit() and "เดือน" not in month_str and "วัน" not in day_str:
            year_ad = int(year_buddhist_str) - 543
            month_map = {"มกราคม": "01", "กุมภาพันธ์": "02", "มีนาคม": "03", "เมษายน": "04", "พฤษภาคม": "05", "มิถุนายน": "06", "กรกฎาคม": "07", "สิงหาคม": "08", "กันยายน": "09", "ตุลาคม": "10", "พฤศจิกายน": "11", "ธันวาคม": "12"}
            month_num = month_map.get(month_str)
            day_num = f"{int(day_str):02d}"
            return f"{year_ad}-{month_num}-{day_num}"
        return None

    def go_back(self, *args):
        self.manager.current = 'elder_detail_screen'