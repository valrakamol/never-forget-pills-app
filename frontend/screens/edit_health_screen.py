from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from api_client import ApiClient
from widgets.alert_box import AlertBox
# Import Label ที่นี่ เพื่อให้ฟังก์ชันอื่นใช้ได้ (ถ้าจำเป็น)
from kivy.uix.label import Label 

class EditHealthScreen(Screen):
    # เชื่อม Widget จากไฟล์ .kv เข้ากับโค้ด Python
    header_label = ObjectProperty(None)
    systolic_input = ObjectProperty(None)
    diastolic_input = ObjectProperty(None)
    weight_input = ObjectProperty(None)
    pulse_input = ObjectProperty(None)
    notes_input = ObjectProperty(None)

    def on_pre_enter(self, *args):
        """
        ฟังก์ชันนี้จะถูกเรียก "ก่อน" ที่หน้าจอจะแสดงผล
        เหมาะสำหรับการเตรียมข้อมูลและ UI
        """
        # 1. ดึงข้อมูลผู้สูงอายุที่ถูกส่งมาจากหน้า Dashboard
        elder_name = self.manager.current_elder_name
        
        # 2. อัปเดต Label Header โดยใช้ ObjectProperty ที่เชื่อมไว้
        if self.header_label:
            self.header_label.text = f"บันทึกข้อมูล: {elder_name}"
        
        # 3. เคลียร์ข้อมูลเก่าในฟอร์มทั้งหมด
        if self.systolic_input: self.systolic_input.text = ""
        if self.diastolic_input: self.diastolic_input.text = ""
        if self.weight_input: self.weight_input.text = ""
        if self.pulse_input: self.pulse_input.text = ""
        if self.notes_input: self.notes_input.text = ""

    def save_health_data(self):
        """
        รวบรวมข้อมูลจากฟอร์ม, ตรวจสอบ, และส่งไปบันทึกที่ Backend
        """
        elder_id = self.manager.current_elder_id
        
        systolic_val = self.systolic_input.text.strip()
        diastolic_val = self.diastolic_input.text.strip()
        weight_val = self.weight_input.text.strip()
        pulse_val = self.pulse_input.text.strip()
        notes_val = self.notes_input.text.strip()

        # Input Validation: ตรวจสอบว่าค่าที่กรอกเป็นตัวเลข
        try:
            # แปลงเป็นตัวเลข ถ้าแปลงไม่ได้จะเกิด ValueError
            # อนุญาตให้บางช่องว่างได้ โดยจะถูกแปลงเป็น None
            systolic = int(systolic_val) if systolic_val else None
            diastolic = int(diastolic_val) if diastolic_val else None
            weight = float(weight_val) if weight_val else None
            pulse = int(pulse_val) if pulse_val else None
        except ValueError:
            alert = AlertBox(title="ข้อมูลผิดพลาด", message="กรุณากรอกค่าความดัน, น้ำหนัก และชีพจรเป็นตัวเลขเท่านั้น")
            alert.open()
            return

        # ตรวจสอบว่ามีการกรอกข้อมูลมาอย่างน้อย 1 อย่าง
        if not any([systolic, diastolic, weight, pulse, notes_val]):
            alert = AlertBox(title="ข้อมูลไม่ครบ", message="กรุณากรอกข้อมูลสุขภาพอย่างน้อย 1 อย่าง")
            alert.open()
            return
            
        data_to_send = {
            "elder_id": elder_id, 
            "systolic_bp": systolic, 
            "diastolic_bp": diastolic, 
            "weight": weight, 
            "pulse": pulse,
            "notes": notes_val
        }
        
        api = ApiClient()
        response = api.post('/health/record/add', data=data_to_send)
        
        if response and response.status_code == 201:
            # กรณีบันทึกสำเร็จ
            def on_success_close(*args):
                self.go_back()
            
            alert = AlertBox(
                title="สำเร็จ", 
                message="บันทึกข้อมูลสุขภาพเรียบร้อยแล้ว", 
                on_ok_callback=on_success_close
            )
            alert.open()
        else:
            # กรณีเกิดข้อผิดพลาดจาก Backend
            try:
                error_msg = response.json().get('msg', 'เกิดข้อผิดพลาดที่ไม่รู้จัก')
            except:
                error_msg = "เกิดข้อผิดพลาดจากเซิร์ฟเวอร์"
            alert = AlertBox(title="บันทึกล้มเหลว", message=error_msg)
            alert.open()

    def go_back(self):
        """
        นำทางกลับไปยังหน้า Dashboard ของ อสม.
        """
        self.manager.current = 'health_record_screen'