#backend/app/users.py
from flask import Blueprint, request, jsonify
from .models import User
from .extensions import db
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# -----------------------------------------------------------------------------
# Endpoint สำหรับดึงข้อมูลโปรไฟล์ของผู้ใช้ที่ล็อกอินอยู่
# -----------------------------------------------------------------------------
@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    # ใช้ get_jwt() เพื่อดึง claims ทั้งหมดจาก Token
    # มีประสิทธิภาพสูง เพราะไม่ต้อง query ฐานข้อมูลอีก
    claims = get_jwt()
    return jsonify({
        'id': claims.get('sub'),  # 'sub' คือ user_id ที่เราใส่ใน identity
        'username': claims.get('username'),
        'full_name': claims.get('full_name'),
        'role': claims.get('role')
    }), 200

# -----------------------------------------------------------------------------
# Endpoint สำหรับผู้ดูแล/อสม. เพื่อดึงรายชื่อผู้สูงอายุในความดูแล
# -----------------------------------------------------------------------------
@users_bp.route('/my_managed_elders', methods=['GET'])
@jwt_required()
def get_my_managed_elders():
    claims = get_jwt()
    # อนุญาตให้ elder, osm, caregiver ใช้ endpoint นี้
    if claims.get('role') not in ['osm', 'caregiver', 'elder']:
        return jsonify({"msg": "Unauthorized"}), 403

    current_user_id = get_jwt_identity()
    manager = User.query.get(current_user_id)
    if not manager:
        return jsonify(msg="ไม่พบผู้ใช้ที่มีบทบาทผู้จัดการในฐานข้อมูล"), 404

    # ถ้าเป็น elder ให้คืนข้อมูลของตัวเอง
    if manager.role == 'elder':
        elders_list = [{
            "id": manager.id,
            "username": manager.username,
            "first_name": manager.first_name,
            "last_name": manager.last_name,
            "full_name": f"{manager.first_name} {manager.last_name}"
        }]
        return jsonify(elders=elders_list), 200

    # ถ้าเป็น osm/caregiver คืน managed_elders ตามเดิม
    elders = manager.managed_elders.order_by(User.first_name).all()
    elders_list = [{
        "id": elder.id,
        "username": elder.username,
        "first_name": elder.first_name,
        "last_name": elder.last_name,
        "full_name": f"{elder.first_name} {elder.last_name}"
    } for elder in elders]
    return jsonify(elders=elders_list), 200

# -----------------------------------------------------------------------------
# Endpoint สำหรับผู้ดูแล (Caregiver) เพื่อ "สร้าง" บัญชีผู้สูงอายุใหม่
# -----------------------------------------------------------------------------
@users_bp.route('/add_elder', methods=['POST'])
@jwt_required()
def add_elder():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') != 'caregiver':
        return jsonify({"msg": "ไม่มีสิทธิ์: การกระทำนี้อนุญาตให้เฉพาะผู้ดูแลทำได้เท่านั้น"}), 403

    caregiver_user = User.query.get(current_user_id)
    if not caregiver_user:
         return jsonify({"msg": "ไม่พบผู้ใช้ในฐานข้อมูลที่มีบทบาทเป็นผู้ดูแล"}), 404

    data = request.json
    # --- *** จุดที่แก้ไข 1: รับ username มาโดยตรง *** ---
    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    password = data.get('password')

    # --- *** จุดที่แก้ไข 2: ตรวจสอบว่ามี username ด้วย *** ---
    if not all([username, first_name, last_name, password]):
        return jsonify({"msg": "กรุณากรอกข้อมูลที่จำเป็น (ชื่อผู้ใช้, ชื่อ, นามสกุล, รหัสผ่าน) ให้ครบถ้วน"}), 400

    # ตรวจสอบว่า username ซ้ำหรือไม่ (เหมือนเดิม)
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": f"ชื่อผู้ใช้ '{username}' นี้ถูกใช้ไปแล้ว"}), 409

    elder = User(
        username=username.strip().lower(), # <-- ทำให้เป็นตัวพิมพ์เล็กและตัดช่องว่าง
        first_name=first_name, 
        last_name=last_name, 
        role='elder',
        status='active'
    )
    elder.set_password(password)
    caregiver_user.managed_elders.append(elder)

    db.session.add(elder)
    db.session.commit()
    return jsonify({"msg": f"สร้างผู้สูงอายุชื่อ '{username}' เรียบร้อย และเชื่อมต่อกับผู้ดูแล '{caregiver_user.username}' แล้ว"}), 201

