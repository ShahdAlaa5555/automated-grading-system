from cv2 import data
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

app = FastAPI()


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
    #by shahd 

    submission_id = cursor.lastrowid 
    conn.commit()

    cursor.close()
    conn.close()

    # ==============================
    # OCR
    # ==============================
    update_progress(submission_id, "Processing", 20)
    lines = run_pipeline(file_path)

    
    update_progress(submission_id, "OCR Complete", 40)
    # ==============================
    # Parse exam using Qwen
    # ==============================
    update_progress(submission_id, "Grading", 80)
    exam = parse_exam(lines, subject)


    # ==============================
    # Generate reference answers
    # ==============================

    exam = generate_answers(exam, subject)

    update_progress(submission_id, "Completed", 100)


    return {
    "submission_id": submission_id,
    "exam": exam
}
#Menna: for login
@app.post("/login")
@app.post("/login")
def login(data: LoginRequest):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM teachers
        WHERE email = %s
        """,
        (data.email,)
    )

    teacher = cursor.fetchone()

    if teacher is None:

        response = {
            "success": False,
            "message": "Invalid email or password"
        }

    elif teacher["password"] != data.password:

        response = {
            "success": False,
            "message": "Invalid email or password"
        }

    else:

        response = {
            "success": True,
            "message": "Login successful"
        }

    cursor.close()
    conn.close()

    return response
    