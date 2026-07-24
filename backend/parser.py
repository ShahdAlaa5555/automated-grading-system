import json
import re

from ollama import chat

from config import MODEL


# ==========================================================
# BUILD PROMPT
# ==========================================================

def build_prompt(ocr_text):

    return f"""
You are an expert German chemistry teacher.

Your task is to extract a complete chemistry exam from OCR text.

The OCR contains:
- printed exam questions
- handwritten student answers
- points
- chemistry formulas
- calculations
- reaction equations

You must separate:

QUESTION:
Only the printed task/question.

STUDENT ANSWER:
Only what the student wrote as a solution.

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do not add explanations.
3. Do not use markdown.
4. Preserve German language.
5. Preserve chemical formulas:
   H2O, HCl, NaOH, MgCl2, NaCl, CaCO3
6. Preserve calculations and units.
7. Keep original exam order.

Extraction rules:

- "Aufgabe 1", "1.", "2.", etc. are sections.
- "a)", "b)", "c)" are subquestions.
- Text describing what to do belongs to "question".
- Solutions after the question belong to "student_answer".
- Bullet points answering the question belong to "student_answer".
- Reaction equations written by the student belong to "student_answer".
- Calculations after:
  Gegeben:
  Gesucht:
  Formel:
  =
  belong to "student_answer".

If no answer exists:
"student_answer": ""

If handwriting cannot be read:
"student_answer": "UNREADABLE"


Return exactly this format:

{{
    "exam":
    {{
        "subject":"Chemie",
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


    start = text.find("{")

    if start == -1:
        raise Exception(
            "No JSON object found in model output"
        )


    try:

        obj, _ = decoder.raw_decode(
            text[start:]
        )

        return obj


    except Exception as e:

        print("JSON ERROR:")
        print(e)

        raise Exception(
            "Could not extract valid JSON"
        )



# ==========================================================
# CALL QWEN
# ==========================================================

def call_llm(prompt):

    print("\nSending prompt to Qwen...\n")


    response = chat(

        model=MODEL,

        format="json",

        think=False,

        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )


    return response["message"]["content"]



# ==========================================================
# MAIN PARSER FUNCTION
# ==========================================================

def parse_exam(lines):


    if isinstance(lines, list):

        ocr_text = "\n".join(lines)

    else:

        ocr_text = str(lines)



    prompt = build_prompt(
        ocr_text
    )


    raw_response = call_llm(
        prompt
    )


    exam_json = extract_json(
        raw_response
    )


    return exam_json



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



# ==========================================================
# TEST RUN (OPTIONAL)
# ==========================================================

if __name__ == "__main__":


    with open(
        "outputs/exam_clean.txt",
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read()



    result = parse_exam(
        text
    )


    save_exam(
        result,
        "outputs/questions.json"
    )


    print(
        "questions.json created successfully"
    )