# -----------------------------------------------------------------------------
# Endpoint สำหรับ อสม. (osm) เพื่อ "เชื่อมโยง" กับผู้สูงอายุที่มีบัญชีอยู่แล้ว
# -----------------------------------------------------------------------------
@users_bp.route('/link_elder_by_id', methods=['POST'])
@jwt_required()
def link_elder_by_id():
    current_user_id = get_jwt_identity()
    manager = User.query.get(current_user_id)
    if not manager or manager.role not in ['caregiver', 'osm']:
        return jsonify(msg="Permission denied"), 403

    data = request.json
    elder_id = data.get('elder_id')
    elder = User.query.filter_by(id=elder_id, role='elder').first()

    if not elder:
        return jsonify(msg="Elder not found"), 404
    
    if elder in manager.managed_elders:
        return jsonify(msg="You are already managing this elder"), 409

    manager.managed_elders.append(elder)
    db.session.commit()
    return jsonify(msg=f"Successfully linked with {elder.first_name}"), 200

# -----------------------------------------------------------------------------
# Endpoint สำหรับผู้ดูแล/อสม. เพื่อ "ยกเลิกการเชื่อมโยง" กับผู้สูงอายุ
# -----------------------------------------------------------------------------
@users_bp.route('/unlink_elder', methods=['POST'])
@jwt_required()
def unlink_elder():
    current_user_id = get_jwt_identity()
    manager = User.query.get(current_user_id)
    
    if not manager or manager.role not in ['caregiver', 'osm']:
        return jsonify(msg="ไม่มีสิทธิ์เข้าใช้งาน"), 403

    data = request.json
    elder_id = data.get('elder_id')
    
    elder_to_unlink = User.query.filter_by(id=elder_id, role='elder').first()

    if not elder_to_unlink:
        return jsonify(msg="ไม่พบข้อมูลผู้สูงอายุในระบบ"), 404

    # ตรวจสอบว่าผู้สูงอายุคนนี้อยู่ในความดูแลของผู้ใช้คนนี้จริงหรือไม่
    if elder_to_unlink in manager.managed_elders:
        # ใช้ .remove() เพื่อลบความสัมพันธ์ออกจาก association table
        manager.managed_elders.remove(elder_to_unlink)
        db.session.commit()
        return jsonify(msg=f"ยกเลิกการเชื่อมต่อกับ {elder_to_unlink.first_name} สำเร็จแล้ว"), 200
    else:
        return jsonify(msg="คุณไม่มีสิทธิ์ดูแลผู้สูงอายุรายนี้"), 403

# -----------------------------------------------------------------------------
# Endpoint สำหรับรับ FCM Token จาก Client
# -----------------------------------------------------------------------------
@users_bp.route('/register_fcm', methods=['POST'])
@jwt_required()
def register_fcm():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify(msg="ไม่พบข้อมูลผู้ใช้ในระบบ"), 404
        
    data = request.json
    fcm_token = data.get('fcm_token')
    if not fcm_token:
        return jsonify(msg="ไม่มีข้อมูลโทเค็น FCM"), 400
        
    existing_user_with_token = User.query.filter_by(fcm_token=fcm_token).first()
    if existing_user_with_token and existing_user_with_token.id != user.id:
        existing_user_with_token.fcm_token = None
        db.session.commit()

    user.fcm_token = fcm_token
    db.session.commit()
    return jsonify(msg="บันทึกโทเค็น FCM เรียบร้อยแล้ว"), 200

@users_bp.route('/admin/reset_password/<int:user_id>', methods=['GET', 'POST'])
@jwt_required(locations=['cookies'])
def admin_reset_password(user_id):
    admin_id = get_jwt_identity()
    admin_user = User.query.get(admin_id)
    if not admin_user or admin_user.role != 'admin':
        return "Permission Denied", 403

    user_to_edit = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or new_password != confirm_password:
            flash('Passwords do not match or are empty.', 'danger')
        else:
            user_to_edit.set_password(new_password)
            db.session.commit()
            flash(f'Password for {user_to_edit.username} has been updated!', 'success')
            # --- *** แก้ไขเล็กน้อย: redirect ไปที่หน้า List ของ User *** ---
            return redirect(url_for('admin_user.index_view'))

    # ถ้าเป็น GET, แสดงฟอร์ม
    return render_template('admin/reset_password.html', user=user_to_edit)

# ----------------------------------------------------------------------------- 
# Endpoint สำหรับดึง "ผู้สูงอายุทั้งหมด" (สำหรับอสม.ดูได้ทุกคน)
# ----------------------------------------------------------------------------- 
@users_bp.route('/all_elders', methods=['GET'])
def get_all_elders():
    elders = User.query.filter_by(role='elder').order_by(User.first_name).all()
    elders_list = [
        {
            "id": elder.id,
            "username": elder.username,
            "first_name": elder.first_name,
            "last_name": elder.last_name,
            "full_name": f"{elder.first_name} {elder.last_name}"
        }
        for elder in elders
    ]
    return jsonify(elders=elders_list), 200