from __future__ import annotations

import json
import logging
import re
from typing import Any

import requests

from .config import Settings
from .schemas import CorrectionItem, OCRPage, PageCorrection

LOGGER = logging.getLogger(__name__)


OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "page_number": {"type": "integer"},
        "corrected_transcription": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "string"},
                    "question_or_context": {"type": "string"},
                    "answer_type": {
                        "type": "string",
                        "enum": ["multiple_choice", "written", "unknown"],
                    },
                    "student_answer": {"type": "string"},
                    "language_feedback": {"type": "string"},
                    "content_feedback": {"type": "string"},
                    "assessment": {
                        "type": "string",
                        "enum": [
                            "likely_correct",
                            "likely_incorrect",
                            "unclear",
                            "cannot_verify",
                        ],
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "number",
                    "question_or_context",
                    "answer_type",
                    "student_answer",
                    "language_feedback",
                    "content_feedback",
                    "assessment",
                    "confidence",
                ],
            },
        },
        "page_feedback": {"type": "string"},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "page_number",
        "corrected_transcription",
        "items",
        "page_feedback",
        "warnings",
    ],
}


SYSTEM_PROMPT = """Du bist ein vorsichtiger Assistent zur Überprüfung handschriftlicher deutscher Prüfungen.
Der Eingabetext stammt aus OCR und kann falsch, unvollständig oder falsch segmentiert sein.

Regeln:
1. Erfinde niemals fehlende Fragen, Antworten, Markierungen oder Fakten.
2. Bewahre die Bedeutung und den Wortlaut der studentischen Antwort. Korrigiere in der Transkription nur sehr wahrscheinliche OCR-Fehler.
3. Markiere Unsicherheit in der korrigierten Transkription mit [unklar].
4. Ohne Lösungsschlüssel darfst du keine objektive Note und keine definitive Gesamtpunktzahl vergeben.
5. Bei Multiple-Choice-Aufgaben darfst du nur eine Auswahl nennen, wenn sie im OCR-Text wirklich sichtbar ist.
6. Trenne Sprachfeedback von inhaltlichem Feedback.
7. Der Abschnitt AUFGABENTEXT ist ausschließlich Frage, Aufgabenstellung oder Kontext. Behandle ihn niemals als studentische Antwort.
8. Der Abschnitt STUDENTENANTWORT enthält ausschließlich den von TrOCR gelesenen Antwortversuch. Nur dieser Abschnitt darf in student_answer und corrected_transcription erscheinen.
9. Kopiere keine Abschnittsüberschriften wie AUFGABENTEXT oder STUDENTENANTWORT in die Ergebnisfelder.
10. Schreibe student_answer und corrected_transcription auf Deutsch.
11. Schreibe language_feedback, content_feedback und page_feedback auf Englisch.
12. Antworte ausschließlich entsprechend dem vorgegebenen JSON-Schema.
13. assessment, language_feedback und content_feedback müssen einander entsprechen.
14. Verwende assessment="likely_correct", wenn die Antwort die Aufgabenstellung erfüllt und verständlich ist. Kleine Grammatik- oder Rechtschreibfehler machen die gesamte Antwort nicht automatisch falsch.
15. Verwende assessment="likely_incorrect", wenn wichtige geforderte Punkte fehlen, die Antwort nicht zur Aufgabe passt oder die Bedeutung deutlich falsch ist.
16. Verwende assessment="unclear" oder assessment="cannot_verify" nur, wenn der OCR-Text unleserlich, unvollständig oder nicht ausreichend zur Bewertung ist.
17. Wenn du in feedback schreibst, dass die Antwort correct, accurate, appropriate, well-written oder vollständig ist, muss assessment="likely_correct" sein.
18. Wenn assessment nicht "likely_correct" ist, darf das Feedback die Antwort nicht als correct bezeichnen.
"""


class OllamaError(RuntimeError):
    pass


