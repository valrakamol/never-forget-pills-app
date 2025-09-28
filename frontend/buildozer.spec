[app]
title = ยาไม่ลืม
package.name = medireminder
package.domain = com.valrakamol
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,json
version = 1.0

# ✅ Dependencies ที่แนะนำ
requirements = python3,kivy==2.3.0,pillow,requests,pyjwt,plyer,pyjnius

orientation = portrait
icon.filename = %(source.dir)s/assets/app_logo.png

# ✅ ใช้ Service FCM (ถ้ามีไฟล์จริง)
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
android.permissions = INTERNET, VIBRATE
android.archs = arm64-v8a
android.wakelock = True
android.enable_androidx = True

# ✅ เพิ่ม Path ให้ CI หา SDK/NDK เจอ
android.sdk_path = $HOME/.buildozer/android/platform/android-sdk
android.ndk_path = $HOME/.buildozer/android/platform/android-ndk-r25b

# ✅ ใช้ branch develop เพื่อแก้บั๊กล่าสุด
p4a.branch = develop
