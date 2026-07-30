# cleaner_easyocr.py

import easyocr
from pdf2image import convert_from_path
import os
import re

from config import OUTPUT_FOLDER


# ==================================================
# CONFIG
# ==================================================

OUTPUT_TEXT = os.path.join(
    OUTPUT_FOLDER,
    "exam_clean.txt"
)

TEMP_FOLDER = "temp_images"

# CHANGE THIS TO YOUR POPPLER LOCATION
POPPLER_PATH = r"C:\Users\menna\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"

# ==================================================
# OCR MODEL
# ==================================================

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


# ==================================================
# CLEANING
# ==================================================

def clean_text(text):

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    corrections = {

        "clectron": "electron",
        "clcctron": "electron",
        "ncutron": "neutron",
        "cmpirical": "empirical",
        "e) xamination": "examination",
        "e) lectron": "electron",

    }

    for wrong, right in corrections.items():

        text = text.replace(
            wrong,
            right
        )

    return text


# ==================================================
# PDF -> IMAGES
# ==================================================

def pdf_to_images(pdf_path):

    os.makedirs(
        TEMP_FOLDER,
        exist_ok=True
    )

    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    image_paths = []

    for i, page in enumerate(pages):

        image_path = os.path.join(
            TEMP_FOLDER,
            f"page_{i+1}.jpg"
        )

        page.save(
            image_path,
            "JPEG"
        )

        image_paths.append(
            image_path
        )

    return image_paths


# ==================================================
# OCR
# ==================================================

def run_ocr(image_path):

    result = reader.readtext(
        image_path,
        detail=1
    )

    lines = []

    print(f"\n===== Reading {image_path} =====\n")

    for detection in result:

        bbox, text, confidence = detection

        text = clean_text(text)

        if not text:
            continue

        print(f"{confidence:.2f} | {text}")

        lines.append(text)

    return lines


# ==================================================
# PREPROCESS
# ==================================================

def preprocess_lines(lines):

    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "klassenarbeiten.de" in line.lower():
            continue

        if line in [
            "Name:",
            "Punkte:",
            "Note:"
        ]:
            continue

        if re.fullmatch(
            r"[HI\-|/\\]+",
            line
        ):
            continue

        cleaned.append(line)

    return cleaned


# ==================================================
# MAIN PIPELINE
# ==================================================

def run_pipeline(input_file):

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    if input_file.lower().endswith(".pdf"):

        images = pdf_to_images(
            input_file
        )

    else:

        images = [
            input_file
        ]

    all_lines = []

    for image in images:

        all_lines.extend(
            run_ocr(image)
        )

    all_lines = preprocess_lines(
        all_lines
    )

    with open(
        OUTPUT_TEXT,
        "w",
        encoding="utf-8"
    ) as f:

        for line in all_lines:

            f.write(line + "\n")

    print(
        "\nOCR saved to",
        OUTPUT_TEXT
    )

    return all_lines