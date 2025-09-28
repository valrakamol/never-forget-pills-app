# frontend/firebase/fcm_service.py

try:
    from jnius import autoclass, cast

    # เข้าถึง Context หลักของ Android app
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
    activity = PythonActivity.mActivity

    # ลองเข้าถึง Firebase Messaging SDK (ถ้ามีติดตั้งใน Gradle)
    FirebaseMessaging = autoclass("com.google.firebase.messaging.FirebaseMessaging")

    def get_fcm_token():
        """
        ขอ Token ของ Firebase (ต้องมี Firebase SDK ฝั่ง Android Gradle)
        """
        try:
            FirebaseMessaging.getInstance().getToken().addOnCompleteListener(
                autoclass("com.google.android.gms.tasks.OnCompleteListener")(
                    lambda task: print("FCM Token:", task.getResult())
                )
            )
        except Exception as e:
            print("Error fetching FCM Token:", e)

    def on_message_received(message):
        """
        Handle ข้อความที่เข้ามาจาก FCM
        """
        print("FCM Message:", message)

except ImportError:
    # ถ้า import jnius ไม่ได้ (เช่น ตอนรันบน Windows/macOS)
    print("JNIus not found. FCM service inactive.")

    def get_fcm_token():
        print("FCM token unavailable (not running on Android).")

    def on_message_received(message):
        print("Received FCM message (simulated):", message)
