# frontend/caregiver_screen.py (หรือไฟล์ Python ที่เกี่ยวข้อง)
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from api_client import ApiClient, clear_auth_token
from widgets.alert_box import AlertBox

class CaregiverScreen(Screen):
    elder_list_layout = ObjectProperty(None)
    
    def on_enter(self, *args):
        self.load_managed_elders()

    def load_managed_elders(self):
        """
        โหลดรายชื่อผู้สูงอายุในความดูแลและแสดงผลด้วยการ์ดดีไซน์ใหม่
        """
        self.elder_list_layout.clear_widgets()
        api = ApiClient()
        response = api.get('/users/my_managed_elders')

        if response and response.status_code == 200:
            elders = response.json().get('elders', [])
            if not elders:
                no_elder_label = Label(
                    text='ยังไม่มีผู้สูงอายุในความดูแล', 
                    font_name="THFont", 
                    halign='center',
                    color=(0,0,0,1)
                )
                self.elder_list_layout.add_widget(no_elder_label)
            else:
                for elder in elders:
                    # เรียกใช้ฟังก์ชันใหม่เพื่อสร้างการ์ด
                    card = self.create_elder_card(elder)
                    self.elder_list_layout.add_widget(card)
        else:
            error_label = Label(text='ไม่สามารถโหลดข้อมูลได้', font_name="THFont", color=(1, 0, 0, 1))
            self.elder_list_layout.add_widget(error_label)

    def create_elder_card(self, elder_data):
        """
        ฟังก์ชันสำหรับสร้าง Widget การ์ด 1 ใบ พร้อมปุ่มลบแบบข้อความ
        """
        card_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='64dp',
            padding=['12dp', '8dp', '12dp', '8dp'], 
            spacing='12dp'
        )
        with card_layout.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(rgba=(1, 1, 1, 1)) 
            rect = RoundedRectangle(pos=card_layout.pos, size=card_layout.size, radius=[16,])

        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        card_layout.bind(pos=update_rect, size=update_rect)

        # ปุ่มชื่อผู้สูงอายุ
        name_button = Button(
            text=f"ชื่อ: {elder_data.get('full_name', 'N/A')}",
            font_name='THFont',
            font_size='18sp',
            color=(0,0,0,1),
            halign='left',
            valign='middle',
            background_color=(0,0,0,0),
            background_normal=''
        )
        name_button.bind(size=name_button.setter('text_size'))
        name_button.bind(on_release=lambda x, e_id=elder_data.get('id'), e_name=elder_data.get('full_name'): self.view_elder_details(e_id, e_name))

        # ปุ่มลบ (เปลี่ยนเป็นปุ่มข้อความธรรมดา)
        delete_button = Button(
            text='ลบ',
            font_name='THFont',
            font_size='16sp',
            size_hint_x=None,
            width='50dp',
            background_normal='',
            background_color=(220/255, 50/255, 50/255, 1), # สีแดง
            color=(1, 1, 1, 1) # สีขาว
        )
        delete_button.bind(on_release=lambda x, e_id=elder_data.get('id'), e_name=elder_data.get('full_name'): self.confirm_delete_elder(e_id, e_name))

        # --- ลำดับการเพิ่มที่ถูกต้อง ---
        card_layout.add_widget(name_button)   # เพิ่มชื่อก่อน
        card_layout.add_widget(delete_button) # เพิ่มปุ่มลบทีหลัง

        return card_layout

    def view_elder_details(self, elder_id, elder_name):
        self.manager.current_elder_id = elder_id
        self.manager.current_elder_name = elder_name
        self.manager.current = 'elder_detail_screen' 

    def go_to_add_elder(self):
        self.manager.current = 'add_elder_screen'
    
    def switch_to_caregiver_screen(self):
        self.manager.current = 'caregiver_screen'
    
    def go_to_caregiver_profile(self):
        self.manager.current = 'caregiver_profile_screen'

    def confirm_delete_elder(self, elder_id, elder_name):
        def on_confirm(*args):
            self.delete_elder(elder_id)
        alert = AlertBox(title="ยืนยันการยกเลิก", message=f"คุณต้องการยกเลิกการดูแล [b]{elder_name}[/b] ใช่หรือไม่?", on_ok_callback=on_confirm)
        alert.open()

    def delete_elder(self, elder_id):
        api = ApiClient()
        response = api.post('/users/unlink_elder', data={'elder_id': elder_id})
        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message="ยกเลิกการดูแลเรียบร้อยแล้ว").open()
            self.load_managed_elders()
        else:
            msg = "ไม่สามารถยกเลิกการดูแลได้"
            if response:
                try: msg = response.json().get('msg', msg)
                except: pass
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()