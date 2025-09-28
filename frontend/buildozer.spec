[app]
title = ยาไม่ลืม
package.name = medireminder
package.domain = com.valrakamol
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,json
version = 1.0

requirements = python3,kivy==2.3.0,pillow,requests,pyjwt,plyer,git+https://github.com/kivy/pyjnius.git@fix-python3-long

orientation = portrait
icon.filename = %(source.dir)s/assets/app_logo.png
services = FcmService:firebase/fcm_service.py

[buildozer]
log_level = 2
warn_on_root = 1

# Android Settings
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.ndk_version = 25b
android.permissions = INTERNET, VIBRATE
android.archs = arm64-v8a,armeabi-v7a
android.wakelock = True
android.enable_androidx = True
p4a.branch = develop
