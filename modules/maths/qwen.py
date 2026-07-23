import ollama

SYSTEM_PROMPT = """
You are an OCR verification assistant.

You are given:

1. The original image.
2. The OCR transcription.

The OCR may:
- miss lines
- merge lines
- skip calculations
- confuse symbols

Your task is to compare BOTH the image and the OCR.

Rules:

- Make the MINIMUM edits necessary.
- Preserve every calculation.
- Preserve every intermediate step.
- Preserve spelling mistakes made by the student.
- Preserve grammar mistakes.
- Preserve line order.
- Preserve repeated words.
- Never solve the problem.
- Never finish incomplete calculations.
- Never rewrite the student's wording.
- Never summarize.

If OCR omitted a visible line, restore it.

If OCR inserted text not visible in the image, remove it.

If something cannot be read from the image, write [unclear].

If a diagram exists but cannot be represented, write [diagram present].

Return ONLY the transcription.
"""


def repair(image_path, raw_ocr):

    response = ollama.chat(

        model="qwen2.5vl:3b",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content":
                    f"""
OCR TRANSCRIPTION

{raw_ocr}

Compare this OCR against the attached image.
Return the most faithful transcription.
""",
                "images": [image_path]
            }
        ]

    )

    return response["message"]["content"]