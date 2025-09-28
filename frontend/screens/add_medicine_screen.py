# frontend/screens/add_medicine_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox
from datetime import date
from kivy.clock import Clock

class AddMedicineScreen(Screen):
    # --- Properties สำหรับเชื่อม Widget ---
    name_spinner = ObjectProperty(None)
    dosage_value_input = ObjectProperty(None)
    dosage_unit_spinner = ObjectProperty(None)
    meal_spinner = ObjectProperty(None)
    time_morning = ObjectProperty(None)
    time_noon = ObjectProperty(None)
    time_evening = ObjectProperty(None)
    time_bedtime = ObjectProperty(None)
    start_day_spinner = ObjectProperty(None)
    start_month_spinner = ObjectProperty(None)
    start_year_spinner = ObjectProperty(None)
    end_day_spinner = ObjectProperty(None)
    end_month_spinner = ObjectProperty(None)
    end_year_spinner = ObjectProperty(None)
    
    # --- Properties สำหรับเก็บข้อมูล ---
    master_medicine_list = ListProperty([])
    medicine_names = ListProperty([])
    year_options = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ผูก Event หลังจากที่ Widget ถูกสร้างเสร็จแล้ว
        Clock.schedule_once(self.bind_spinner_event)

    def bind_spinner_event(self, dt):
        """ผูก Event ให้กับ name_spinner"""
        if self.name_spinner:
            self.name_spinner.bind(text=self.on_medicine_selected)

    def on_pre_enter(self, *args):
        """เคลียร์ฟอร์มและโหลดข้อมูลเมื่อเข้ามาหน้านี้"""
        self.load_master_medicines()
        
        today = date.today()
        current_buddhist_year = today.year + 543
        self.year_options = [str(y) for y in range(current_buddhist_year, current_buddhist_year + 5)]

        self.name_spinner.text = "เลือกชื่อยา"
        self.dosage_value_input.text = ""
        self.dosage_unit_spinner.text = "หน่วย"
        self.meal_spinner.text = "เลือกมื้ออาหาร"
    
        self.time_morning.active = False
        self.time_noon.active = False
        self.time_evening.active = False
        self.time_bedtime.active = False

        month_map_th = {
            1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
            5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
            9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
        }
        self.start_year_spinner.text = str(current_buddhist_year)
        self.start_month_spinner.text = month_map_th.get(today.month, "เดือน")
        self.start_day_spinner.text = str(today.day)
    
        self.end_year_spinner.text = str(current_buddhist_year)
        self.end_month_spinner.text = "เดือน"
        self.end_day_spinner.text = "วัน"
        
    def load_master_medicines(self):
        """ดึงรายชื่อยาหลักจาก API"""
        api = ApiClient()
        response = api.get('/medicines/master_list')
        if response and response.status_code == 200:
            self.master_medicine_list = response.json().get('medicines', [])
            self.medicine_names = [med['name'] for med in self.master_medicine_list]
        else:
            self.master_medicine_list = []
            self.medicine_names = ["ไม่สามารถโหลดข้อมูลยาได้"]

    # --- *** นี่คือฟังก์ชันที่หายไป *** ---
    def on_medicine_selected(self, spinner, text):
        """
        ทำงานเมื่อผู้ใช้เลือกยาจาก Spinner เพื่อตั้งค่าหน่วยยาอัตโนมัติ
        """
        if text == "เลือกชื่อยา" or "ไม่สามารถโหลด" in text:
            # รีเซ็ตฟอร์มถ้าผู้ใช้เลือกค่าเริ่มต้น
            self.dosage_unit_spinner.text = "หน่วย"
            self.dosage_value_input.text = ""
            return
        
        selected_med_form = None
        for med in self.master_medicine_list:
            if med['name'] == text:
                selected_med_form = med.get('form')
                break
        
        if selected_med_form:
            # --- *** จุดที่แก้ไขสำคัญ: ทำให้ Logic ยืดหยุ่นขึ้น *** ---
            
            # 1. ตรวจสอบว่า "form" ที่ได้มา มีอยู่ใน "values" ของ Spinner หรือไม่
            if selected_med_form in self.dosage_unit_spinner.values:
                # ถ้ามี ให้ตั้งค่า Spinner เป็นค่านั้นโดยตรง
                self.dosage_unit_spinner.text = selected_med_form
            else:
                # ถ้าไม่มี (เช่น "ผง", "อื่นๆ") ให้ตั้งเป็นค่าเริ่มต้น
                self.dosage_unit_spinner.text = "หน่วย"

            # 2. ตั้งค่าปริมาณเริ่มต้น (อาจจะตั้งเป็น 1 สำหรับทุกกรณี)
            self.dosage_value_input.text = "1"
            
        else:
            # กรณีที่ไม่พบข้อมูล form (ไม่ควรเกิดขึ้น)
            self.dosage_unit_spinner.text = "หน่วย"
            self.dosage_value_input.text = ""

    def save_medicine(self):
        """รวบรวมข้อมูลและส่งไป Backend"""
        medicine_name = self.name_spinner.text
        if medicine_name == "เลือกชื่อยา" or "ไม่สามารถโหลด" in medicine_name:
            AlertBox(title="ข้อมูลไม่ครบ", message="กรุณาเลือกชื่อยา").open()
            return

        dosage_value = self.dosage_value_input.text.strip()
        dosage_unit = self.dosage_unit_spinner.text if self.dosage_unit_spinner.text != "หน่วย" else ""
        full_dosage = f"{dosage_value} {dosage_unit}".strip() if dosage_value and dosage_unit else ""
        
        meal_val = self.meal_spinner.text if self.meal_spinner.text != "เลือกมื้ออาหาร" else ""
        
        start_date = self.assemble_date(self.start_year_spinner.text, self.start_month_spinner.text, self.start_day_spinner.text)
        end_date = self.assemble_date(self.end_year_spinner.text, self.end_month_spinner.text, self.end_day_spinner.text)
        
        selected_times = []
        if self.time_morning.active:
            selected_times.append("08:00")
        if self.time_noon.active:
            selected_times.append("12:00")
        if self.time_evening.active:
            selected_times.append("18:00")
        if self.time_bedtime.active:
            selected_times.append("21:00")
        
        data = {
            "elder_id": self.manager.current_elder_id,
            "name": medicine_name,
            "dosage": full_dosage,
            "meal_instruction": meal_val,
            "times_to_take": selected_times,
            "start_date": start_date,
            "end_date": end_date,
        }
        
        if not all([data['name'], data['times_to_take'], data['start_date']]):
            AlertBox(title="ข้อมูลไม่ครบ", message="กรุณาเลือกชื่อยา, เลือกเวลาอย่างน้อย 1 เวลา, และวันที่เริ่มให้ครบถ้วน").open()
            return
            
        api = ApiClient()
        response = api.post('/medicines/add', data=data)
        
        if response and response.status_code == 201:
            AlertBox(title="สำเร็จ", message="เพิ่มรายการยาเรียบร้อยแล้ว", on_ok_callback=self.go_back).open()
        else:
            msg = "ไม่สามารถเพิ่มยาได้"
            if response:
                try: msg = response.json().get('msg', msg)
                except: pass
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()

    def assemble_date(self, year_buddhist_str, month_str, day_str):
        if year_buddhist_str.isdigit() and "เดือน" not in month_str and "วัน" not in day_str:
            year_ad = int(year_buddhist_str) - 543
            month_map = { "มกราคม": "01", "กุมภาพันธ์": "02", "มีนาคม": "03", "เมษายน": "04", "พฤษภาคม": "05", "มิถุนายน": "06", "กรกฎาคม": "07", "สิงหาคม": "08", "กันยายน": "09", "ตุลาคม": "10", "พฤศจิกายน": "11", "ธันวาคม": "12" }
            month_num = month_map.get(month_str)
            day_num = f"{int(day_str):02d}"
            return f"{year_ad}-{month_num}-{day_num}"
        return None

    def go_back(self, *args):
        self.manager.current = 'medicine_list_screen'