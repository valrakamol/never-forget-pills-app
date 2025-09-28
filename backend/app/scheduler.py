# backend/app/scheduler.py
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, timedelta
from .models import User, Medication, MedicationLog, Notification, SystemSetting
from .extensions import db
from firebase_admin import messaging

def create_internal_notification(user_id, message, link_to=None):
    """ฟังก์ชันช่วยสำหรับสร้าง Notification ในฐานข้อมูลของเราเองเพื่อป้องกันการส่งซ้ำ"""
    notif = Notification(user_id=user_id, message=message, link_to=link_to)
    db.session.add(notif)

def send_fcm_message(user, title, body):
    """ฟังก์ชันช่วยสำหรับส่ง FCM Notification"""
    if user and user.fcm_token:
        try:
            fcm_message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=user.fcm_token
            )
            messaging.send(fcm_message)
            print(f"Sent FCM to {user.username}: {title}")
        except Exception as e:
            print(f"Error sending FCM to {user.id}: {e}")

def check_medicine_schedule(app):
    """
    Job ที่ทำงานทุกนาทีเพื่อจัดการการแจ้งเตือนการทานยา
    """
    with app.app_context():
        now = datetime.now()
        today = now.date()
        
        # --- ดึงค่า Config จากฐานข้อมูล (เหมือนเดิม) ---
        try:
            alert_after_min = int(SystemSetting.query.filter_by(key='ALERT_AFTER_MINUTES').first().value)
        except (AttributeError, ValueError):
            alert_after_min = 15 # Default: 15 นาที
        
        # --- *** จุดที่แก้ไข 1: ดึงยาทั้งหมดที่ต้องกินในวันนี้ *** ---
        # เราจะไม่กรองตามเวลาแล้ว แต่จะดึงยาที่ต้องกิน "ในวันนี้" ทั้งหมด
        meds_for_today = Medication.query.filter(
            Medication.start_date <= today,
            (Medication.end_date == None) | (Medication.end_date >= today)
        ).all()

        for med in meds_for_today:
            # แปลงเวลาที่เก็บเป็น String "HH:MM" กลับเป็น datetime object ของ "วันนี้"
            try:
                med_time_obj = datetime.strptime(med.time_to_take, '%H:%M').time()
                med_datetime_today = datetime.combine(today, med_time_obj)
            except ValueError:
                continue # ข้ามยาที่ format เวลาผิด

            # ตรวจสอบว่ากินยาไปหรือยัง
            log_exists_today = MedicationLog.query.filter(
                MedicationLog.medication_id == med.id, 
                db.func.date(MedicationLog.taken_at) == today
            ).first()

            if log_exists_today:
                continue # ถ้ากินแล้ว ก็ไม่ต้องทำอะไรกับยาตัวนี้

            # --- *** จุดที่แก้ไข 2: Logic การแจ้งเตือนใหม่ *** ---
            
            elder = med.patient
            elder_name = f"{elder.first_name} {elder.last_name}"
            med_info_str = f"{med.name} ({med.time_to_take})"

            # A. แจ้งเตือนเมื่อ "ถึงเวลาพอดี"
            # เช็คว่าเวลาปัจจุบัน อยู่ในนาทีเดียวกับเวลากินยาหรือไม่
            if now.hour == med_datetime_today.hour and now.minute == med_datetime_today.minute:
                
                # --- ส่งหาผู้สูงอายุ ---
                title_elder = f"ได้เวลาทานยา! ({med.time_to_take})"
                body_elder = f"อย่าลืมทานยา {med.name}"
                send_fcm_message(elder, title_elder, body_elder)
                create_internal_notification(elder.id, f"เตือนกินยา: {med_info_str}")

                # --- ส่งหาผู้ดูแลทุกคน ---
                title_manager = f"แจ้งเตือน: {elder_name}"
                body_manager = f"ถึงเวลาทานยา {med_info_str}"
                for manager in elder.managers:
                    send_fcm_message(manager, title_manager, body_manager)
                    create_internal_notification(manager.id, f"{elder_name} ถึงเวลาทานยา: {med_info_str}")

            # B. แจ้งเตือนซ้ำทุก 15 นาที "หลังจากเลยเวลา"
            # เช็คว่าเลยเวลากินยามาแล้ว และ "หารด้วย 15 ลงตัว"
            minutes_passed = (now - med_datetime_today).total_seconds() / 60
            
            if minutes_passed > 0 and (int(minutes_passed) % alert_after_min == 0):
                # ป้องกันการส่งซ้ำในนาทีเดียวกัน (ถ้า job ทำงานเหลื่อม)
                last_minute_start = now.replace(second=0, microsecond=0) - timedelta(minutes=1)
                
                # สร้างข้อความที่ไม่ซ้ำกันสำหรับการแจ้งเตือนซ้ำ
                reminder_message_log = f"ยาขาด (เตือนซ้ำ): {med_info_str}"
                
                # เช็คว่าเคยส่งแจ้งเตือนซ้ำไปใน "นาทีที่แล้ว" หรือไม่
                notif_sent_recently = Notification.query.filter(
                    Notification.message == reminder_message_log,
                    Notification.created_at >= last_minute_start
                ).first()

                if not notif_sent_recently:
                    # --- ส่งหาผู้ดูแลทุกคน (เท่านั้น) ---
                    title_manager_missed = f"ยาขาด! (เตือนซ้ำ): {elder_name}"
                    body_manager_missed = f"ยังไม่กดยืนยันการทานยา {med_info_str}"
                    for manager in elder.managers:
                        send_fcm_message(manager, title_manager_missed, body_manager_missed)
                        create_internal_notification(manager.id, reminder_message_log)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error during scheduler db commit: {e}")


def init_scheduler(app):
    """สร้างและเริ่มการทำงานของ Scheduler"""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=check_medicine_schedule, 
        args=[app], 
        trigger="interval", 
        minutes=1, # ทำงานทุก 1 นาที
        id='check_medicine_schedule_job',
        replace_existing=True
    )
    scheduler.start()
    print("ตัวจัดตารางแจ้งเตือนการทานยาได้เริ่มทำงานเรียบร้อยแล้ว")