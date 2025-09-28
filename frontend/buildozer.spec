[app]
title = ยาไม่ลืม
package.name = medireminder
package.domain = com.valrakamol
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,json
version = 1.0

# ✅ Dependencies (ใช้ pyjnius commit ล่าสุดแทน long issue)
requirements = python3,kivy==2.3.0,pillow,requests,pyjwt,plyer,https://github.com/kivy/pyjnius/archive/master.zip

orientation = portrait
icon.filename = %(source.dir)s/assets/app_logo.png

# ✅ Service FCM (อย่าลืมมีไฟล์จริง firebase/fcm_service.py)
services = FcmService:firebase/fcm_service.py

[buildozer]
log_level = 2
warn_on_root = 1

# --- Android Settings ---
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.ndk_version = 25b
android.permissions = INTERNET, VIBRATE, WAKE_LOCK, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE
android.archs = arm64-v8a
android.wakelock = True
android.enable_androidx = True

# ✅ Paths (สำคัญเวลาใช้ GitHub Actions CI)
android.sdk_path = $HOME/.buildozer/android/platform/android-sdk
android.ndk_path = $HOME/.buildozer/android/platform/android-ndk-r25b

# ✅ ใช้ branch develop ของ python-for-android (แก้บั๊กใหม่สุด)
p4a.branch = develop

# ✅ ถ้ามี Gradle ปัญหา ให้เปิดใช้ตัวนี้
android.gradle_dependencies = com.google.firebase:firebase-messaging:23.1.2

# ✅ เพิ่ม options
android.extra_args = --no-byte-compile-python
