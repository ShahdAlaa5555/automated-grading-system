# Automated Grading System
GUC Summer Internship 2026

## Project Structure
- modules/ — AI grading modules per subject
- shared/ — shared utilities
- web/ — Flask web application
- data/ — sample exams for testing
- tests/ — test scripts

## Modules
- biology/ — Shahd Alaa Ahmed (58-22017)
- chemistry/ — [colleague]
- math/ — Mennatullah Shaaban Amer (58-23237)
- german/ — [colleague]

## Tech Stack
- OCR: TrOCR + OpenCV
- LLM: Qwen2.5:3b + LLaVA (Ollama, fully local)
- Web: Flask + SQLite
- Language: Python 3.12

## Setup
1. Install Ollama
2. ollama pull qwen2.5:3b
3. ollama pull llava
4. pip install -r requirements.txt
5. cd web/backend && python app.py

## Supervisor
Dr. Aya Salama — GUC
