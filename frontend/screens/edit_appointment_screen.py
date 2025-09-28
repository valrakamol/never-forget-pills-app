# frontend/screens/edit_appointment_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox
from datetime import datetime

class EditAppointmentScreen(Screen):
    # เชื่อม Widget จาก .kv (เหมือนหน้า Add)
    title_field = ObjectProperty(None)
    doctor_field = ObjectProperty(None)
    location_field = ObjectProperty(None)
    notes_field = ObjectProperty(None)
    day_spinner = ObjectProperty(None)
    month_spinner = ObjectProperty(None)
    year_spinner = ObjectProperty(None)
    time_spinner = ObjectProperty(None)
    
    year_options = ListProperty([])
    appointment_id_to_edit = None

    def on_pre_enter(self, *args):
        """
        ฟังก์ชันนี้จะถูกเรียกก่อนที่หน้าจอจะแสดง
        ทำหน้าที่โหลดข้อมูลนัดหมายเดิมมาใส่ในฟอร์ม
        """
        # 1. ดึงข้อมูลนัดหมายที่จะแก้ไขจาก ScreenManager
        app_data = self.manager.current_appointment_data
        if not app_data:
            self.go_back() # ถ้าไม่มีข้อมูล ให้กลับไปเลย
            return

        self.appointment_id_to_edit = app_data.get('id')

        # 2. ตั้งค่าปี พ.ศ. สำหรับ Spinner
        current_buddhist_year = datetime.now().year + 543
        self.year_options = [str(y) for y in range(current_buddhist_year, current_buddhist_year + 5)]

        # 3. เติมข้อมูลลงในฟอร์ม
        self.title_field.text = app_data.get('title', '')
        self.doctor_field.text = app_data.get('doctor', '')
        self.location_field.text = app_data.get('location', '')
        self.notes_field.text = app_data.get('notes', '')

        # 4. แยกและตั้งค่าวันที่และเวลาใน Spinner
        full_datetime_str = app_data.get('datetime', '')
        if full_datetime_str:
            try:
                dt_obj = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M')
                month_map_th = {
                    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
                    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
                    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
                }
                self.year_spinner.text = str(dt_obj.year + 543)
                self.month_spinner.text = month_map_th.get(dt_obj.month, "เดือน")
                self.day_spinner.text = str(dt_obj.day)
                self.time_spinner.text = dt_obj.strftime('%H:%M')
            except ValueError:
                self.reset_date_spinners()
        else:
            self.reset_date_spinners()

    def reset_date_spinners(self):
        current_buddhist_year = datetime.now().year + 543
        self.year_spinner.text = str(current_buddhist_year)
        self.month_spinner.text = "เดือน"
        self.day_spinner.text = "วัน"
        self.time_spinner.text = "เลือกเวลา"

    def save_changes(self):
        """รวบรวมข้อมูลและส่งไปอัปเดตที่ Backend"""
        if not self.appointment_id_to_edit:
            return

        appointment_date = self.assemble_date(self.year_spinner.text, self.month_spinner.text, self.day_spinner.text)
        appointment_time = self.time_spinner.text if self.time_spinner.text != "เลือกเวลา" else ""
        datetime_str = f"{appointment_date} {appointment_time}" if appointment_date and appointment_time else ""

        data = {
            "title": self.title_field.text.strip(),
            "doctor_name": self.doctor_field.text.strip(),
            "location": self.location_field.text.strip(),
            "appointment_datetime": datetime_str,
            "notes": self.notes_field.text.strip()
        }
        
        if not all([data['title'], data['location'], data['appointment_datetime']]):
            AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกหัวข้อ, สถานที่, และวันเวลาให้ครบถ้วน").open()
            return
            
        api = ApiClient()
        # เรียก Endpoint ใหม่สำหรับอัปเดต
        response = api.post(f'/appointments/update/{self.appointment_id_to_edit}', data=data)
        
        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message="แก้ไขนัดหมายเรียบร้อยแล้ว", on_ok_callback=self.go_back).open()
        else:
            msg = "ไม่สามารถแก้ไขนัดหมายได้"
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
        # กลับไปหน้ารายการนัดหมายของผู้ดูแล
        self.manager.current = 'appointment_list_screen'