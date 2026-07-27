import json
from ollama import chat

from config import MODEL


# =====================================================
# LOAD JSON
# =====================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



# =====================================================
# GRADE ONE QUESTION
# =====================================================

def grade_answer(
        question,
        student_answer,
        max_points,
        subject
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
- Nicht jede kleine Ungenauigkeit führt zu Punktabzug.
- Wenn der Schüler die meisten geforderten Inhalte nennt,
  soll die Punktzahl entsprechend hoch sein.
- Bei Rechnungen:
  - richtige Formel zählt
  - richtiger Ansatz zählt
  - Rechenfehler nur teilweise abziehen.
- Bei Chemie:
  - falsche Indizes durch OCR (z.B. H2 wird Hz)
    nicht hart bestrafen.


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
# EXTRACT JSON FROM QWEN
# =====================================================

def extract_json(text):

    start = text.find("{")
    end = text.rfind("}")


    if start == -1 or end == -1:

        return {
            "score": 0,
            "feedback": "Ungültige Modellantwort"
        }


    json_text = text[start:end+1]


    try:

        return json.loads(json_text)


    except:

        return {
            "score": 0,
            "feedback": "JSON konnte nicht gelesen werden"
        }



# =====================================================
# GRADE COMPLETE EXAM
# =====================================================

def grade_exam(exam, subject):

    results = []


    total_score = 0

    total_points = 0



    for section in exam["sections"]:


        section_points = int(
            section["points"]
        )


        section_result = {

            "number": section["number"],

            "title": section["title"],

            "subquestions": []

        }



        for question in section["subquestions"]:


            print(
                f"Grading {section['number']}{question['id']}..."
            )


            grading = grade_answer(

                question["question"],

                question["student_answer"],

                section_points,

                subject

            )


            score = grading.get(
                "score",
                0
            )


            # safety limit

            if score > section_points:

                score = section_points


            if score < 0:

                score = 0



            total_score += score

            total_points += section_points



            section_result["subquestions"].append({

                "id": question["id"],

                "question": question["question"],

                "student_answer":
                    question["student_answer"],

                "score":
                    score,

                "max_points":
                    section_points,

                "feedback":
                    grading.get(
                        "feedback",
                        ""
                    )

            })


        results.append(section_result)



    percentage = 0


    if total_points > 0:

        percentage = round(

            (total_score / total_points) * 100,

            2

        )



    return {


        "total_score":
            total_score,


        "total_points":
            total_points,


        "percentage":
            percentage,


        "questions":
            results

    }



# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":


    subject = "chemistry"


    exam = load_json(

        "outputs/questions.json"

    )



    result = grade_exam(

        exam,

        subject

    )



    with open(

        "grading_results.json",

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            result,

            f,

            indent=4,

            ensure_ascii=False

        )



    print("\n====================")
    print("FINAL RESULT")
    print("====================")


    print(
        "Score:",
        result["total_score"],
        "/",
        result["total_points"]
    )


    print(
        "Percentage:",
        result["percentage"],
        "%"
    )


    print("\nFinished grading!")