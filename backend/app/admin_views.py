#backend/app/admin_views.py
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, flash, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired
import wtforms
from firebase_admin import messaging

# -----------------------------------------------------------------------------
# Base View สำหรับ Admin (มีระบบตรวจสอบสิทธิ์ และ ปิด CSRF)
# -----------------------------------------------------------------------------
class ProtectedAdminView(ModelView):
    # ปิดการป้องกัน CSRF โดยการใช้ FlaskForm พื้นฐาน
    form_base_class = FlaskForm

    def is_accessible(self):
        """ตรวจสอบสิทธิ์ Admin โดยใช้ JWT Cookie"""
        try:
            # ตรวจสอบว่ามี JWT ใน cookie หรือไม่
            verify_jwt_in_request(locations=['cookies'])
            current_user_id = get_jwt_identity()
            # Import model ภายในฟังก์ชันเพื่อป้องกัน Circular Import
            from .models import User
            user = User.query.get(current_user_id)
            return user.role == 'admin'
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        """ถ้าไม่มีสิทธิ์ ให้ Redirect ไปหน้า Login ของ Admin"""
        return redirect(url_for('admin_auth.admin_login', next=request.url))
# -----------------------------------------------------------------------------
# Custom Form สำหรับ MasterMedicine
# -----------------------------------------------------------------------------

class MasterMedicineForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="กรุณากรอกชื่อยา")])
    form = SelectField(
        'Form',
        choices=[
            ('เม็ด', 'เม็ด'),
            ('แคปซูล', 'แคปซูล'),
            ('ช้อนชา', 'ช้อนชา'),
            ('ช้อนโต๊ะ', 'ช้อนโต๊ะ'),
            ('มิลลิกรัม', 'มิลลิกรัม'),
            ('cc', 'cc'),
            ('ผง', 'ผง')
        ],
        validators=[DataRequired(message="กรุณาเลือกรูปแบบยา")]
    )
    description = TextAreaField('Description')

# -----------------------------------------------------------------------------
# View สำหรับจัดการ "User" โดยเฉพาะ
# -----------------------------------------------------------------------------
class UserAdminView(ProtectedAdminView):
    # คอลัมน์ที่จะแสดงในหน้า List
    column_list = ('id', 'username', 'first_name', 'last_name', 'role', 'status')
    # คอลัมน์ที่ค้นหาได้
    column_searchable_list = ('username', 'first_name', 'last_name')
    # Filter ด้านข้าง
    column_filters = ('role', 'status')
    # คอลัมน์ที่แก้ไขได้โดยตรงในตาราง
    column_editable_list = ('status', 'role')

    form_choices = {
        'role': [
            ('admin', 'Admin'),
            ('caregiver', 'Caregiver'),
            ('osm', 'OSM'),
            ('elder', 'Elder')
        ],
        'status': [
            ('active', 'Active'),
            ('pending', 'Pending')  
        ]
    }
    
    # --- *** จุดที่แก้ไข *** ---
    # 1. กำหนด Fields ที่จะแสดงในฟอร์ม "สร้าง" (Create) ให้เป็น List
    form_create_rules = [
        'username', 'first_name', 'last_name', 'role', 'status', 'password_new'
    ]

    # 2. กำหนด Fields ที่จะแสดงในฟอร์ม "แก้ไข" (Edit) ให้เป็น List
    form_edit_rules = [
        'username', 'first_name', 'last_name', 'role', 'status', 'password_new'
    ]

    # 3. เพิ่ม Field พิเศษสำหรับ "ตั้ง/เปลี่ยนรหัสผ่าน"
    form_extra_fields = {
        'password_new': PasswordField('New Password (leave blank to keep unchanged)')
    }

    # 4. ทำให้ฟิลด์ 'username' เป็นแบบอ่านอย่างเดียว (Read-only) ในหน้า Edit
    form_widget_args = {
        'username': {
            'readonly': True
        }
    }

    # 5. Logic ตอนบันทึกข้อมูล (ปรับปรุงเล็กน้อย)
    def on_model_change(self, form, model, is_created):
        """
        ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่กด Save ในฟอร์ม
        """
        # ตรวจสอบว่ามีการกรอกรหัสผ่านใหม่เข้ามาหรือไม่
        if hasattr(form, 'password_new') and form.password_new.data:
            model.set_password(form.password_new.data)
        elif is_created and (not hasattr(form, 'password_new') or not form.password_new.data):
            # ป้องกันการสร้าง user ใหม่โดยไม่มีรหัสผ่าน
            raise wtforms.validators.ValidationError('Password is required for new users.')

# -----------------------------------------------------------------------------
# View สำหรับ Model อื่นๆ ที่ต้องการการปรับแต่งเล็กน้อย
# -----------------------------------------------------------------------------
class MedicationLogAdminView(ProtectedAdminView):
    column_list = ('id', 'patient.username', 'medication_info.name', 'status', 'taken_at')
    column_filters = ('status',)
    column_searchable_list = ('patient.username', 'medication_info.name')
    can_create = False
    can_edit = False

