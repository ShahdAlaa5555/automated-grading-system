from ollama import chat
from config import MODEL



def generate_reference_answer(question):


    prompt = f"""
Du bist ein erfahrener deutscher Chemielehrer.

Erstelle die ideale Musterlösung für folgende Prüfungsfrage:

Frage:
{question}


Anforderungen:

- Schreibe auf Deutsch.
- Verwende fachlich korrekte Chemiebegriffe.
- Halte die Antwort kurz und präzise.
- Verwende Stichpunkte wenn sinnvoll.
- Füge chemische Gleichungen hinzu, wenn notwendig.
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


    answer = response["message"]["content"]


    return answer.strip()




def generate_answers(questions):


    for section in questions:


        for subquestion in section["subquestions"]:


            print(
                f"Generating answer for "
                f"{section['number']}{subquestion['id']}..."
            )


            answer = generate_reference_answer(
                subquestion["question"]
            )


            subquestion["reference_answer"] = answer


            print("Done!")


    return questions