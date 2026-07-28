import json
import re
import ollama

SYSTEM_PROMPT = """
You are an experienced mathematics teacher.

The OCR text below contains BOTH:

- the printed exam question, where the question title looks like this: "Question [question_number]: [topic] ([maximum_grades_awarded])"
- the student's handwritten answer

Your job is to:

1. Understand the exam question.
2. Understand the student's answer.
3. Grade it fairly.
4. Return ONLY valid JSON.

Return exactly:

{
    "mark": 0,
    "feedback": "...",
    "reasoning": "..."
}

Rules:

- Return ONLY JSON.
- Do not use Markdown.
- Do not use ``` blocks.
- Do not use LaTeX.
Award marks proportionally to the quality of the student's answer.

If the answer is completely correct, award full marks.

If the answer is partially correct, award an appropriate partial mark.

Base your decision on:
- mathematical correctness,
- completeness,
- logical reasoning,
- explanation.

Explain why you deducted marks.
"""


def parse_qwen_json(answer):

    answer = re.sub(r"```json|```", "", answer).strip()

    answer = answer.replace(r"\(", "")
    answer = answer.replace(r"\)", "")

    answer = answer.replace("\\", "\\\\")

    return json.loads(answer)


def grade_answer(ir):

    prompt = f"""
OCR OUTPUT

{ir["student_text"]}

Diagram Information

{json.dumps(ir["diagram"], indent=2)}
"""

    response = ollama.chat(

        model="qwen2.5:3b",

        messages=[

            {

                "role": "system",

                "content": SYSTEM_PROMPT

            },

            {

                "role": "user",

                "content": prompt

            }

        ]

    )

    answer = response["message"]["content"]

    print("\n================ RAW QWEN RESPONSE ================\n")
    print(answer)
    print("\n===================================================\n")

    return parse_qwen_json(answer)