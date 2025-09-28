# frontend/widgets/medicine_list_item.py
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty

class MedicineListItem(BoxLayout):
    """
    การ์ดสำหรับแสดงข้อมูลยา 1 รายการ
    """
    med_id = NumericProperty(0)
    med_name = StringProperty('')
    med_time = StringProperty('')
    med_dosage = StringProperty('')
    med_meal = StringProperty('')
    med_status = StringProperty('') # 'กินแล้ว' หรือ 'ยังไม่กิน'
    med_image_url = StringProperty('') # URL ของรูปภาพยา

    image_source = StringProperty('assets/image_placeholder.png')
    
    # Callback สำหรับปุ่มลบ
    on_delete_callback = ObjectProperty(None)

    def trigger_delete(self):
        """
        ฟังก์ชันนี้จะถูกเรียกเมื่อกดปุ่มลบ
        """
        if self.on_delete_callback:
            self.on_delete_callback(self.med_id, self.med_name)