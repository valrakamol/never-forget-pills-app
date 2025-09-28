# frontend/screens/osm_add_elder_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from api_client import ApiClient
from widgets.alert_box import AlertBox

class OsmAddElderScreen(Screen):
    all_elders_layout = ObjectProperty(None)
    search_input = ObjectProperty(None)
    _all_elders_cache = []

    def on_enter(self):
        self.load_all_elders()

    def load_all_elders(self):
        self.all_elders_layout.clear_widgets()
        api = ApiClient()
        response = api.get('/users/all_elders')

        if response and response.status_code == 200:
            self._all_elders_cache = response.json().get('elders', [])
            self.populate_elder_list(self._all_elders_cache)
        else:
            self.all_elders_layout.add_widget(Label(text="ไม่สามารถโหลดข้อมูลได้", font_name="THFont"))

    def populate_elder_list(self, elders_list):
        self.all_elders_layout.clear_widgets()
        if not elders_list:
            self.all_elders_layout.add_widget(Label(text="ไม่พบผู้สูงอายุ", font_name="THFont"))
            return
        
        for elder in elders_list:
            item = self.create_elder_item(elder)
            self.all_elders_layout.add_widget(item)

    def create_elder_item(self, elder_data):
        card_layout = BoxLayout(
            size_hint_y=None,
            height='64dp',
            padding=['12dp', '8dp', '12dp', '8dp'], 
            spacing='12dp'
        )
        with card_layout.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(rgba=(1, 1, 1, 1)) # สีพื้นหลังขาว
            self.rect = RoundedRectangle(pos=card_layout.pos, size=card_layout.size, radius=[16,])

        def update_rect(instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
        card_layout.bind(pos=update_rect, size=update_rect)

        name_label = Label(
            text=elder_data.get('full_name', 'N/A'), 
            font_name="THFont",
            font_size='18sp',
            color=(0, 0, 0, 1), # <-- สีดำ
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))

        link_button = Button(
            text="เชื่อมโยง", 
            font_name="THFont", 
            size_hint_x=None, 
            width='120dp',
            background_normal='',
            background_color=(0.4, 0.4, 0.4, 1) # สีเทาเข้ม
        )
        link_button.bind(on_release=lambda x, e_id=elder_data.get('id'), e_name=elder_data.get('full_name'): self.confirm_link_elder(e_id, e_name))

        card_layout.add_widget(name_label)
        card_layout.add_widget(link_button)
        return card_layout

    def confirm_link_elder(self, elder_id, elder_name):
        """เพิ่ม Popup ยืนยันก่อนเชื่อมโยง"""
        def on_confirm(*args):
            self.link_elder(elder_id)
        
        alert = AlertBox(
            title="ยืนยันการเชื่อมโยง",
            message=f"ต้องการเพิ่ม [b]{elder_name}[/b] เข้าสู่การดูแลใช่หรือไม่?",
            show_cancel_button=True,
            on_ok_callback=on_confirm
        )
        alert.open()

    def link_elder(self, elder_id):
        api = ApiClient()
        response = api.post('/users/link_elder_by_id', data={'elder_id': elder_id})
        
        if response and response.status_code == 200:
            AlertBox(title="สำเร็จ", message="เชื่อมโยงเรียบร้อยแล้ว").open()
        else:
            msg = "ไม่สามารถเชื่อมโยงได้"
            if response:
                try: msg = response.json().get('msg', msg)
                except: pass
            AlertBox(title="เกิดข้อผิดพลาด", message=msg).open()

    def filter_elders(self, search_text):
        search_text = search_text.strip().lower()
        if not search_text:
            filtered_list = self._all_elders_cache
        else:
            filtered_list = [
                e for e in self._all_elders_cache
                if search_text in e.get('full_name', '').lower()
            ]
        self.populate_elder_list(filtered_list)

    def go_back(self):
        self.manager.current = 'osm_screen'