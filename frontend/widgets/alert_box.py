# frontend/widgets/alert_box.py
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty

class AlertBox(Popup):
    def __init__(self, title='', message='', ok_text='ตกลง', 
                 cancel_text='ยกเลิก', show_cancel_button=False, 
                 on_ok_callback=None, on_cancel_callback=None, **kwargs):
        
        super().__init__(**kwargs)

        # ตั้งค่าพื้นฐานของ Popup
        self.size_hint = (0.85, None)
        self.height = '220dp'
        self.auto_dismiss = False
        self.title = '' # เราจะสร้าง Title ของเราเอง
        self.separator_height = 0
        self.background = ''
        self.background_color = (0.15, 0.15, 0.15, 0.95)

        # --- สร้าง Content ทั้งหมดด้วย Python ---
        # 1. สร้าง Layout หลัก
        main_layout = BoxLayout(orientation='vertical', padding='20dp', spacing='15dp')

        # 2. สร้าง Label Title
        title_label = Label(
            text=title,
            font_name='THFont',
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height='30dp',
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(title_label)
        
        # 3. สร้าง Label Message
        message_label = Label(
            text=message,
            font_name='THFont',
            font_size='16sp',
            halign='center',
            valign='top',
            markup=True,
            color=(.9, .9, .9, 1)
        )
        message_label.bind(size=message_label.setter('text_size'))
        main_layout.add_widget(message_label)

        # 4. สร้าง Layout สำหรับปุ่ม
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp', spacing='10dp')

        # 5. สร้างปุ่ม "ยกเลิก" (ถ้าต้องการ)
        if show_cancel_button:
            cancel_button = Button(
                text=cancel_text,
                font_name='THFont',
                font_size='16sp',
                background_color=(0.6, 0.6, 0.6, 1)
            )
            def cancel_action(instance):
                self.dismiss()
                if on_cancel_callback:
                    on_cancel_callback()
            cancel_button.bind(on_release=cancel_action)
            button_layout.add_widget(cancel_button)

        # 6. สร้างปุ่ม "ตกลง/ยืนยัน"
        ok_button = Button(
            text=ok_text,
            font_name='THFont',
            font_size='16sp',
            background_color=(0.2, 0.6, 0.3, 1)
        )
        def ok_action(instance):
            self.dismiss()
            if on_ok_callback:
                on_ok_callback()
        ok_button.bind(on_release=ok_action)
        button_layout.add_widget(ok_button)

        main_layout.add_widget(button_layout)
        
        # 7. กำหนด content ของ Popup ให้เป็น main_layout
        self.content = main_layout