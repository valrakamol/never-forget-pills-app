# frontend/screens/osm_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from api_client import ApiClient
from widgets.alert_box import AlertBox

class OsmScreen(Screen):
    elder_list_layout = ObjectProperty(None)
    welcome_label = ObjectProperty(None)
    search_input = ObjectProperty(None)
    _managed_elders_cache = [] # Cache สำหรับการค้นหา

    def on_enter(self, *args):
        """
        ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่เข้ามาที่หน้านี้
        """
        self.load_managed_elders()
        if self.search_input:
            self.search_input.text = ""

    def load_managed_elders(self):
        """
        โหลดรายชื่อผู้สูงอายุในความดูแล (Managed Elders) เท่านั้น
        """
        self.elder_list_layout.clear_widgets()
        api = ApiClient()
        # ใช้ Endpoint ที่ดึงเฉพาะผู้สูงอายุที่ผูกกับ อสม. คนนี้
        response = api.get('/users/my_managed_elders')

        if response and response.status_code == 200:
            elders = response.json().get('elders', [])
            self._managed_elders_cache = elders # เก็บข้อมูลไว้ใน Cache สำหรับค้นหา
            self.populate_managed_elders(elders)
        else:
            error_label = Label(text='ไม่สามารถโหลดข้อมูลได้', font_name="THFont", color=(1, 0, 0, 1))
            self.elder_list_layout.add_widget(error_label)

    def populate_managed_elders(self, elders_list):
        """แสดงผลรายชื่อผู้สูงอายุในความดูแล"""
        self.elder_list_layout.clear_widgets()
        if not elders_list:
            no_elder_label = Label(
                text='ยังไม่มีผู้สูงอายุในความดูแล\nกดปุ่ม "+" เพื่อเพิ่ม', 
                font_name="THFont", 
                halign='center',
                color=(0.3, 0.3, 0.3, 1)
            )
            self.elder_list_layout.add_widget(no_elder_label)
        else:
            for elder in elders_list:
                item = self.create_elder_list_item(elder)
                self.elder_list_layout.add_widget(item)

    def create_elder_list_item(self, elder_data):
        """
        สร้าง Widget การ์ด 1 ใบ สำหรับผู้สูงอายุ 1 คน
        พร้อมปุ่มสำหรับดูรายละเอียด และปุ่มยกเลิกการดูแล
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

        # ปุ่มชื่อผู้สูงอายุ (สำหรับกดเข้าไปดูรายละเอียด)
        name_button = Button(
            text=f"{elder_data.get('full_name', 'N/A')}",
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

        # ปุ่มยกเลิกการดูแล
        unlink_button = Button(
            text='ยกเลิก',
            font_name='THFont',
            font_size='16sp',
            size_hint_x=None,
            width='100dp',
            background_normal='',
            background_color=(220/255, 80/255, 80/255, 1), # สีแดง
            color=(1, 1, 1, 1)
        )
        unlink_button.bind(on_release=lambda x, e_id=elder_data.get('id'), e_name=elder_data.get('full_name'): self.confirm_unlink_elder(e_id, e_name))

        card_layout.add_widget(name_button)
        card_layout.add_widget(unlink_button)

        return card_layout

    def filter_elder_list(self, search_text):
        """ค้นหารายชื่อจาก Cache ของผู้สูงอายุที่ดูแลอยู่"""
        search_text = search_text.strip().lower()
        if not search_text:
            filtered_list = self._managed_elders_cache
        else:
            filtered_list = [
                e for e in self._managed_elders_cache
                if search_text in e.get('full_name', '').lower()
            ]
        self.populate_managed_elders(filtered_list)

    def view_elder_details(self, elder_id, elder_name):
        """เมื่อกดที่ชื่อผู้สูงอายุ, จะนำทางไปยังหน้าจอรายละเอียด"""
        self.manager.current_elder_id = elder_id
        self.manager.current_elder_name = elder_name
        self.manager.current = 'osm_elder_detail_screen' 

    def go_to_add_elder_page(self):
        """นำทางไปยังหน้าจอสำหรับ "เพิ่ม" ผู้สูงอายุในความดูแล"""
        self.manager.current = 'osm_add_elder_screen'

    def confirm_unlink_elder(self, elder_id, elder_name):
        """แสดง Popup เพื่อยืนยันการยกเลิกการเชื่อมโยง"""
        def on_confirm(*args):
            self.unlink_elder(elder_id)
        
        alert = AlertBox(
            title="ยืนยันการยกเลิก", 
            message=f"คุณต้องการยกเลิกการดูแล [b]{elder_name}[/b] ใช่หรือไม่?",
            show_cancel_button=True, # แสดงปุ่มยกเลิกใน Popup ด้วย
            on_ok_callback=on_confirm
        )
        alert.open()

    def unlink_elder(self, elder_id):
        """ส่ง request ไปยัง Backend เพื่อยกเลิกการเชื่อมโยง"""
        api = ApiClient()
        response = api.post('/users/unlink_elder', data={'elder_id': elder_id})
        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message="ยกเลิกการดูแลเรียบร้อยแล้ว").open()
            self.load_managed_elders() # รีเฟรชรายการ
        else:
            msg = "ไม่สามารถยกเลิกได้"
            if response:
                try: msg = response.json().get('msg', msg)
                except: pass
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()