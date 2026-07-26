from ollama import chat
from config import MODEL


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

        for subquestion in section["subquestions"]:

            print(
                f"Generating answer for "
                f"{section['number']}{subquestion['id']}..."
            )

            answer = generate_reference_answer(
                subquestion["question"],
                subject
            )

            subquestion["reference_answer"] = answer

            print("Done!")

    return questions