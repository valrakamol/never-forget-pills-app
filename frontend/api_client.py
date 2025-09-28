import requests
import json
from kivy.storage.jsonstore import JsonStore
import jwt
import os # <-- *** 1. เพิ่ม import os ***

# สร้าง JsonStore สำหรับเก็บข้อมูลการล็อกอิน
store = JsonStore('user_data.json')

def ensure_user_data_file_exists():
    """ตรวจสอบให้แน่ใจว่าไฟล์ user_data.json มีอยู่จริง"""
    if not store.exists('auth'):
        store.put('auth', token=None, user_info=None)

def save_auth_token(token, user_info):
    """บันทึก Token และข้อมูลผู้ใช้ลงในไฟล์"""
    store.put('auth', token=token, user_info=user_info)

def get_stored_auth_info():
    """ดึงข้อมูลการล็อกอินที่เก็บไว้ออกจากไฟล์"""
    if store.exists('auth') and store.get('auth').get('token'):
        return store.get('auth')
    return None

def clear_auth_token():
    """ล้างข้อมูลการล็อกอินออกจากไฟล์ (Logout)"""
    store.put('auth', token=None, user_info=None)

def jwt_decode(token):
    """
    ถอดรหัส JWT Token ฝั่ง Client เพื่ออ่านข้อมูล (Claims)
    โดยไม่ต้องใช้ secret key (ไม่ตรวจสอบ signature)
    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None    

class ApiClient:
    def __init__(self):
        # --- *** 2. แยก Base URL สำหรับ API และสำหรับไฟล์ Static *** ---
        self.api_base_url = "http://127.0.0.1:5000/api"
        self.static_base_url = "http://127.0.0.1:5000"
        
        self.headers = {'Content-Type': 'application/json'}
        auth_info = get_stored_auth_info()
        if auth_info:
            token = auth_info.get('token')
            if token:
                self.headers['Authorization'] = f'Bearer {token}'

    def post(self, endpoint, data=None):
        url = f"{self.api_base_url}{endpoint}"
        try:
            return requests.post(url, headers=self.headers, data=json.dumps(data), timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"API POST Error to {url}: {e}")
            return None
        
    def post_file(self, endpoint, file_path):
        url = f"{self.api_base_url}{endpoint}"
        # --- *** จุดที่แก้ไข *** ---
        # 1. สร้าง header สำหรับอัปโหลดโดยเฉพาะ
        upload_headers = {}
        # 2. คัดลอกเฉพาะ Authorization header มา
        if 'Authorization' in self.headers:
            upload_headers['Authorization'] = self.headers['Authorization']
        # (เราจะไม่ใส่ 'Content-Type': 'application/json' เพราะ requests จะตั้งเป็น 'multipart/form-data' ให้เอง)
        
        try:
            with open(file_path, 'rb') as f:
                # 3. กำหนดชื่อ part ของไฟล์ให้เป็น 'file'
                files = {'file': (os.path.basename(file_path), f)}
                # 4. ส่ง request ด้วย header ที่ถูกต้อง
                response = requests.post(url, headers=upload_headers, files=files, timeout=30)
            return response
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print(f"API FILE POST Error to {url}: {e}")
            return None


    def get(self, endpoint):
        url = f"{self.api_base_url}{endpoint}"
        try:
            return requests.get(url, headers=self.headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"API GET Error to {url}: {e}")
            return None
        
    def delete(self, endpoint):
        url = f"{self.api_base_url}{endpoint}"
        try:
            return requests.delete(url, headers=self.headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"API DELETE Error to {url}: {e}")
            return None
            
    def get_full_url(self, relative_path):
        """
        สร้าง URL เต็มจาก relative path ที่ได้จาก Backend
        จะใช้สำหรับรูปภาพที่อยู่ใน /static เท่านั้น
        """
        if relative_path and relative_path.startswith('/'):
            # --- *** 3. ใช้ static_base_url แทน api_base_url *** ---
            return f"{self.static_base_url}{relative_path}"
        return relative_path