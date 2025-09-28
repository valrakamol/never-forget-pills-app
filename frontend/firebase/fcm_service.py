# frontend/firebase/fcm_service.py

# พยายาม import JNIus (Java Native Interface for Python)
# ซึ่งจำเป็นสำหรับการทำงานบน Android
try:
    from jnius import autoclass

    # เข้าถึงคลาส Service ของ Firebase ที่มากับ python-for-android
    PythonFirebaseMessagingService = autoclass('org.kivy.android.PythonFirebaseMessagingService')
    
    # ใช้ @-decorator เพื่อลงทะเบียนฟังก์ชันของเรากับ Service
    @PythonFirebaseMessagingService.on_message
    def on_message(message):
        """
        ฟังก์ชันนี้จะถูกเรียกเมื่อได้รับ Notification
        ในขณะที่แอปกำลังเปิดใช้งานอยู่ (Foreground)
        
        คุณสามารถเพิ่ม Logic ตรงนี้ได้ถ้าต้องการให้แอปทำอะไรบางอย่าง
        เมื่อได้รับ Notification ตอนที่ผู้ใช้กำลังใช้งานแอปอยู่
        """
        print("FCM Message Received in Foreground Service:", message)

    @PythonFirebaseMessagingService.on_token
    def on_token(token):
        """
        ฟังก์ชันนี้จะถูกเรียกเมื่อมีการสร้าง Token ใหม่
        (เช่น ติดตั้งแอปครั้งแรก หรือล้างข้อมูลแอป)
        
        plyer จะจัดการการส่ง Token นี้ไปให้โค้ดหลักของเราโดยอัตโนมัติ
        เราแค่ต้องมีฟังก์ชันนี้ไว้เพื่อความสมบูรณ์ของ Service
        """
        print("FCM Token Generated/Refreshed in Service:", token)

except ImportError:
    # ถ้า import jnius ไม่ได้ (เช่น รันบน Windows/macOS)
    # ให้โค้ดส่วนนี้เป็นค่าว่าง เพื่อไม่ให้แอปแครชตอนทดสอบบนคอมพิวเตอร์
    print("JNIus not found. FCM service will not be active on this platform.")
    pass