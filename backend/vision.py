from ollama import chat
import json


def analyze_exam(image_path):

    prompt = """
You are analyzing a German chemistry exam page.

Your task is NOT to transcribe the page.

Instead, analyze the visual structure.

Return ONLY valid JSON in this format:

{
    "contains_table": true,
    "contains_diagram": false,
    "contains_graph": false,
    "contains_molecule": false,
    "contains_handwriting": true,
    "layout": {
        "multiple_columns": true,
        "printed_and_handwritten_mixed": true
    },
    "visual_elements": [
        {
            "type": "table",
            "description": ""
        },
        {
            "type": "diagram",
            "description": ""
        }
    ]
}

Rules:

- Do NOT transcribe the exam.
- Do NOT answer chemistry questions.
- Do NOT invent objects.
- Describe only visible visual elements.
- Return JSON only.
"""

    response = chat(
        model="llava",
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }
        ]
    )

    text = response["message"]["content"]

    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)