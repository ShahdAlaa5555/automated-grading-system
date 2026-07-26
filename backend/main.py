import os
import json

from cleaner import run_pipeline
from parser import parse_exam, save_exam
from database import get_connection
from config import OUTPUT_FOLDER


# ==================================================
# CREATE OUTPUT FOLDER
# ==================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ==================================================
# MAIN FUNCTION
# ==================================================

def process_exam(file_path):

    print("Running OCR...")

    ocr_lines = run_pipeline(file_path)

    print("Parsing exam with Qwen...")

    exam = parse_exam(ocr_lines)

    output_file = os.path.join(
        OUTPUT_FOLDER,
        "questions.json"
    )

    save_exam(
        exam,
        output_file
    )

    print("questions.json created successfully")

    print("\nExam extracted:")
    print(
        json.dumps(
            exam,
            indent=4,
            ensure_ascii=False
        )
    )

    return exam


# ==================================================
# RUN ONLY IF EXECUTED DIRECTLY
# ==================================================

if __name__ == "__main__":

    from config import INPUT_FILE

    process_exam(INPUT_FILE)