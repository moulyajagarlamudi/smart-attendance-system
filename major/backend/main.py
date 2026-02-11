from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, constr
import firebase_admin
from firebase_admin import credentials, db
import datetime
from typing import List
import uvicorn
import bcrypt
import re
import secrets
from fastapi import File, UploadFile, Form
import base64
import os

# ------------------- FIREBASE INIT -------------------
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://major-f5939-default-rtdb.firebaseio.com/"  # ✅ ensure trailing slash
    })

app = FastAPI()

@app.get("/student/{rollno}")
def get_student(rollno: str):
    ref = db.reference(f"students/{rollno}")
    student = ref.get()
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    
    
# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- MODELS -------------------
class Student(BaseModel):
    roll: str
    name: str

class AttendanceData(BaseModel):
    section: str
    date: str
    present: List[Student]
    absent: List[Student]

class StudentRegister(BaseModel):
    roll: str
    name: str
    email: EmailStr
    password: str

class StudentLogin(BaseModel):
    roll: str
    password: str

class TeacherRegister(BaseModel):
    teacher_id: str
    name: str
    email: EmailStr
    phone: str
    department: str
    password: str

class TeacherLogin(BaseModel):
    teacher_id: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: constr(min_length=8)

# ------------------- PASSWORD VALIDATION -------------------
password_pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")

