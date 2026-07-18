import os
import sys
os.environ['HF_HOME'] = 'D:\\hf_cache'
sys.path.insert(0, 'D:\\Python312\\Lib\\site-packages')
sys.path.insert(1, 'D:\\grading_project\\libs')

import streamlit as st
import ollama
import fitz
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch
import io
import time
import re
import base64

# ── Configuration ──────────────────────────────────────────────────────────────
MODEL_NAME = "qwen2.5:3b"

# ── Load TrOCR once at startup ─────────────────────────────────────────────────
@st.cache_resource
def load_trocr():
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-handwritten')
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-handwritten')
    return processor, model

# ── Translation ────────────────────────────────────────────────────────────────
def translate_to_english(text):
    if not text or len(text.strip()) < 3:
        return text
    prompt = f"""Translate the following text to English.
Keep all question numbers, answer options (A, B, C, D), and student answers exactly as they are.
Only translate the actual words — do not change structure or formatting.
Do not add any explanation, just output the translated text.

Text:
{text[:800]}"""
    response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content'].strip()

# ── Diagram Detection ──────────────────────────────────────────────────────────
def detect_diagram_regions(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    diagram_regions = []
    image_area = image.shape[0] * image.shape[1]
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = w / h if h > 0 else 0
        if (area > image_area * 0.05 and
                h > 100 and w > 100 and
                0.3 < aspect_ratio < 3.0):
            diagram_regions.append((x, y, w, h))
    return diagram_regions

# ── TrOCR Line Extraction ──────────────────────────────────────────────────────
def extract_lines_from_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 5))
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    lines = []
    prev_y = -1
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > 20 and w > 100:
            if abs(y - prev_y) < 30:
                continue
            prev_y = y
            pad = 15
            y1 = max(0, y - pad)
            y2 = min(img.shape[0], y + h + pad)
            lines.append(img[y1:y2, :])
    return lines

def read_line_trocr(line_img, processor, model):
    pil_img = Image.fromarray(cv2.cvtColor(line_img, cv2.COLOR_BGR2RGB))
    pixel_values = processor(images=pil_img, return_tensors='pt').pixel_values
    with torch.no_grad():
        generated_ids = model.generate(pixel_values, max_new_tokens=100)
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

# ── OCR / Text Extraction ──────────────────────────────────────────────────────
def extract_text(file_bytes, file_type):
    processor, trocr_model = load_trocr()
    text = ""

    if file_type == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()

        if len(text.strip()) < 50:
            st.info("Handwritten PDF detected — running TrOCR...")
            images = convert_from_bytes(file_bytes, dpi=300)
            for pil_img in images:
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                diagram_regions = detect_diagram_regions(img)
                if diagram_regions:
                    st.info(f"📊 Found {len(diagram_regions)} diagram region(s)")
                    if 'diagram_images' not in st.session_state:
                        st.session_state['diagram_images'] = []
                    for (x, y, w, h) in diagram_regions:
                        st.session_state['diagram_images'].append(img[y:y+h, x:x+w])
                lines = extract_lines_from_image(img)
                for line_img in lines:
                    text += read_line_trocr(line_img, processor, trocr_model) + "\n"
    else:
        img_pil = Image.open(io.BytesIO(file_bytes))
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        diagram_regions = detect_diagram_regions(img)
        if diagram_regions:
            st.info(f"📊 Found {len(diagram_regions)} diagram region(s)")
            if 'diagram_images' not in st.session_state:
                st.session_state['diagram_images'] = []
            for (x, y, w, h) in diagram_regions:
                st.session_state['diagram_images'].append(img[y:y+h, x:x+w])
        lines = extract_lines_from_image(img)
        st.info(f"Found {len(lines)} lines of handwriting...")
        for line_img in lines:
            text += read_line_trocr(line_img, processor, trocr_model) + "\n"

    return text.strip()

