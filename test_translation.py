import sys
sys.path.insert(0, 'D:\\grading_project\\libs')
import ollama

MODEL_NAME = "qwen2.5:3b"

def translate_to_english(text):
    prompt = f"""Translate the following German text to English.
Keep all question numbers, answer options (A, B, C, D), and student answers exactly as they are.
Only translate the actual words — do not change structure or formatting.
Do not add any explanation, just output the translated text.

German text:
{text}"""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content'].strip()

def translate_feedback_to_german(text):
    prompt = f"""Translate the following English feedback to German.
The feedback is for a school student aged 12-15.
Use friendly, encouraging, and simple language a young student would understand.
Do not add any explanation, just output the German translation.

English feedback:
{text}"""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content'].strip()

# Test 1 — translate German question to English
german_text = """Was benötigen Pflanzen, um Photosynthese durchzuführen?
A) Dunkelheit, Wasser und Sauerstoff
B) Sonnenlicht, Wasser und Kohlendioxid
C) Boden, Stickstoff und Wärme
D) Sonnenlicht, Salz und Wasserstoff
Antwort des Schülers: A"""

print("=== TEST 1: German → English ===")
english = translate_to_english(german_text)
print(english)
print()

# Test 2 — translate English feedback to German
english_feedback = """Good attempt! You identified that plants need sunlight, 
but you missed that they also need water and carbon dioxide. 
Try to remember all three ingredients next time!"""

print("=== TEST 2: English feedback → German ===")
german = translate_feedback_to_german(english_feedback)
print(german)