import json
import re

from ollama import chat
from config import MODEL


# ==========================================
# Prompt
# ==========================================

def build_prompt(ocr_text):

    return f"""
Du bist ein erfahrener deutscher Chemielehrer.

Die folgende OCR stammt von einer ausgefüllten Chemie-Klassenarbeit.

Die OCR enthält sowohl:
- gedruckte Prüfungsfragen
- handschriftliche Schülerantworten

Deine Aufgabe:

Extrahiere die komplette Prüfungsstruktur.

Für jede Aufgabe gib zurück:

- number
- question
- subquestions

Jede Teilaufgabe muss enthalten:

- id
- question
- student_answer

WICHTIGE REGELN

1. Trenne gedruckte Fragen und Schülerantworten.
2. Erfinde niemals Informationen.
3. Korrigiere nur offensichtliche OCR-Fehler
   (z.B. Losung -> Lösung, MgClz -> MgCl2).
4. Ändere niemals die Bedeutung der Schülerantwort.
5. Chemische Gleichungen unverändert übernehmen.
6. Falls keine Antwort vorhanden ist:
   student_answer = ""
7. Keine Erklärungen.
8. Kein Markdown.
9. Keine Kommentare.
10. Antworte NUR mit gültigem JSON.

Beispiel:

[
  {{
    "number": 1,
    "question": "Säuren und Basen",
    "subquestions": [
      {{
        "id": "a",
        "question": "Nenne jeweils vier Eigenschaften von Säuren und Basen.",
        "student_answer": "- schmecken sauer"
      }}
    ]
  }}
]

OCR:

{ocr_text}
"""


# ==========================================
# Extract JSON safely
# ==========================================

def extract_json(text):

    text = text.strip()

    # Remove markdown if present
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    # Find first JSON array
    start = text.find("[")

    if start == -1:
        raise Exception("No JSON array found.")

    text = text[start:]

    decoder = json.JSONDecoder()

    try:
        obj, _ = decoder.raw_decode(text)
        return obj

    except json.JSONDecodeError as e:

        print("\n========= RAW MODEL OUTPUT =========")
        print(text)
        print("====================================\n")

        raise Exception(f"Invalid JSON: {e}")


# ==========================================
# Parse OCR
# ==========================================

def parse_exam(lines):

    ocr_text = "\n".join(lines)

    prompt = build_prompt(ocr_text)

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

    raw = response["message"]["content"]

    print("\n========== RAW LLM OUTPUT ==========\n")
    print(raw)
    print("\n===================================\n")

    return extract_json(raw)


# ==========================================
# Save
# ==========================================

def save_exam(exam, path):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            exam,
            f,
            indent=4,
            ensure_ascii=False
        )