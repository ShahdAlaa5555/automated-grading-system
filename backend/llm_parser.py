import json
import re

from ollama import chat

from config import MODEL
#Menna moved these imports here because code was unreachable.
import json
from json import JSONDecoder


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
#Menna Shaaban: I will comment the old implementation of this method to fix an exception I am having. I will keep it, but note that the current version is changed to avoid the exception on fetching the curly brackets. Worry not :)
# def extract_json(text):

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

#Menna: I will replace this for the sake of attempting to upload. I will keep it commented in case the change is problematic.
# def extract_json(text: str):
    """
    Extract the first valid JSON object from a model response.
    """

    decoder = JSONDecoder()

    start = text.find("{")

    while start != -1:

        try:
            obj, end = decoder.raw_decode(text[start:])
            return obj

        except json.JSONDecodeError:

            start = text.find("{", start + 1)

    raise Exception("Could not extract valid JSON.")



# def extract_json(text: str):

#     decoder = JSONDecoder()

#     start = text.find("{")

#     while start != -1:

#         try:
#             obj, end = decoder.raw_decode(text[start:])
#         #Menna: Changed this to accomodate both formats.
#             # if (
#             #     isinstance(obj, dict)
#             #     and "sections" in obj
#             # ):
#             #     return obj
#             if not isinstance(obj, dict):
#                 continue

# # Old format
#             if "sections" in obj:
#                 return obj

# # New format
#             if "exam" in obj and isinstance(obj["exam"], dict):
#                 if "sections" in obj["exam"]:
#                     return obj["exam"]

#         except json.JSONDecodeError:
#             pass

#         start = text.find("{", start + 1)
#     print(repr(text))
#     raise Exception("Could not find exam JSON.")
#Added by Menna to temporarily test
def extract_json(text: str):

    print("========== extract_json received ==========")
    print(repr(text))
    print("==========================================")

    decoder = JSONDecoder()

    start = text.find("{")

    while start != -1:

        try:
            obj, end = decoder.raw_decode(text[start:])

            print("Parsed object keys:", obj.keys())

            if isinstance(obj, dict):

                if "sections" in obj:
                    print("Matched root sections")
                    return obj

                if (
                    "exam" in obj
                    and isinstance(obj["exam"], dict)
                    and "sections" in obj["exam"]
                ):
                    print("Matched nested exam")
                    return obj["exam"]

        except json.JSONDecodeError as e:
            print("JSON decode failed:", e)

        start = text.find("{", start + 1)

    raise Exception("Could not find exam JSON.")
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
    #Menna debugging 
    with open("llm_output.txt", "w", encoding="utf-8") as f:
        f.write(raw)
    #Menna: debugging ;') 
    print("\n================ RAW STRING ================\n")
    print(raw)
    print("\n===========================================\n")
    print("\n========== RAW RESPONSE ==========")
    print(raw)      # or whatever variable you're passing to extract_json
    print(type(raw))
    print("=================================\n")
    exam = extract_json(
        raw
    )
    #Menna Shaaban: I will remove this below if-condition to accomodate receiving the whole exam. Feel free to return it if problematic.
    # if "sections" in exam:
    #    exam = exam["sections"]


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