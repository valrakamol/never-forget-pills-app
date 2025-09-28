[app]
title = ยาไม่ลืม
package.name = medireminder
package.domain = com.valrakamol
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,json
version = 1.2
requirements = python3,kivy==2.3.0,pillow,requests,pyjwt,plyer,pyjnius
orientation = portrait
icon.filename = %(source.dir)s/assets/app_logo.png
services = FcmService:firebase/fcm_service.py

[buildozer]
log_level = 2

# (android)
android.api = 33
android.minapi = 21
android.ndk_version = 25b
android.permissions = INTERNET, VIBRATE
android.archs = arm64-v8a
android.enable_androidx = True
p4a.branch = develop