class NotificationAdminView(ProtectedAdminView):
    column_list = ('id', 'recipient.username', 'message', 'is_read', 'created_at')
    column_filters = ('is_read',)
    column_searchable_list = ('recipient.username', 'message')
    can_create = False
    can_edit = False
    
class SystemSettingAdminView(ProtectedAdminView):
    can_create = False
    can_delete = False
    column_list = ('key', 'value', 'description')
    form_columns = ('key', 'value', 'description')
    form_widget_args = { 'key': {'readonly': True}, 'description': {'readonly': True} }

# -----------------------------------------------------------------------------
# View สำหรับจัดการ "Appointment" โดยเฉพาะ
# -----------------------------------------------------------------------------
class AppointmentAdminView(ProtectedAdminView):
    # --- *** จุดแก้ไขสำคัญ *** ---
    # เพิ่ม 'patient.username' เพื่อแสดงชื่อผู้ใช้ของผู้สูงอายุ
    column_list = ('id', 'patient.username', 'title', 'location', 'appointment_datetime')
    
    # ทำให้สามารถค้นหาจากชื่อผู้ใช้และหัวข้อได้
    column_searchable_list = ('patient.username', 'title', 'location')
    
    # เพิ่ม Filter ด้านข้างสำหรับค้นหาตามผู้ป่วย
    column_filters = ('patient',)

# -----------------------------------------------------------------------------
# View สำหรับจัดการ "HealthRecord" โดยเฉพาะ
# -----------------------------------------------------------------------------
class HealthRecordAdminView(ProtectedAdminView):
    # --- *** จุดแก้ไขสำคัญ *** ---
    # เพิ่ม 'patient.username' เพื่อแสดงชื่อผู้ใช้ของผู้สูงอายุ
    column_list = ('id', 'patient.username', 'record_date', 'systolic_bp', 'diastolic_bp', 'weight', 'pulse')
    
    # ทำให้สามารถค้นหาจากชื่อผู้ใช้ได้
    column_searchable_list = ('patient.username',)
    
    # เพิ่ม Filter ด้านข้างสำหรับค้นหาตามผู้ป่วย
    column_filters = ('patient',)

    # เราไม่ต้องการให้แอดมินสร้าง/แก้ไขข้อมูลสุขภาพโดยตรงจากหน้านี้
    can_create = False
    can_edit = False

# -----------------------------------------------------------------------------
# View สำหรับจัดการ "MasterMedicine" โดยเฉพาะ
# -----------------------------------------------------------------------------
class MasterMedicineAdminView(ProtectedAdminView):
    # (column_list, column_searchable_list เหมือนเดิม)
    column_list = ('id', 'name', 'form', 'description')
    column_searchable_list = ('name', 'description')
    
    # --- *** 2. บอกให้ View นี้ใช้ Custom Form ของเรา *** ---
    # ลบบรรทัด form_columns ออกไป
    # form_columns = ['name', 'form', 'description']
    
    # เพิ่มบรรทัดนี้เข้ามาแทน
    form = MasterMedicineForm

# -----------------------------------------------------------------------------
# View แบบ Custom ที่ไม่ผูกกับ Model โดยตรง
# -----------------------------------------------------------------------------
class CustomProtectedView(BaseView):
    def is_accessible(self):
        try:
            verify_jwt_in_request(locations=['cookies'])
            current_user_id = get_jwt_identity()
            from .models import User
            user = User.query.get(current_user_id)
            return user and user.role == 'admin'
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.admin_login'))

class StatsDashboardView(CustomProtectedView):
    @expose('/')
    def index(self):
        return self.render('admin/stats_dashboard.html')



# -----------------------------------------------------------------------------
# ฟังก์ชันสำหรับลงทะเบียน Views ทั้งหมด
# -----------------------------------------------------------------------------
def register_views(admin, db):
    """ฟังก์ชันนี้จะถูกเรียกจาก __init__.py เพื่อลงทะเบียน Admin Views ทั้งหมด"""
    from .models import User, Medication, HealthRecord, MedicationLog, Appointment, SystemSetting, Notification
    
    # Custom Views
    admin.add_view(StatsDashboardView(name="Statistics", endpoint="admin_stats", category="Dashboard"))
    # Model Views
    admin.add_view(UserAdminView(User, db.session, name="Users", endpoint="admin_user", category="Management"))
    admin.add_view(ProtectedAdminView(Medication, db.session, name="Medications", endpoint="admin_medication", category="Management"))
    admin.add_view(ProtectedAdminView(HealthRecord, db.session, name="Health Records", endpoint="admin_healthrecord", category="Management"))
    admin.add_view(ProtectedAdminView(Appointment, db.session, name="Appointments", endpoint="admin_appointment", category="Management"))
    admin.add_view(SystemSettingAdminView(SystemSetting, db.session, name="System Settings", endpoint="admin_settings", category="Configuration"))

    # Log Views
    admin.add_view(MedicationLogAdminView(MedicationLog, db.session, name="Medication Logs", endpoint="admin_medlog", category="Logs"))
    admin.add_view(NotificationAdminView(Notification, db.session, name="Notifications Log", endpoint="admin_notification", category="Logs"))