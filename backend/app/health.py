from flask import Blueprint, request, jsonify
from .models import User, HealthRecord, Notification
from .extensions import db
# เพิ่ม import get_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from firebase_admin import db as firebase_db, messaging
from datetime import datetime

health_bp = Blueprint('health', __name__, url_prefix='/api/health')

def send_fcm_notification(user, title, body):
    if user and user.fcm_token:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=user.fcm_token
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"Failed to send FCM to {user.username}: {e}")
    return False

# -----------------------------------------------------------------------------
# Endpoint สำหรับ อสม. เพื่อบันทึกข้อมูลสุขภาพของผู้สูงอายุ
# -----------------------------------------------------------------------------
@health_bp.route('/record/add', methods=['POST'])
@jwt_required()
def add_health_record():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') != 'osm':
        return jsonify(msg="สิทธิ์ไม่เพียงพอ..."), 403

    data = request.json
    elder_id = data.get('elder_id')
    if not elder_id:
        return jsonify(msg="กรุณาระบุรหัสผู้สูงอายุ"), 400

    osm_user = User.query.get(current_user_id)
    elder = User.query.filter_by(id=elder_id, role='elder').first()

    # --- *** จุดที่แก้ไข: ลบการตรวจสอบ managed_elders ออก *** ---
    # เราจะเช็คแค่ว่า osm_user และ elder มีตัวตนในระบบหรือไม่
    if not osm_user or not elder:
        return jsonify(msg="ไม่พบผู้ใช้ อสม. หรือผู้สูงอายุรายนี้"), 404
    
    new_record = HealthRecord(
        systolic_bp=data.get('systolic_bp'),
        diastolic_bp=data.get('diastolic_bp'),
        weight=data.get('weight'),
        pulse=data.get('pulse'),
        notes=data.get('notes'),
        user_id=elder.id,
        recorded_by_id=osm_user.id
    )
    db.session.add(new_record)
    alerts = []
    # เกณฑ์ (สามารถย้ายไปไว้ใน SystemSettings ได้ในอนาคต)
    SYSTOLIC_HIGH = 140
    DIASTOLIC_HIGH = 90
    PULSE_LOW = 50
    PULSE_HIGH = 100

    if new_record.systolic_bp and new_record.systolic_bp >= SYSTOLIC_HIGH:
        alerts.append(f"ความดันตัวบนสูงผิดปกติ ({new_record.systolic_bp})")
    if new_record.diastolic_bp and new_record.diastolic_bp >= DIASTOLIC_HIGH:
        alerts.append(f"ความดันตัวล่างสูงผิดปกติ ({new_record.diastolic_bp})")
    if new_record.pulse:
        if new_record.pulse <= PULSE_LOW:
            alerts.append(f"ชีพจรต่ำผิดปกติ ({new_record.pulse})")
        elif new_record.pulse >= PULSE_HIGH:
            alerts.append(f"ชีพจรสูงผิดปกติ ({new_record.pulse})")

    # ถ้ามีค่าผิดปกติ
    if alerts:
        elder_name = f"{elder.first_name} {elder.last_name}"
        alert_message = f"แจ้งเตือนสุขภาพ ({elder_name}): {', '.join(alerts)}"
        
        # ส่ง Notification ไปหาผู้ดูแลทุกคน
        for manager in elder.managers:
            # 1. บันทึก Notification ลง DB
            notif = Notification(user_id=manager.id, message=alert_message)
            db.session.add(notif)
            # 2. ส่ง FCM
            send_fcm_notification(manager, "แจ้งเตือนสุขภาพผิดปกติ!", alert_message)
            
    db.session.commit()

    try:
        ref = firebase_db.reference(f'health_summary/{elder.id}')
        ref.set({
            'systolic_bp': new_record.systolic_bp,
            'diastolic_bp': new_record.diastolic_bp,
            'weight': new_record.weight,
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูลไปยัง Firebase RTDB: {e}")

    return jsonify(msg="เพิ่มข้อมูลสุขภาพสำเร็จแล้ว"), 201

# -----------------------------------------------------------------------------
# Endpoint สำหรับผู้ดูแล/อสม. เพื่อดึงประวัติข้อมูลสุขภาพ
# -----------------------------------------------------------------------------
@health_bp.route('/records/elder/<int:elder_id>', methods=['GET'])
@jwt_required()
def get_health_records_for_elder(elder_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') not in ['caregiver', 'osm', 'elder']:
        return jsonify(msg="สิทธิ์ไม่เพียงพอ"), 403

    viewer = User.query.get(current_user_id)
    elder_to_view = User.query.filter_by(id=elder_id, role='elder').first()
    
    # --- *** จุดที่แก้ไข: เพิ่มเงื่อนไขสำหรับ 'osm' *** ---
    if claims.get('role') == 'elder':
        if elder_id != current_user_id:
            return jsonify(msg="ไม่ได้รับอนุญาต..."), 403
    elif claims.get('role') == 'caregiver': # <-- ใช้ elif เพื่อแยกเงื่อนไข
        # caregiver ต้องเป็นผู้ดูแลของ elder นี้
        if not viewer or not elder_to_view or elder_to_view not in viewer.managed_elders:
            return jsonify(msg="ไม่ได้รับอนุญาตให้เข้าถึงข้อมูลสุขภาพของผู้สูงอายุรายนี้"), 403

    # อ่าน month/year จาก query string
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    query = HealthRecord.query.filter_by(user_id=elder_id)
    if month and year:
        # กรอง record_date ให้อยู่ในเดือน/ปีที่เลือก
        from datetime import datetime
        from calendar import monthrange
        start_date = datetime(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = datetime(year, month, end_day, 23, 59, 59)
        query = query.filter(HealthRecord.record_date >= start_date, HealthRecord.record_date <= end_date)

    records = query.order_by(HealthRecord.record_date.desc()).all()
    result = [
        {
            'id': rec.id, 
            'systolic_bp': rec.systolic_bp, 
            'diastolic_bp': rec.diastolic_bp, 
            'weight': rec.weight,
            'pulse': rec.pulse, 
            'notes': rec.notes, 
            'recorded_at': rec.record_date.strftime('%Y-%m-%d %H:%M')
        } for rec in records
    ]
    return jsonify(records=result), 200