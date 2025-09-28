#backend/app/auth.py
from flask import Blueprint, request, jsonify
from .models import User
from .extensions import db
from flask_jwt_extended import create_access_token,set_access_cookies, unset_jwt_cookies
from flask import render_template, redirect, url_for, flash, make_response, request

# สร้าง Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# -----------------------------------------------------------------------------
# Endpoint สำหรับการสมัครสมาชิก (สำหรับผู้ดูแล/อสม.)
# -----------------------------------------------------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    role = data.get('role')

    # ตรวจสอบว่าได้รับข้อมูลครบหรือไม่
    if not all([username, password, first_name, last_name, role]):
        return jsonify({"msg": "กรุณากรอกข้อมูลให้ครบถ้วน"}), 400

    # ตรวจสอบว่า role ที่ส่งมาถูกต้องหรือไม่
    if role not in ['caregiver', 'osm']:
        return jsonify({"msg": "สิทธิ์บทบาทไม่ถูกต้องสำหรับการลงทะเบียนด้วยตนเอง"}), 400

    # ตรวจสอบว่า username นี้มีในระบบแล้วหรือยัง
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว"}), 409
    
    # ประกาศตัวแปรก่อน แล้วค่อยกำหนดค่าใน if-elif
    initial_status = ''
    success_message = ''

    if role == 'caregiver':
        initial_status = 'active'
    elif role == 'osm':
        initial_status = 'pending'

    # สร้าง User ใหม่
    new_user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
        status=initial_status 
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    if role == 'caregiver':
        return jsonify({"msg": f"User '{username}' การลงทะเบียนสำเร็จ!"}), 201
    else: # role == 'osm'
        return jsonify({"msg": "การลงทะเบียนสำเร็จ! โปรดส่งข้อมูลทางอีเมล \n valrakamol.kh.65@ubu.ac.th \n และรออนุมัติเพื่อยืนยันว่าเป็นอสม "}), 201

# -----------------------------------------------------------------------------
# Endpoint สำหรับการเข้าสู่ระบบ (สำหรับทุก Role)
# -----------------------------------------------------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if user.status != 'active':
            return jsonify({"msg": f"บัญชีของคุณยังไม่ได้รับการอนุมัติหรือถูกระงับ"}), 403
        
        additional_claims = {
            "role": user.role,
            "username": user.username,
            "full_name": f"{user.first_name} {user.last_name}"
        }
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"}), 401

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'admin':
            access_token = create_access_token(identity=user.id)
            # เรา redirect ไปที่ 'admin.index' ซึ่งคือหน้าแรกของ Flask-Admin
            response = make_response(redirect(url_for('admin.index')))
            set_access_cookies(response, access_token)
            return response
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง หรือไม่ใช่บัญชีผู้ดูแลระบบ')

    return render_template('admin/login.html')

@admin_auth_bp.route('/logout')
def admin_logout():
    # แก้ไข url_for ให้ถูกต้องด้วย
    response = make_response(redirect(url_for('admin_auth.admin_login')))
    unset_jwt_cookies(response)
    return response