from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable
from typing import Any

from .config import Settings
from .schemas import AnalyzeResult, CorrectionItem, PageCorrection
from .document_loader import load_document_pages
from .llm_service import LLMService
from .ocr_service import OCRService


ProgressCallback = Callable[[str, int], None]


class ExamPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ocr = OCRService(settings)
        self.llm = LLMService(settings)

    def analyze(
        self,
        data: bytes,
        filename: str,
        exam_context: str = "",
        progress_callback: ProgressCallback | None = None,
    ) -> AnalyzeResult:
        """
        Run the original German analysis pipeline.

        The return type remains AnalyzeResult so existing German-module code
        that uses this method directly is not broken.
        """

        started = time.perf_counter()

        def report(status: str, progress: int) -> None:
            if progress_callback is not None:
                progress_callback(status, progress)

        report("Processing", 20)

        pages = load_document_pages(data, filename, self.settings)
        ocr_pages = self.ocr.recognize_pages(pages)

        report("OCR Complete", 60)
        report("Grading", 80)

        corrections = self.llm.correct_pages(
            ocr_pages,
            exam_context=exam_context,
        )

        warnings: list[str] = []
        for page in ocr_pages:
            if page.warning:
                warnings.append(f"Page {page.page_number}: {page.warning}")
        for correction in corrections:
            warnings.extend(
                f"Page {correction.page_number}: {warning}"
                for warning in correction.warnings
            )
        assessments = Counter(
            item.assessment
            for correction in corrections
            for item in correction.items
        )
        overall = _build_overall_feedback(corrections, assessments)
        elapsed = time.perf_counter() - started
        return AnalyzeResult(
            filename=filename,
            page_count=len(pages),
            models={
                "ocr": (
                    f"question={self.settings.printed_trocr_model_id}; "
                    f"answer={self.settings.trocr_model_id}"
                ),
                "llm": self.settings.ollama_model,
            },
            processing_seconds=round(elapsed, 2),
            note=(
                "Output should be reviewed by a teacher."
            ),
            ocr_pages=ocr_pages,
            corrections=corrections,
            overall_feedback=overall,
            warnings=warnings,
            metadata={
                "ocr_device": self.ocr.device_name,
                "database_used": False,
                "temporary_files_written": False,
                "exam_context_supplied": bool(exam_context.strip()),
            },
        )

    def analyze_for_grading_system(
        self,
        data: bytes,
        filename: str,
        exam_context: str = "",
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """
        Run the German pipeline and add the common ``questions`` structure
        used by server.py, save_results(), and the React ResultsPage.

        All original German output fields are kept in the returned dictionary.
        """

        result = self.analyze(
            data=data,
            filename=filename,
            exam_context=exam_context,
            progress_callback=progress_callback,
        )

        payload = result.model_dump(mode="json")
        payload["questions"] = _build_questions_for_results_page(result)
        return payload


def _build_questions_for_results_page(
    result: AnalyzeResult,
) -> list[dict[str, Any]]:
    """
    Build the common question format expected by save_results():

    number, question, student_answer, is_correct, and feedback.
    """

    questions: list[dict[str, Any]] = []
    ocr_pages_by_number = {
        page.page_number: page
        for page in result.ocr_pages
    }

    for correction in result.corrections:
        ocr_page = ocr_pages_by_number.get(correction.page_number)

        if not correction.items:
            question_text = (
                ocr_page.printed_text.strip()
                if ocr_page and ocr_page.printed_text.strip()
                else f"German exam page {correction.page_number}"
            )

            student_answer = (
                ocr_page.text.strip()
                if ocr_page and ocr_page.text.strip()
                else correction.corrected_transcription.strip()
            )

            feedback = (
                correction.page_feedback.strip()
                or result.overall_feedback.strip()
                or "The answer could not be verified automatically. Teacher review is required."
            )

            questions.append(
                {
                    "number": len(questions) + 1,
                    "question": question_text,
                    "student_answer": student_answer,
                    "is_correct": _infer_correctness_from_feedback(feedback),
                    "feedback": feedback,
                }
            )
            continue

        for item in correction.items:
            question_text = _get_question_text(
                item=item,
                correction=correction,
                ocr_page=ocr_page,
            )

            student_answer = (
                ocr_page.text.strip()
                if ocr_page and ocr_page.text.strip()
                else item.student_answer.strip()
                or correction.corrected_transcription.strip()
            )

            questions.append(
                {
                    "number": len(questions) + 1,
                    "question": question_text,
                    "student_answer": student_answer,
                    "is_correct": item.assessment == "likely_correct",
                    "feedback": _build_item_feedback(item, correction),
                }
            )

    if not questions:
        questions.append(
            {
                "number": 1,
                "question": "German exam review",
                "student_answer": "",
                "is_correct": False,
                "feedback": (
                    result.overall_feedback.strip()
                    or "No reliably separated answers were detected. Teacher review is required."
                ),
            }
        )

    return questions


def _get_question_text(item, correction, ocr_page) -> str:
    question_text = item.question_or_context.strip()

    if not question_text and ocr_page is not None:
        question_text = ocr_page.printed_text.strip()

    if not question_text:
        question_text = f"German exam page {correction.page_number}"

    original_number = item.number.strip()
    if original_number:
        question_text = f"{original_number}. {question_text}"

    return question_text


def _build_item_feedback(
    item: CorrectionItem,
    correction: PageCorrection,
) -> str:
    feedback_parts: list[str] = []

    if item.language_feedback.strip():
        feedback_parts.append(
            f"Language feedback: {item.language_feedback.strip()}"
        )

    if item.content_feedback.strip():
        feedback_parts.append(
            f"Content feedback: {item.content_feedback.strip()}"
        )

    if not feedback_parts and correction.page_feedback.strip():
        feedback_parts.append(correction.page_feedback.strip())

    assessment_label = item.assessment.replace("_", " ").title()
    confidence_percent = round(item.confidence * 100)
    feedback_parts.append(
        f"Assessment: {assessment_label} ({confidence_percent}% confidence)."
    )

    return "\n\n".join(feedback_parts)


def _build_overall_feedback(corrections, assessments: Counter[str]) -> str:
    counts = ", ".join(
        f"{key}: {value}"
        for key, value in sorted(assessments.items())
    )

    if counts:
        return f"Overall assessment summary: {counts}."

    return "No reliably separated answer items were detected."

def _infer_correctness_from_feedback(feedback: str) -> bool:
    """
    Used only when the LLM failed to return a valid CorrectionItem,
    but returned understandable page-level feedback.
    """

    normalized = feedback.strip().lower()

    positive_phrases = (
        "answer is correct",
        "response is correct",
        "correct and well-written",
        "accurate and appropriate",
        "covers all required points",
        "includes all the required points",
        "fulfills the task",
        "fulfils the task",
        "meets the task requirements",
        "fully addresses the task",
    )

    negative_phrases = (
        "answer is incorrect",
        "response is incorrect",
        "does not answer",
        "does not address",
        "important points are missing",
        "required points are missing",
        "fails to include",
        "cannot be verified",
        "could not be verified",
        "not enough information",
        "insufficient information",
        "unreadable",
    )

    says_positive = any(
        phrase in normalized
        for phrase in positive_phrases
    )

    says_negative = any(
        phrase in normalized
        for phrase in negative_phrases
    )

    return says_positive and not says_negative