from ollama import chat
from config import MODEL
from grader2 import grade_answer


# ==========================================================
# GENERATE ONE REFERENCE ANSWER
# ==========================================================

def generate_reference_answer(question, subject):

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

Erstelle die ideale Musterlösung für folgende Prüfungsfrage:

Frage:
{question}

Anforderungen:

- Schreibe auf Deutsch.
- Gib eine fachlich korrekte Musterlösung.
- Halte die Antwort kurz und präzise.
- Verwende Stichpunkte wenn sinnvoll.
- Falls nötig, benutze Formeln oder Gleichungen.
- Keine Erklärung deines Denkprozesses.
- Gib nur die Musterlösung zurück.
"""


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


    return response["message"]["content"].strip()


# ==========================================================
# GENERATE ALL REFERENCE ANSWERS
# ==========================================================

def generate_answers(questions, subject):

    for section in questions:

       points = section.get("points")
       print("POINTS =", repr(points))
       max_points = 1

       for subquestion in section["subquestions"]:

            print(
                f"Generating answer for "
                f"{section['number']}{subquestion['id']}..."
            )

            # Generate reference answer
            reference = generate_reference_answer(
                subquestion["question"],
                subject
            )

            subquestion["reference_answer"] = reference

            # Grade the student's answer
            grading = grade_answer(
                question=subquestion["question"],
                student_answer=subquestion.get("student_answer", ""),
                reference_answer=reference,
                max_points=max_points,
                subject=subject
            )

            score = grading.get("score", 0)

            subquestion["score"] = score
            subquestion["feedback"] = grading.get("feedback", "")
            subquestion["is_correct"] = score > 0

            print(
                f"Done! Score: {score}/{max_points}"
            )

    return questions