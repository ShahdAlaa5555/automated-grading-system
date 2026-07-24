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

def grade_answer(question, reference_answer, student_answer):

    prompt = f"""
Du bist ein erfahrener deutscher Chemielehrer.

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
Keine <think> Tags.


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

    # Remove Qwen thinking section

    if "</think>" in result:
        result = result.split("</think>")[-1]


    # Find JSON object

    start = result.find("{")
    end = result.rfind("}")


    if start == -1 or end == -1:

        return {
            "score": 0,
            "feedback": "Kein gültiges JSON vom Modell erhalten."
        }


    json_text = result[start:end+1]


    try:

        return json.loads(json_text)


    except Exception as e:

        print("\nFAILED TO PARSE JSON")
        print(json_text)
        print(e)


        return {
            "score": 0,
            "feedback": "Ungültiges JSON vom Modell."
        }



# ======================================
# Grade complete exam
# ======================================

def grade_exam(reference_data, student_data):

    results = []


    for ref_section, stu_section in zip(
        reference_data,
        student_data
    ):


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

                student_answer=stu_sq["answer"]

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


    reference = load_json(
        "outputs/reference_answers.json"
    )


    student = load_json(
        "student_answers.json"
    )


    graded = grade_exam(
        reference,
        student
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