import json
from ollama import chat

from config import MODEL


# ======================================
# Load JSON
# ======================================

def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ======================================
# Grade one subquestion
# ======================================

def grade_answer(question, reference_answer, student_answer, subject):

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

Bewerte die Antwort eines Schülers.

Frage:
{question}

Musterlösung:
{reference_answer}

Schülerantwort:
{student_answer}

Bewertungsregeln:

- Bewerte nur die fachliche Richtigkeit.
- Ignoriere Rechtschreibfehler.
- Ignoriere OCR-Fehler, wenn die Bedeutung eindeutig ist.
- Vergib Teilpunkte, wenn Teile der Antwort richtig sind.
- Gib kurzes Feedback auf Deutsch.

WICHTIG:

Antworte ausschließlich mit einem JSON Objekt.

Keine Analyse.
Keine Erklärung.
Keine Gedanken.
Kein Markdown.
Keine ```.

Format:

{{
    "score": 0,
    "feedback": "kurzes Feedback"
}}
"""

    response = chat(
        model=MODEL,
        options={
            "temperature": 0
        },
        think=False,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    print("\n========== RAW QWEN RESPONSE ==========")
    print(answer)
    print("=======================================\n")

    return answer


# ======================================
# Extract JSON safely
# ======================================

def parse_grading(result):

    if "</think>" in result:
        result = result.split("</think>")[-1]

    start = result.find("{")
    end = result.rfind("}")

    if start == -1 or end == -1:

        return {
            "score": 0,
            "feedback": "Kein gültiges JSON vom Modell erhalten."
        }

    json_text = result[start:end + 1]

    try:
        return json.loads(json_text)

    except Exception:

        return {
            "score": 0,
            "feedback": "Ungültiges JSON vom Modell."
        }


# ======================================
# Grade complete exam
# ======================================

def grade_exam(reference_data, student_data, subject):

    results = []

    for ref_section, stu_section in zip(reference_data, student_data):

        section = {
            "number": ref_section["number"],
            "subquestions": []
        }

        for ref_sq, stu_sq in zip(
            ref_section["subquestions"],
            stu_section["subquestions"]
        ):

            print(
                f"Grading {ref_section['number']}{ref_sq['id']}..."
            )

            result = grade_answer(

                question=ref_sq["question"],

                reference_answer=ref_sq["reference_answer"],

                student_answer=stu_sq["answer"],

                subject=subject

            )

            grading = parse_grading(result)

            section["subquestions"].append({

                "id": ref_sq["id"],

                "question": ref_sq["question"],

                "reference_answer": ref_sq["reference_answer"],

                "student_answer": stu_sq["answer"],

                "grading": grading

            })

        results.append(section)

    return results


# ======================================
# Main
# ======================================

if __name__ == "__main__":

    subject = "chemistry"

    reference = load_json(
        "outputs/reference_answers.json"
    )

    student = load_json(
        "student_answers.json"
    )

    graded = grade_exam(
        reference,
        student,
        subject
    )

    with open(
        "grading_results.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            graded,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\nFinished grading.")