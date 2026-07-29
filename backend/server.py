from cv2 import data
import torch

from fastapi import FastAPI, UploadFile, File,HTTPException
#Menna: Evidently, I need this to hardcode a teacher to test the login.
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from cleaner import run_pipeline
from llm_parser import parse_exam
from reference_generator import generate_answers
from database import get_connection

#Menna: just for login testing
class LoginRequest(BaseModel):
    email: str
    password: str
from german.adapter import analyze_german_exam


app = FastAPI()

from results import router as results_router

app.include_router(results_router)
def _extract_teacher_name(teacher_record):
    for key in ("name", "full_name", "teacher_name", "display_name"):
        value = teacher_record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    first_name = teacher_record.get("first_name")
    last_name = teacher_record.get("last_name")
    if isinstance(first_name, str) and first_name.strip() and isinstance(last_name, str) and last_name.strip():
        return f"{first_name.strip()} {last_name.strip()}"

    return "Teacher"


def _extract_teacher_subjects(teacher_record, fallback_profile):
    for key in ("subjects", "subjects_taught", "teaching_subjects", "subject_names"):
        value = teacher_record.get(key)
        if isinstance(value, list):
            subjects = [str(item).strip() for item in value if str(item).strip()]
            if subjects:
                return subjects
        elif isinstance(value, str) and value.strip():
            subjects = [item.strip() for item in value.split(",") if item.strip()]
            if subjects:
                return subjects

    if fallback_profile and fallback_profile.get("subjects"):
        return fallback_profile["subjects"]

    return []

def get_teacher_courses(cursor, teacher_id):
    cursor.execute(
        """
        SELECT c.course_name
        FROM teacher_courses AS tc
        INNER JOIN courses AS c
            ON c.course_id = tc.course_id
        WHERE tc.teacher_id = %s
        ORDER BY c.course_name
        """,
        (teacher_id,)
    )

    course_rows = cursor.fetchall()

    return [
        row["course_name"]
        for row in course_rows
    ]

# ==========================================
# Allow React to communicate with FastAPI
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#by shahd 
def update_progress(submission_id, status, progress):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE submissions
        SET status=%s,
            progress=%s
        WHERE submission_id=%s
        """,
        (
            status,
            progress,
            submission_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()



@app.get("/submission/{submission_id}")
def get_submission(submission_id: int):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            submission_id,
            status,
            progress
        FROM submissions
        WHERE submission_id=%s
        """,
        (submission_id,)
    )

    submission = cursor.fetchone()

    cursor.close()
    conn.close()

    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission
@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.post("/{subject}/upload")
async def upload_exam(subject: str,file: UploadFile = File(...)):

    # ==============================
    # Save uploaded file
    # ==============================

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

  # ==============================
    # Save submission in MySQL
    # ==============================

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Submissions
    (subject, filename, file_path, status, progress)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            subject,
            file.filename,
            file_path,
            "Uploaded",
            0
        )
    )
    
    submission_id = cursor.lastrowid 
    conn.commit()

    cursor.close()
    conn.close()

    normalized_subject = subject.strip().lower()

    if normalized_subject == "german":
        update_progress(
            submission_id,
            "Processing",
            20,
        )

        exam = analyze_german_exam(file_path)

        update_progress(
            submission_id,
            "OCR Complete",
            60,
        )

        update_progress(
            submission_id,
            "Grading",
            80,
        )

    else:
        update_progress(
            submission_id,
            "Processing",
            20,
        )

        lines = run_pipeline(file_path)

        update_progress(
            submission_id,
            "OCR Complete",
            40,
        )

        update_progress(
            submission_id,
            "Grading",
            80,
        )

        exam = parse_exam(lines, normalized_subject)
        exam = generate_answers(
            exam,
            normalized_subject,
        )
        save_results(submission_id, exam)
    update_progress(
        submission_id,
        "Released",
        100,
    )
    print(exam)
    return {
    "submission_id": submission_id,
    "exam": exam
}

def save_results(submission_id, exam):
    conn = get_connection()
    cursor = conn.cursor()

    for q in exam["questions"]:

        cursor.execute(
            """
            INSERT INTO question_results
            (
                submission_id,
                question_number,
                question_text,
                student_answer,
                ai_is_correct,
                ai_feedback
            )
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (
                submission_id,
                q["number"],
                q["question"],
                q["student_answer"],
                q["is_correct"],
                q["feedback"]
            )
        )

    conn.commit()
    cursor.close()
    conn.close()



@app.post("/login")
def login(data: LoginRequest):
    email = data.email.strip().lower()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                teacher_id,
                full_name,
                email,
                password
            FROM teachers
            WHERE email = %s
            """,
            (email,)
        )

        teacher = cursor.fetchone()

        if teacher is None or teacher["password"] != data.password:
            return {
                "success": False,
                "message": "Invalid email or password",
            }

        teacher_subjects = get_teacher_courses(
            cursor,
            teacher["teacher_id"]
        )

        return {
            "success": True,
            "message": "Login successful",
            "teacher": {
                "id": teacher["teacher_id"],
                "name": teacher["full_name"],
                "email": teacher["email"],
                "subjects": teacher_subjects,
            },
        }

    finally:
        cursor.close()
        conn.close()