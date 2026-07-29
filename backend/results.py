"""
Routes backing the /results/:submissionId page.

  GET   /results/{submission_id}
  PATCH /question-results/{question_result_id}

Wire this into your app with, e.g.:

    from fastapi import FastAPI
    from results import router as results_router

    app = FastAPI()
    app.include_router(results_router)

SECURITY NOTE: `teachers.password` is currently stored in plain text.
These routes don't touch auth, but flagging it here since it's a real risk —
passwords should be hashed (e.g. with bcrypt/passlib) before this app
handles any real student data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import mysql.connector

from database import get_connection

router = APIRouter(tags=["results"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class QuestionResultOut(BaseModel):
    question_result_id: int
    question_number: int
    question_text: str
    student_answer: str | None
    is_correct: bool | None
    feedback: str | None
    edited: bool


class SubmissionOut(BaseModel):
    student_name: str | None
    subject: str
    filename: str


class ResultsResponse(BaseModel):
    submission: SubmissionOut
    questions: list[QuestionResultOut]


class QuestionResultUpdate(BaseModel):
    is_correct: bool
    feedback: str = Field(..., min_length=1)


class QuestionResultUpdateOut(BaseModel):
    question_result_id: int
    is_correct: bool
    feedback: str
    edited: bool


# ---------------------------------------------------------------------------
# GET /results/{submission_id}
# ---------------------------------------------------------------------------

@router.get("/results/{submission_id}", response_model=ResultsResponse)
def get_results(submission_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                s.submission_id,
                s.subject,
                s.filename,
                st.full_name AS student_name
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.student_id
            WHERE s.submission_id = %s
            """,
            (submission_id,),
        )
        submission_row = cursor.fetchone()

        if submission_row is None:
            raise HTTPException(status_code=404, detail="Submission not found")

        cursor.execute(
            """
            SELECT
                question_result_id,
                question_number,
                question_text,
                student_answer,
                COALESCE(teacher_is_correct, ai_is_correct) AS is_correct,
                COALESCE(teacher_feedback, ai_feedback) AS feedback,
                (teacher_is_correct IS NOT NULL) AS edited
            FROM question_results
            WHERE submission_id = %s
            ORDER BY question_number ASC
            """,
            (submission_id,),
        )
        question_rows = cursor.fetchall()

        for row in question_rows:
            row["is_correct"] = bool(row["is_correct"]) if row["is_correct"] is not None else None
            row["edited"] = bool(row["edited"])

        return {
            "submission": {
                "student_name": submission_row["student_name"],
                "subject": submission_row["subject"],
                "filename": submission_row["filename"],
            },
            "questions": question_rows,
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# PATCH /question-results/{question_result_id}
# ---------------------------------------------------------------------------

@router.patch("/question-results/{question_result_id}", response_model=QuestionResultUpdateOut)
def update_question_result(question_result_id: int, update: QuestionResultUpdate):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE question_results
            SET teacher_is_correct = %s,
                teacher_feedback = %s,
                edited_at = NOW()
            WHERE question_result_id = %s
            """,
            (update.is_correct, update.feedback, question_result_id),
        )

        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Question result not found")

        conn.commit()

        return {
            "question_result_id": question_result_id,
            "is_correct": update.is_correct,
            "feedback": update.feedback,
            "edited": True,
        }

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()