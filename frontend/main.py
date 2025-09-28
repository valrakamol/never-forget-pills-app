
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.core.text import LabelBase
from kivy.config import Config

# --- 1. ตั้งค่าฟอนต์ ---
main_dir = os.path.dirname(__file__)
font_path = os.path.join(main_dir, 'fonts', 'NotoSansThai-Regular.ttf')
LabelBase.register(name="THFont", fn_regular=font_path)
Config.set('kivy', 'default_font', ['THFont', 'Roboto', 'DejaVuSans', 'Arial'])

# --- 2. Import ที่จำเป็น ---
from api_client import ensure_user_data_file_exists, get_stored_auth_info, ApiClient
from screens.role_select_screen import RoleSelectScreen
from screens.login_screen import LoginScreen
from screens.elder_login_screen import ElderLoginScreen
from screens.register_screen import RegisterScreen
from screens.caregiver_screen import CaregiverScreen
from screens.add_elder_screen import AddElderScreen
from screens.elder_detail_screen import ElderDetailScreen
from screens.add_medicine_screen import AddMedicineScreen
from screens.add_appointment_screen import AddAppointmentScreen

from screens.osm_screen import OsmScreen
from screens.add_elder_volunteer_screen import AddElderVolunteerScreen
from screens.edit_health_screen import EditHealthScreen
from screens.osm_summary_screen import OsmSummaryScreen
from screens.caregiver_profile_screen import CaregiverProfileScreen
from screens.medicine_list_screen import MedicineListScreen
from screens.appointment_list_screen import AppointmentListScreen
from screens.elder_medicine_screen import ElderMedicineScreen
from screens.elder_profile_screen import ElderProfileScreen
from screens.elder_appointment_screen import ElderAppointmentScreen  
from screens.osm_profile_screen import OsmProfileScreen   
from screens.osm_elder_detail_screen import OsmElderDetailScreen   
from screens.health_record_screen import HealthRecordScreen    
from screens.elder_health_record_screen import ElderHealthRecordScreen
from screens.caregiver_health_record_screen import CaregiverHealthRecordScreen
from screens.edit_appointment_screen import EditAppointmentScreen
from screens.osm_add_elder_screen import OsmAddElderScreen

class WindowManager(ScreenManager):
    current_elder_id = NumericProperty(None)
    current_elder_name = StringProperty(None)
    current_appointment_data = ObjectProperty(None) 
    current_caregiver_name = StringProperty('')  # เพิ่มบรรทัดนี้

