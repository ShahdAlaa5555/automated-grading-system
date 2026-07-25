import json
import re

from ollama import chat

from config import MODEL


# ==========================================================
# BUILD PROMPT
# ==========================================================

def build_prompt(ocr_text, subject):

    if subject == "chemistry":
        subject_name = "German chemistry"

    elif subject == "math":
        subject_name = "German mathematics"

    elif subject == "biology":
        subject_name = "German biology"

    elif subject == "german":
        subject_name = "German language"

    else:
        subject_name = "German"

    return f"""
You are an expert {subject_name} exam extraction AI.

Your job is to extract the COMPLETE exam from OCR text.

The OCR contains:
- printed exam questions
- handwritten student answers
- points
- formulas
- calculations
- reaction equations

IMPORTANT RULES:

- Return ONLY valid JSON.
- Do not explain.
- Do not add markdown.
- Do not translate.
- Do not summarize.
- Do not remove information.
- Preserve the original order.
- Separate printed questions from handwritten answers.

Printed exam text belongs to:
"question"

Student handwriting belongs to:
"student_answer"

Keep:
- chemical formulas (H2O, HCl, NaOH)
- equations
- numbers
- units (g, mol, L, pH)

Return this exact structure:

{{
    "exam":
    {{
        "subject":"",
        "title":"",
        "date":""
    }},

    "student":
    {{
        "name":"",
        "class":""
    }},

    "sections":
    [
        {{
            "number":1,
            "title":"",
            "points":"",

            "subquestions":
            [
                {{
                    "id":"a",
                    "points":"",
                    "question":"",
                    "student_answer":""
                }}
            ]
        }}
    ]
}}

If there is no student answer:
"student_answer": ""

If handwriting cannot be read:
"student_answer": "UNREADABLE"

OCR TEXT:

--------------------
{ocr_text}
--------------------
"""



# ==========================================================
# CLEAN MODEL OUTPUT
# ==========================================================

def clean_output(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()


# ==========================================================
# EXTRACT JSON
# ==========================================================

def extract_json(text):

    print("\n================ RAW MODEL OUTPUT ================\n")
    print(text)
    print("\n==================================================\n")

    text = clean_output(text)

    decoder = json.JSONDecoder()

    start = text.find("[")

    if start != -1:

        try:

            obj, _ = decoder.raw_decode(text[start:])

            return obj

        except Exception:
            pass

    start = text.find("{")

    if start != -1:

        try:

            obj, _ = decoder.raw_decode(text[start:])

            return obj

        except Exception:
            pass

    raise Exception("Could not extract valid JSON.")


# ==========================================================
# CALL OLLAMA
# ==========================================================

def call_llm(prompt):

    print("\nSending prompt to Qwen...\n")

    response = chat(
        model=MODEL,
        think=False,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("\n========== QWEN RAW RESPONSE ==========")
    print(response)
    print("========================================")

    return response["message"]["content"]

# ==========================================================
# PARSE EXAM
# ==========================================================

def parse_exam(lines, subject):

    if isinstance(lines, list):

        ocr_text = "\n".join(lines)

    else:

        ocr_text = str(lines)


    prompt = build_prompt(
        ocr_text, subject
    )


    raw = call_llm(
        prompt
    )


    exam = extract_json(
        raw
    )
    if "sections" in exam:
       exam = exam["sections"]


    return exam


# ==========================================================
# SAVE JSON
# ==========================================================

def save_exam(exam, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            exam,
            f,
            indent=4,
            ensure_ascii=False
        )