# ── Smart LLM Parser ───────────────────────────────────────────────────────────
def parse_questions(text, subject):
    st.info("🔍 Analysiere Prüfungsstruktur...")

    prompt = f"""You are analyzing a student {subject} exam paper.
Extract every single question and the student's answer.

For each question output EXACTLY this format on one line:
QUESTION|[number]|[type]|[question text]|[student answer]

Rules for type:
- 'mcq' = has options A) B) C) D) and student chose one letter
- 'essay' = asks for a long multi-paragraph response
- 'diagram' = asks to label, describe or interpret a diagram/graph/image
- 'short' = everything else

Rules for student answer:
- For mcq: just the single letter the student chose (A, B, C, or D)
- For short/essay/diagram: the full text the student wrote
- If no answer found: write "No answer provided"

Important:
- Extract ALL questions — do not skip any
- Include MCQ questions
- Do not add explanation — only QUESTION| lines
- Keep question text to first sentence if very long

Exam text:
{text}"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{'role': 'user', 'content': prompt}]
    )

    raw = response['message']['content']
    questions = []

    for line in raw.strip().split('\n'):
        line = line.strip()
        if line.startswith('QUESTION|'):
            parts = line.split('|')
            if len(parts) >= 5:
                try:
                    number = int(parts[1].strip()) if parts[1].strip().isdigit() else len(questions) + 1
                    q_type = parts[2].strip().lower()
                    if q_type not in ['mcq', 'short', 'essay', 'diagram']:
                        q_type = 'short'
                    questions.append({
                        "number": number,
                        "type": q_type,
                        "full_text": parts[3].strip(),
                        "student_answer": parts[4].strip(),
                        "diagram_image": None
                    })
                except Exception:
                    continue

    # Attach diagram images to diagram questions
    if 'diagram_images' in st.session_state and st.session_state['diagram_images']:
        diagram_qs = [q for q in questions if q['type'] == 'diagram']
        for i, q in enumerate(diagram_qs):
            if i < len(st.session_state['diagram_images']):
                q['diagram_image'] = st.session_state['diagram_images'][i]

    st.success(f"✅ {len(questions)} Fragen gefunden")
    return questions

# ── Grade Single MCQ ───────────────────────────────────────────────────────────
def grade_single_mcq(question, subject):
    english_text = translate_to_english(question['full_text'])
    prompt = f"""You are a {subject} teacher grading one multiple choice question.
This is a school-level exam for students aged 12-15.

{english_text}

Using your knowledge, determine the correct answer.
Check if the student's answer matches.

IMPORTANT:
- Be decisive — do not second guess yourself
- Score is 1 if student answer matches correct answer, 0 if not

Reply in EXACTLY this format:
Correct answer: [A or B or C or D]
Student answer: [A or B or C or D]
Score: [1 or 0]
Reason: [one sentence explaining the correct answer]"""

    response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
    return parse_mcq_result(response['message']['content'], question)

# ── Grade Single Short Answer ──────────────────────────────────────────────────
def grade_single_short(question, subject):
    english_question = translate_to_english(question['full_text'])
    english_answer = translate_to_english(question['student_answer'])

    prompt = f"""You are a {subject} teacher grading one short answer question.
This is a school-level exam for students aged 12-15.
Grade based on age-appropriate expectations only.

Question: {english_question}

Student answered: {english_answer}

Grade 0-3:
0 = completely wrong or blank
1 = one correct idea but missing key concepts
2 = mostly correct, one key concept missing
3 = complete and accurate for school level

RULES:
- Never penalize for missing university-level concepts
- Accept synonyms and related concepts
- Be generous — when in doubt give the higher grade
- Grade the scientific understanding, not spelling

Reply in EXACTLY this format:
Score: [0, 1, 2, or 3]/3
Thinking: [reasoning in English]
Feedback: [2 encouraging sentences in German directly to the student]"""

    response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

# ── Grade Single Essay ─────────────────────────────────────────────────────────
def grade_single_essay(question, subject):
    english_question = translate_to_english(question['full_text'])
    english_answer = translate_to_english(question['student_answer'])

    prompt = f"""You are a {subject} teacher grading an essay question.
This is a school-level exam for students aged 12-15.

Question: {english_question}

Student answered: {english_answer}

Grade 0-15:
13-15 = excellent, all parts addressed with clear reasoning
9-12  = good, most parts covered, minor gaps
5-8   = basic understanding, significant gaps
1-4   = very limited, mostly incorrect
0     = blank or completely off topic

Reply in EXACTLY this format:
Score: [0-15]/15
Thinking: [detailed reasoning in English]
Feedback: [3-4 encouraging sentences in German directly to the student]"""

    response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

# ── Grade Diagram Question ─────────────────────────────────────────────────────
def grade_diagram_question(question, subject):
    if question.get('diagram_image') is None:
        return grade_single_short(question, subject)

    pil_img = Image.fromarray(cv2.cvtColor(question['diagram_image'], cv2.COLOR_BGR2RGB))
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG')
    image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    english_answer = translate_to_english(question['student_answer']) if question['student_answer'] else "No answer provided"

    prompt = f"""You are an experienced {subject} teacher grading a student exam.
This is a school-level exam for students aged 12-15.

Look carefully at this diagram or graph.

The question asked: {question['full_text']}

The student answered: {english_answer}

Grade 0-3:
0 = completely wrong or blank
1 = partially correct, missing key observations
2 = mostly correct, minor gap
3 = fully correct and complete