# ------------------- STUDENT REGISTER -------------------
@app.post("/register-student")
async def register_student(student: StudentRegister):
    if not password_pattern.match(student.password):
        raise HTTPException(status_code=400,
                            detail="Weak password: must be 8+ chars, include uppercase, lowercase, number and special character.")

    students_ref = db.reference("students")
    all_students = students_ref.get() or {}

    if students_ref.child(student.roll).get() is not None:
        raise HTTPException(status_code=400, detail="Roll number already registered.")

    for _, s in (all_students.items() if isinstance(all_students, dict) else []):
        if s.get("email") == student.email:
            raise HTTPException(status_code=400, detail="Email already registered.")

    hashed = bcrypt.hashpw(student.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    students_ref.child(student.roll).set({
        "roll": student.roll,
        "name": student.name,
        "email": student.email,
        "password": hashed,
        "registeredAt": datetime.datetime.utcnow().isoformat(),
        "reset_token": None,
        "reset_token_created_at": None
    })

    return {"success": True, "message": "Student registered successfully"}

# ------------------- STUDENT LOGIN -------------------
@app.post("/login-student")
async def login_student(login: StudentLogin):
    students_ref = db.reference("students")
    student_node = students_ref.child(login.roll).get()

    if not student_node:
        return {"success": False, "message": "Roll number not found"}

    stored_hash = student_node.get("password")
    if not stored_hash:
        return {"success": False, "message": "No password set for this user"}

    try:
        match = bcrypt.checkpw(login.password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        match = False

    if not match:
        return {"success": False, "message": "Invalid password"}

    student_data = {
        "roll": student_node.get("roll"),
        "name": student_node.get("name"),
        "email": student_node.get("email")
    }
    return {"success": True, "message": "Login successful", "student": student_data}

# ------------------- TEACHER REGISTER -------------------
@app.post("/register-teacher")
async def register_teacher(teacher: TeacherRegister):
    if not password_pattern.match(teacher.password):
        raise HTTPException(status_code=400,
                            detail="Weak password: must be 8+ chars, include uppercase, lowercase, number and special character.")

    teachers_ref = db.reference("teachers")

    # Check if teacherId already exists
    if teachers_ref.child(teacher.teacher_id).get() is not None:
        raise HTTPException(status_code=400, detail="Teacher ID already exists")

    # Check email uniqueness
    all_teachers = teachers_ref.get() or {}
    for _, t in (all_teachers.items() if isinstance(all_teachers, dict) else []):
        if t.get("email") == teacher.email:
            raise HTTPException(status_code=400, detail="Email already registered.")

    hashed = bcrypt.hashpw(teacher.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    teacher_data = {
        "teacher_id": teacher.teacher_id,
        "name": teacher.name,
        "email": teacher.email,
        "phone": teacher.phone,
        "department": teacher.department,
        "password": hashed,
        "registeredAt": datetime.datetime.utcnow().isoformat()
    }

    teachers_ref.child(teacher.teacher_id).set(teacher_data)
    return {"success": True, "message": "Teacher registered successfully"}

# ------------------- TEACHER LOGIN -------------------
@app.post("/login-teacher")
async def login_teacher(login: TeacherLogin):
    teachers_ref = db.reference("teachers")
    teacher_node = teachers_ref.child(login.teacher_id).get()

    if not teacher_node:
        return {"success": False, "message": "Teacher ID not found"}

    stored_hash = teacher_node.get("password")
    if not stored_hash:
        return {"success": False, "message": "No password set for this teacher"}

    try:
        match = bcrypt.checkpw(login.password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        match = False

    if not match:
        return {"success": False, "message": "Invalid password"}

    teacher_data = {
        "teacher_id": teacher_node.get("teacher_id"),
        "name": teacher_node.get("name"),
        "email": teacher_node.get("email"),
        "phone": teacher_node.get("phone"),
        "department": teacher_node.get("department"),
    }
    return {"success": True, "message": "Login successful", "teacher": teacher_data}

# ------------------- SUBMIT ATTENDANCE -------------------
@app.post("/submit-attendance")
async def submit_attendance(data: AttendanceData):
    attendance_data = {
        "section": data.section,
        "date": data.date,
        "present": [{"roll": s.roll, "name": s.name} for s in data.present],
        "absent": [{"roll": s.roll, "name": s.name} for s in data.absent],
        "presentCount": len(data.present),
        "absentCount": len(data.absent),
        "totalStudents": len(data.present) + len(data.absent),
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        attendance_ref = db.reference(f"attendance/{data.section}/{data.date}")
        attendance_ref.set(attendance_data)
        return {"success": True, "message": f"Attendance submitted successfully for Section {data.section} on {data.date}!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving to Firebase: {str(e)}")

# ------------------- GET ATTENDANCE BY DATE -------------------
@app.get("/get-attendance/{section}/{date}")
async def get_attendance(section: str, date: str):
    try:
        attendance_ref = db.reference(f"attendance/{section}/{date}")
        data = attendance_ref.get()
        if data:
            return {"success": True, "data": data}
        else:
            return {"success": False, "message": "No attendance data found for this date"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving attendance: {str(e)}")

# ------------------- GET SECTION REPORTS -------------------
@app.get("/get-section-reports/{section}")
async def get_section_reports(section: str):
    try:
        section_ref = db.reference(f"attendance/{section}")
        data = section_ref.get()
        if data:
            reports = []
            for date, attendance in data.items():
                attendance["date"] = date
                reports.append(attendance)
            reports.sort(key=lambda x: x["date"], reverse=True)
            return {"success": True, "reports": reports}
        else:
            return {"success": False, "reports": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")

# ------------------- FORGOT PASSWORD (STUDENT) -------------------
@app.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    students_ref = db.reference("students")
    all_students = students_ref.get() or {}

    user_roll = None
    for roll, student in (all_students.items() if isinstance(all_students, dict) else []):
        if student.get("email") == request.email:
            user_roll = roll
            break

    if not user_roll:
        return {"success": True, "message": "If the email is registered, a reset token has been sent."}

    reset_token = secrets.token_urlsafe(32)
    students_ref.child(user_roll).update({
        "reset_token": reset_token,
        "reset_token_created_at": datetime.datetime.utcnow().isoformat()
    })

    # TODO: integrate email sending here
    return {"success": True, "message": "If the email is registered, a reset token has been sent."}

# ------------------- RESET PASSWORD (STUDENT) -------------------
@app.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    if not password_pattern.match(request.new_password):
        raise HTTPException(status_code=400,
                            detail="Weak password: must be 8+ chars, include uppercase, lowercase, number and special character.")

    students_ref = db.reference("students")
    all_students = students_ref.get() or {}

    user_roll = None
    user_data = None
    for roll, student in (all_students.items() if isinstance(all_students, dict) else []):
        if student.get("email") == request.email:
            user_roll = roll
            user_data = student
            break

    if not user_roll:
        raise HTTPException(status_code=400, detail="Invalid email or reset token")

    stored_token = user_data.get("reset_token")
    token_time_str = user_data.get("reset_token_created_at")

    if not stored_token or stored_token != request.reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if token_time_str:
        token_time = datetime.datetime.fromisoformat(token_time_str)
        if datetime.datetime.utcnow() - token_time > datetime.timedelta(hours=1):
            raise HTTPException(status_code=400, detail="Reset token expired")

    hashed = bcrypt.hashpw(request.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    students_ref.child(user_roll).update({
        "password": hashed,
        "reset_token": None,
        "reset_token_created_at": None
    })

    return {"success": True, "message": "Password has been reset successfully."}

@app.get("/teacher/{teacher_id}")
def get_teacher(teacher_id: str):
    ref = db.reference(f"teachers/{teacher_id}")
    data = ref.get()
    if data:
        return data
    return {"error": "Teacher not found"}

@app.get("/attendance/latest/{teacher_id}")
def get_latest_attendance(teacher_id: str):
    ref = db.reference(f"attendance/{teacher_id}")
    records = ref.get()
    if not records:
        return []
    latest = list(records.values())[-5:]  # last 5 records
    return latest

os.makedirs("uploads/assignments", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ------------------- UPLOAD ASSIGNMENT (LOCAL STORAGE) -------------------
@app.post("/upload-assignment")
async def upload_assignment(
    roll: str = Form(...),
    subjectName: str = Form(...),
    subjectCode: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Save file locally
        file_path = f"uploads/assignments/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Generate local access URL
        file_url = f"http://localhost:8000/uploads/assignments/{file.filename}"

        # Store info in Firebase
        assignment_data = {
            "roll": roll,
            "subjectName": subjectName,
            "subjectCode": subjectCode,
            "fileName": file.filename,
            "fileUrl": file_url,
            "uploadedAt": datetime.datetime.utcnow().isoformat()
        }

        db.reference("assignments").push(assignment_data)

        return {
            "success": True,
            "message": "Assignment uploaded successfully!",
            "fileUrl": file_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
@app.get("/assignments")
async def get_assignments():
    """Return all uploaded assignments from Firebase."""
    ref = db.reference("assignments")
    data = ref.get()
    if not data:
        return {"success": False, "assignments": []}

    assignments = list(data.values())
    assignments.sort(key=lambda x: x.get("uploadedAt", ""), reverse=True)
    return {"success": True, "assignments": assignments}


# ------------------- MAIN -------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


