import json
from ollama import chat

from config import MODEL


# =====================================================
# GRADE ONE QUESTION
# =====================================================

def grade_answer(
    question,
    student_answer,
    reference_answer,
    max_points,
    subject,
):

    if subject == "chemistry":
        teacher = "deutscher Chemielehrer"

    elif subject == "math":
        teacher = "deutscher Mathematiklehrer"

    elif subject == "biology":
        teacher = "deutscher Biologielehrer"

    elif subject == "german":
        teacher = "deutscher Deutschlehrer"

    else:
        teacher = "deutscher Lehrer"

    prompt = f"""
Du bist ein erfahrener {teacher}.

Bewerte die Schülerantwort.

Aufgabe:
{question}

Schülerantwort:
{student_answer}

Musterlösung:
{reference_answer}

Maximale Punkte:
{max_points}

Bewertungsregeln:

- Vergib eine ganze Zahl zwischen 0 und {max_points}.
- Überschreite niemals die maximale Punktzahl.
- Vergib Teilpunkte, wenn Teile der Antwort richtig sind.
- Bewerte wie ein echter deutscher Lehrer.
- Kleine OCR-Fehler ignorieren.
- Rechtschreibfehler ignorieren.
- Beurteile nur die fachliche Richtigkeit.
- Keine Erklärung deines Denkprozesses.

Antworte ausschließlich als JSON:

{{
    "score": 0,
    "feedback": ""
}}
"""

    response = chat(
        model=MODEL,
        think=False,
        options={
            "temperature": 0
        },
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response["message"]["content"]

    print("\n====== QWEN RESPONSE ======")
    print(result)
    print("===========================\n")

    return extract_json(result)


# =====================================================
# EXTRACT JSON
# =====================================================

def extract_json(text):

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return {
            "score": 0,
            "feedback": "Ungültige Modellantwort"
        }

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)

    except Exception:
        return {
            "score": 0,
            "feedback": "JSON konnte nicht gelesen werden"
        }


# =====================================================
# GRADE COMPLETE EXAM
# =====================================================

def grade_exam(exam, subject):

    total_score = 0
    total_points = 0

    for section in exam:

        section_points = int(section.get("points", 1) or 1)

        for question in section["subquestions"]:

            print(
                f"Grading {section['number']}{question.get('id', '')}..."
            )

            grading = grade_answer(
                question.get("question", ""),
                question.get("student_answer", ""),
                question.get("reference_answer", ""),
                section_points,
                subject,
            )
            print("\n========================")
            print("QUESTION :", question.get("question", ""))
            print("STUDENT :", question.get("student_answer", ""))
            print("REFERENCE :", question.get("reference_answer", ""))
            print("GRADING :", grading)
            print("========================\n")

            score = grading.get("score", 0)

            if score < 0:
                score = 0

            if score > section_points:
                score = section_points

            # Save grading back into the question
            question["score"] = score
            question["max_points"] = section_points
            question["feedback"] = grading.get("feedback", "")
            question["is_correct"] = (score == section_points)

            total_score += score
            total_points += section_points

            print(
                f"Score: {score}/{section_points}"
            )

    print("\n====================")
    print("FINAL RESULT")
    print("====================")
    print(f"Score: {total_score}/{total_points}")

    if total_points > 0:
        percentage = round(
            total_score / total_points * 100,
            2,
        )
    else:
        percentage = 0

    print(f"Percentage: {percentage}%")

    return exam