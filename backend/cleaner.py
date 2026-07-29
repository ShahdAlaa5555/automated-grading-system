from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import os
import re

from config import  OUTPUT_FOLDER


OUTPUT_TEXT = os.path.join(
    OUTPUT_FOLDER,
    "exam_clean.txt"
)

TEMP_FOLDER = "temp_images"



# ==================================================
# OCR MODEL
# ==================================================

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="german"
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
        poppler_path=r"C:\Users\User\OneDrive\Desktop\poppler-26.02.0\Library\bin"
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

    result = ocr.ocr(
        image_path,
        cls=True
    )


    lines = []


    if result and result[0]:

        print(
            f"\n===== Reading {image_path} =====\n"
        )


        for line in result[0]:


            text = clean_text(
                line[1][0]
            )


            confidence = line[1][1]


            if not text:
                continue


            print(
                f"{confidence:.2f} | {text}"
            )


            lines.append(
                text
            )


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


        cleaned.append(
            line
        )


    return cleaned




# ==================================================
# MAIN PIPELINE FUNCTION
# ==================================================

def run_pipeline(input_file):


    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )


    # PDF or image?

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



    # save OCR text

    with open(
        OUTPUT_TEXT,
        "w",
        encoding="utf-8"
    ) as f:


        for line in all_lines:

            f.write(
                line + "\n"
            )



    print(
        "\nOCR saved to",
        OUTPUT_TEXT
    )


    return all_lines
