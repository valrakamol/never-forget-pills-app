[app]
# (app)
# title: ชื่อแอปพลิเคชันของคุณ
title = ยาไม่ลืม

# package.name: ชื่อแพ็คเกจ (ตัวพิมพ์เล็ก ไม่มีเว้นวรรค)
package.name = medireminder

# package.domain: โดเมนของคุณ (สลับกัน)
package.domain = com.valrakamol

# source.dir: โฟลเดอร์ที่มี main.py ('.' หมายถึงโฟลเดอร์ปัจจุบัน)
source.dir = .

# source.include_exts: นามสกุลไฟล์ทั้งหมดที่ต้องใช้ในแอป
source.include_exts = py,png,jpg,jpeg,kv,ttf,json

# version: เวอร์ชันของแอป
version = 1.0

# requirements: Library ทั้งหมดที่ Kivy ใช้ (สำคัญมาก)
# เราจะยังไม่ใส่ kivy_garden.graph ก่อน เพื่อให้ Build ผ่านง่ายๆ
requirements = python3,kivy==2.3.0,pillow,requests,pyjwt,plyer,https://github.com/kivy/pyjnius/archive/master.zip

# orientation: การวางแนวของหน้าจอ
orientation = portrait

# icon.filename: Path ไปยังไฟล์ไอคอนของแอป
icon.filename = %(source.dir)s/assets/app_logo.png

# services: ระบุ Service ที่จะทำงานเบื้องหลัง (สำหรับ FCM)
services = FcmService:firebase/fcm_service.py


[buildozer]
# log_level: ระดับการแสดง Log (2 คือ verbose)
log_level = 2

# warn_on_root: เตือนถ้า buildozer ถูกรันในฐานะ root
warn_on_root = 1


# --- *** การตั้งค่าสำหรับ Android (สำคัญที่สุด) *** ---
# (android)
# api: เวอร์ชัน Android API ที่ใช้คอมไพล์
android.api = 33

# minapi: เวอร์ชัน Android ขั้นต่ำที่แอปสามารถทำงานได้
android.minapi = 21

# sdk: เวอร์ชัน Android Build Tools ที่จะใช้ (ไม่จำเป็นต้องเปลี่ยน)
android.sdk = 24

# ndk: เวอร์ชัน Android NDK ที่จะใช้ (ไม่จำเป็นต้องเปลี่ยน)
android.ndk = 25b

# ndk_version: ตรึงเวอร์ชัน NDK ให้แน่นอน
android.ndk_version = 25b

# permissions: สิทธิ์ที่แอปพลิเคชันต้องการ
android.permissions = INTERNET, VIBRATE

# archs: สถาปัตยกรรม CPU ของมือถือ (arm64-v8a คือมาตรฐานปัจจุบัน)
android.archs = arm64-v8a

# entrypoint: ไฟล์ที่จะถูกเรียกเมื่อ Service เริ่มทำงาน (สำหรับ FCM)
android.entrypoint = org.kivy.android.PythonActivity

# activity_class_name: ชื่อคลาส Activity หลัก
android.activity_class_name = org.kivy.android.PythonActivity

# wakelock: ป้องกันไม่ให้ CPU เข้าสู่โหมด Sleep ตอนที่แอปทำงาน
android.wakelock = True

# enable_androidx: เปิดใช้งาน AndroidX ซึ่งจำเป็นสำหรับ Library สมัยใหม่
android.enable_androidx = True


# (p4a: python-for-android)
# branch: สาขาของ python-for-android ที่จะใช้
# develop มักจะมีการแก้ไข Bug ล่าสุดและเข้ากันได้ดีกว่า
p4a.branch = develop