Reply in EXACTLY this format:
Image shows: [brief description of the diagram]
Score: [0-3]/3
Thinking: [reasoning in English]
Feedback: [2 encouraging sentences in German directly to the student]"""

    response = ollama.chat(
        model='llava',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_b64]
        }]
    )
    return response['message']['content']

# ── Parse MCQ Result ───────────────────────────────────────────────────────────
def parse_mcq_result(raw_text, question):
    score = 0
    correct_answer = "?"
    reason = ""
    for line in raw_text.split('\n'):
        line_lower = line.lower().strip()
        if line_lower.startswith('score:'):
            score = 1 if '1' in line else 0
        if line_lower.startswith('correct answer:'):
            correct_answer = line.split(':')[-1].strip().upper()
        if line_lower.startswith('reason:'):
            reason = line.split(':', 1)[-1].strip()
    return {
        "number": question['number'],
        "student_answer": question.get('student_answer', '?'),
        "correct_answer": correct_answer,
        "score": score,
        "reason": reason
    }

# ── Grade All Questions ────────────────────────────────────────────────────────
def grade_all(questions, subject, result_container):
    total_score = 0
    total_possible = 0

    for q in questions:
        start = time.time()

        if q['type'] == 'mcq':
            result = grade_single_mcq(q, subject)
            elapsed = round(time.time() - start, 1)
            total_score += result['score']
            total_possible += 1
            icon = "✅" if result['score'] == 1 else "❌"
            result_container.markdown(
                f"**Q{result['number']}:** {icon} "
                f"Student: **{result['student_answer']}** | "
                f"Correct: **{result['correct_answer']}** | "
                f"Score: **{result['score']}/1** | "
                f"{result['reason']} *(⏱️ {elapsed}s)*"
            )

        elif q['type'] == 'short':
            result_text = grade_single_short(q, subject)
            elapsed = round(time.time() - start, 1)
            score = 0
            for line in result_text.split('\n'):
                if line.lower().startswith('score:'):
                    match = re.search(r'(\d+)', line)
                    if match:
                        score = min(int(match.group(1)), 3)
            total_score += score
            total_possible += 3
            result_container.markdown(f"**Q{q['number']}:** Score **{score}/3** *(⏱️ {elapsed}s)*")
            result_container.markdown(result_text)
            result_container.divider()

        elif q['type'] == 'essay':
            result_text = grade_single_essay(q, subject)
            elapsed = round(time.time() - start, 1)
            score = 0
            for line in result_text.split('\n'):
                if line.lower().startswith('score:'):
                    match = re.search(r'(\d+)', line)
                    if match:
                        score = min(int(match.group(1)), 15)
            total_score += score
            total_possible += 15
            result_container.markdown(f"**Q{q['number']} (Essay):** Score **{score}/15** *(⏱️ {elapsed}s)*")
            result_container.markdown(result_text)
            result_container.divider()

        elif q['type'] == 'diagram':
            result_text = grade_diagram_question(q, subject)
            elapsed = round(time.time() - start, 1)
            score = 0
            for line in result_text.split('\n'):
                if line.lower().startswith('score:'):
                    match = re.search(r'(\d+)', line)
                    if match:
                        score = min(int(match.group(1)), 3)
            total_score += score
            total_possible += 3
            label = "Diagram" if q.get('diagram_image') is not None else "Diagram (text only)"
            result_container.markdown(f"**Q{q['number']} ({label}):** Score **{score}/3** *(⏱️ {elapsed}s)*")
            result_container.markdown(result_text)
            result_container.divider()

    result_container.divider()
    result_container.markdown(f"## 🎯 Final Score: **{total_score}/{total_possible}**")
    return total_score, total_possible

# ── Streamlit UI ───────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Automatische Bewertung",
        page_icon="📝",
        layout="wide"
    )

    st.title("📝 Automatisches Bewertungssystem")
    st.subheader("Naturwissenschaften — Schulbewertung")
    st.divider()

    subject = st.selectbox(
        "Fach auswählen",
        ["Biology", "Chemistry", "Physics", "Science"]
    )

    uploaded_file = st.file_uploader(
        "Prüfung hochladen (PDF oder Bild)",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_type = "pdf" if uploaded_file.name.endswith(".pdf") else "image"

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Extrahierter Text")
            with st.spinner("Text wird extrahiert..."):
                extracted_text = extract_text(file_bytes, file_type)

            if not extracted_text:
                st.error("Kein Text gefunden.")
                return

            edited_text = st.text_area(
                "Text überprüfen und korrigieren:",
                value=extracted_text,
                height=400
            )

        with col2:
            st.subheader("🎯 Bewertung & Feedback")

            if st.button("📊 Jetzt bewerten", type="primary", use_container_width=True):

                with st.spinner("🔍 Analysiere Prüfungsstruktur..."):
                    questions = parse_questions(edited_text, subject)

                if not questions:
                    st.error("Keine Fragen gefunden. Bitte Text überprüfen.")
                    return

                st.info(f"📋 {len(questions)} Fragen gefunden — Bewertung startet...")
                result_container = st.container()
                total_start = time.time()
                total_score, total_possible = grade_all(questions, subject, result_container)
                total_elapsed = round(time.time() - total_start, 1)
                st.success(f"⏱️ Gesamtzeit: {total_elapsed} Sekunden")


if __name__ == "__main__":
    main()