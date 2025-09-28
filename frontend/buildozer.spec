[app]

# (str) Title of your application
title = ยาไม่ลืม

# (str) Package name
package.name = yanotforget

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,ttf,json

# (list) List of inclusions using pattern matching
# assets/* จะรวมไฟล์ทั้งหมดในโฟลเดอร์ assets เข้าไปด้วย
source.include_patterns = assets/*,kv/*

# (list) List of directory to exclude (let empty to not exclude anything)
# ป้องกันไม่ให้ venv และไฟล์ build อื่นๆ ปนเข้าไปใน .apk
source.exclude_dirs = tests, bin, venv, .buildozer

# (str) Application versioning
version = 0.1

# (list) Application requirements
# --- *** จุดที่แก้ไขปัญหา pyjnius และ plyer *** ---
requirements = python3,kivy==2.3.0,kivy-garden.graph,requests,pyjwt,plyer==2.1.0,https://github.com/kivy/pyjnius/archive/master.zip

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/assets/icon.png

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True


#
# Python for android (p4a) specific
#

# --- *** เพิ่มส่วนนี้เพื่อบังคับอัปเดต p4a *** ---
p4a.branch = master
p4a.source_dir = .buildozer/android/platform/python-for-android


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1