from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from cleaner import run_pipeline
from llm_parser import parse_exam
from reference_generator import generate_answers
from database import get_connection


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
    # OCR
    # ==============================

    lines = run_pipeline(file_path)


    # ==============================
    # Parse exam using Qwen
    # ==============================

    exam = parse_exam(lines, subject)


    # ==============================
    # Generate reference answers
    # ==============================

    exam = generate_answers(exam, subject)


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

    conn.commit()

    cursor.close()
    conn.close()


    return exam