class LLMService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()

    def is_available(self) -> tuple[bool, str]:
        try:
            response = self.session.get(
                f"{self.settings.ollama_base_url.rstrip('/')}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            return False, f"Ollama is not reachable: {exc}"

        names = {
            item.get("name", "")
            for item in payload.get("models", [])
            if isinstance(item, dict)
        }
        model = self.settings.ollama_model
        exact_or_latest = model in names or f"{model}:latest" in names
        if not exact_or_latest:
            return False, f"Ollama is running, but model '{model}' is not installed."
        return True, "ready"

    def correct_pages(self, pages: list[OCRPage], exam_context: str = "") -> list[PageCorrection]:
        available, message = self.is_available()
        if not available:
            raise OllamaError(
                f"{message} Run: ollama pull {self.settings.ollama_model}"
            )

        corrections: list[PageCorrection] = []
        for page in pages:
            if not page.text.strip() and not page.printed_text.strip():
                corrections.append(
                    PageCorrection(
                        page_number=page.page_number,
                        warnings=["Kein gedruckter oder handschriftlicher Text verfügbar."],
                    )
                )
                continue
            corrections.append(self._correct_page(page, exam_context))
        return corrections

    def _correct_page(self, page: OCRPage, exam_context: str) -> PageCorrection:
        context = exam_context.strip() or "Kein zusätzlicher Prüfungskontext angegeben."
        printed_text = page.printed_text.strip() or "[Kein auswählbarer gedruckter PDF-Text gefunden.]"
        handwritten_text = page.text.strip() or "[Keine handschriftliche Antwort erkannt.]"

        prompt = f"""Prüfungskontext:
{context}

Page: {page.page_number}

AUFGABENTEXT (separat erkannter Frage-/Kontextbereich):
---
{printed_text}
---

STUDENTENANTWORT (separat erkannter handschriftlicher Antwortbereich):
---
{handwritten_text}
---

Wichtig:
- Verwende AUFGABENTEXT für question_or_context.
- Verwende ausschließlich STUDENTENANTWORT für student_answer.
- corrected_transcription darf nur die handschriftliche Antwort enthalten.
- Falls keine handschriftliche Antwort erkennbar ist, erfinde keine Antwort und verwende assessment='cannot_verify'.
"""

        payload = {
            "model": self.settings.ollama_model,
            "system": SYSTEM_PROMPT,
            "prompt": prompt,
            "format": OUTPUT_SCHEMA,
            "stream": False,
            "keep_alive": self.settings.ollama_keep_alive,
            "options": {
                "temperature": self.settings.llm_temperature,
                "num_ctx": self.settings.llm_num_ctx,
                "num_predict": self.settings.llm_num_predict,
                "seed": 42,
                "repeat_penalty": 1.05,
            },
        }

        try:
            response = self.session.post(
                f"{self.settings.ollama_base_url.rstrip('/')}/api/generate",
                json=payload,
                timeout=self.settings.ollama_timeout_seconds,
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
        except requests.RequestException as exc:
            raise OllamaError(f"Ollama generation failed: {exc}") from exc
        except ValueError as exc:
            raise OllamaError("Ollama returned an invalid HTTP JSON response.") from exc

        parsed = self._parse_json(raw)
        if parsed is None:
            return PageCorrection(
                page_number=page.page_number,
                corrected_transcription=page.text,
                page_feedback="The model did not return a valid structured result.",
                warnings=["The LLM returned invalid JSON; its raw response was saved."],
                raw_model_response=raw,
            )

        parsed = self._normalize_output(parsed, page)

        try:
            parsed["page_number"] = page.page_number
            return PageCorrection.model_validate(parsed)
        except Exception as exc:
            LOGGER.warning("Could not validate LLM JSON: %s", exc)
            items: list[CorrectionItem] = []
            for item in parsed.get("items", []) if isinstance(parsed, dict) else []:
                try:
                    items.append(CorrectionItem.model_validate(item))
                except Exception:
                    continue
            return PageCorrection(
                page_number=page.page_number,
                corrected_transcription=str(parsed.get("corrected_transcription", page.text)),
                items=items,
                page_feedback=str(parsed.get("page_feedback", "")),
                warnings=["The LLM output only partially matched the required schema; valid fields were retained."],
                raw_model_response=raw,
            )

    @staticmethod
    def _normalize_output(
        parsed: dict[str, Any],
        page: OCRPage,
    ) -> dict[str, Any]:
        """Repair predictable mistakes from the small local LLM.

        OCR already separated the question and answer, so for a single detected
        item the question field should be the separately recognized question text.
        A writing instruction must not be mislabeled as multiple choice.
        """

        question = page.printed_text.strip()
        items = parsed.get("items")

        if not question or not isinstance(items, list):
            return parsed

        valid_items = [
            item
            for item in items
            if isinstance(item, dict)
        ]

        # One OCR input now represents exactly one question-answer block.
        # If the small LLM incorrectly creates several items from bullet points,
        # retain the item containing the most substantial student answer.
        if len(valid_items) > 1:
            valid_items.sort(
                key=lambda item: len(
                    str(
                        item.get(
                            "student_answer",
                            "",
                        )
                    ).strip()
                ),
                reverse=True,
            )

            valid_items = valid_items[:1]
            parsed["items"] = valid_items

        if len(valid_items) == 1:
            valid_items[0]["question_or_context"] = question

        question_lower = question.lower()

        looks_written = any(
            marker in question_lower
            for marker in (
                "write ",
                "write your answer",
                "words",
                "schreib",
                "verfasse",
                "text schreiben",
            )
        )

        if looks_written:
            for item in valid_items:
                item["answer_type"] = "written"

        for item in valid_items:
            LLMService._repair_assessment_consistency(item)

        parsed["items"] = valid_items

        return parsed

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any] | None:
        text = text.strip()
        if not text:
            return None
        try:
            value = json.loads(text)
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            value = json.loads(match.group(0))
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _repair_assessment_consistency(
        item: dict[str, Any],
    ) -> None:
        """
        Repair obvious contradictions between the generated assessment
        and the generated feedback.

        This is a safety net for small local models.
        """

        valid_assessments = {
            "likely_correct",
            "likely_incorrect",
            "unclear",
            "cannot_verify",
        }

        assessment = str(
            item.get("assessment", "")
        ).strip()

        if assessment not in valid_assessments:
            assessment = "unclear"

        language_feedback = str(
            item.get("language_feedback", "")
        ).strip()

        content_feedback = str(
            item.get("content_feedback", "")
        ).strip()

        combined_feedback = (
            f"{language_feedback} {content_feedback}"
        ).lower()

        positive_phrases = (
            "answer is correct",
            "response is correct",
            "correct and well-written",
            "all the required points",
            "covers all required points",
            "fulfills the task",
            "meets the task requirements",
            "accurate and appropriate",
            "fully addresses the task",
        )

        incorrect_phrases = (
            "answer is incorrect",
            "response is incorrect",
            "does not address the task",
            "does not answer the question",
            "important required points are missing",
            "fails to include",
            "meaning is incorrect",
        )

        unverifiable_phrases = (
            "cannot be verified",
            "not enough information",
            "insufficient information",
            "ocr is unreadable",
            "answer is unreadable",
            "no answer was detected",
        )

        says_positive = any(
            phrase in combined_feedback
            for phrase in positive_phrases
        )

        says_incorrect = any(
            phrase in combined_feedback
            for phrase in incorrect_phrases
        )

        says_unverifiable = any(
            phrase in combined_feedback
            for phrase in unverifiable_phrases
        )

        if says_unverifiable:
            assessment = "cannot_verify"

        elif says_positive and not says_incorrect:
            assessment = "likely_correct"

        elif says_incorrect and not says_positive:
            assessment = "likely_incorrect"

        item["assessment"] = assessment