class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kv_file = None

    def build(self):
        kv_path = os.path.join(os.path.dirname(__file__), 'kv')
        kv_files_to_load = [
            'widgets.kv', 'role_select_screen.kv', 'login_screen.kv', 
            'elder_login_screen.kv', 'register_screen.kv', 'caregiver_screen.kv',
            'add_elder_screen.kv', 'elder_detail_screen.kv', 'add_medicine_screen.kv',
            'add_appointment_screen.kv', 'caregiver_health_record_screen.kv',
            'osm_screen.kv', 'add_elder_volunteer_screen.kv', 'edit_health_screen.kv',
            'osm_summary_screen.kv', 'caregiver_profile_screen.kv','medicine_list_screen.kv',
            'appointment_list_screen.kv', 'elder_medicine_screen.kv', 'elder_profile_screen.kv', 
            'elder_appointment_screen.kv', 'osm_profile_screen.kv', 'osm_elder_detail_screen.kv',
            'health_record_screen.kv', 'elder_health_record_screen.kv', 'edit_appointment_screen.kv',
            'osm_add_elder_screen.kv',
        ]
        for kv_file in kv_files_to_load:
            Builder.load_file(os.path.join(kv_path, kv_file))
        
        sm = WindowManager()
        sm.add_widget(RoleSelectScreen(name='role_select_screen'))
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(ElderLoginScreen(name='elder_login_screen'))
        sm.add_widget(RegisterScreen(name='register_screen'))
        sm.add_widget(CaregiverScreen(name='caregiver_screen'))
        sm.add_widget(CaregiverHealthRecordScreen(name='caregiver_health_record_screen'))
        sm.add_widget(AddElderScreen(name='add_elder_screen'))
        sm.add_widget(ElderDetailScreen(name='elder_detail_screen'))
        sm.add_widget(AddMedicineScreen(name='add_medicine_screen'))
        sm.add_widget(AddAppointmentScreen(name='add_appointment_screen'))
        sm.add_widget(OsmScreen(name='osm_screen'))
        sm.add_widget(AddElderVolunteerScreen(name='add_elder_volunteer_screen'))
        sm.add_widget(EditHealthScreen(name='edit_health_screen'))
        sm.add_widget(EditAppointmentScreen(name='edit_appointment_screen'))
        sm.add_widget(OsmSummaryScreen(name='osm_summary_screen'))
        sm.add_widget(OsmAddElderScreen(name='osm_add_elder_screen'))
        sm.add_widget(CaregiverProfileScreen(name='caregiver_profile_screen'))  
        sm.add_widget(MedicineListScreen(name='medicine_list_screen'))
        sm.add_widget(AppointmentListScreen(name='appointment_list_screen'))
        sm.add_widget(ElderMedicineScreen(name='elder_medicine_screen'))
        sm.add_widget(ElderProfileScreen(name='elder_profile_screen'))
        sm.add_widget(ElderAppointmentScreen(name='elder_appointment_screen'))
        sm.add_widget(OsmProfileScreen(name='osm_profile_screen'))
        sm.add_widget(OsmElderDetailScreen(name='osm_elder_detail_screen'))
        sm.add_widget(HealthRecordScreen(name='health_record_screen'))
        sm.add_widget(ElderHealthRecordScreen(name='elder_health_record_screen'))
        
        return sm
        
    def on_start(self):
        ensure_user_data_file_exists()
        if platform not in ('android', 'ios'):
            Window.size = (400, 750)
        self.check_persistent_login()
        self.init_fcm()
    
    def check_persistent_login(self):
        auth_info = get_stored_auth_info()
        if auth_info:
            role = auth_info.get('user_info', {}).get('role')
            if role == 'caregiver': 
                self.root.current = 'caregiver_screen' # <-- ไปหน้ารายชื่อ
            elif role in ['osm', 'volunteer']: 
                self.root.current = 'osm_screen' # <-- ไปหน้ารายชื่อ
            elif role == 'elder': 
                self.root.current = 'elder_medicine_screen' 
            else: 
                self.go_to_login_flow()
        else:
            self.go_to_login_flow()

    def go_to_login_flow(self):
        self.root.current = 'role_select_screen'
    
    def init_fcm(self):
        if platform not in ('android', 'ios'):
            print("FCM is not supported on this platform. Skipping FCM setup.")
            return
        try:
            from plyer import fcm
            fcm.start()
            fcm.fcm_token
            fcm.bind(on_fcm_token=self.on_fcm_token_received)
            fcm.bind(on_fcm_message=self.on_fcm_message_received)
            print("FCM service started and events bound.")
        except Exception as e:
            print(f"Failed to initialize FCM: {e}")

    @mainthread
    def on_fcm_token_received(self, token, *args):
        """Callback เมื่อได้รับ FCM token ใหม่"""
        print(f"FCM Token Received: {token}")
        if get_stored_auth_info():
            api = ApiClient()
            api.post('/users/register_fcm', data={'fcm_token': token})

    @mainthread
    def on_fcm_message_received(self, message, *args):
        """Callback เมื่อได้รับ Push Notification"""
        from plyer import notification
        title = message.get('notification', {}).get('title', 'การแจ้งเตือนใหม่')
        body = message.get('notification', {}).get('body', '')
        notification.notify(title=title, message=body)

if __name__ == '__main__':
    MainApp().run()