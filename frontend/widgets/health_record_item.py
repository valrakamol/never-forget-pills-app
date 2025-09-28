from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
class HealthRecordItem(BoxLayout):
    record_id = NumericProperty(0)
    record_title = StringProperty('ตรวจสุขภาพ')
    record_date = StringProperty('')
    systolic_bp = StringProperty('-')
    diastolic_bp = StringProperty('-')
    weight = StringProperty('-')
    pulse = StringProperty('-') # สมมติว่ามีข้อมูลชีพจร
    notes = StringProperty('')