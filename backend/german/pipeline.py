from __future__ import annotations

import time
from collections import Counter

from .config import Settings
from .schemas import AnalyzeResult
from .document_loader import load_document_pages
from .llm_service import LLMService
from .ocr_service import OCRService


class ExamPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ocr = OCRService(settings)
        self.llm = LLMService(settings)

    def analyze(self, data: bytes, filename: str, exam_context: str = "") -> AnalyzeResult:
        started = time.perf_counter()
        pages = load_document_pages(data, filename, self.settings)
        ocr_pages = self.ocr.recognize_pages(pages)
        corrections = self.llm.correct_pages(ocr_pages, exam_context=exam_context)

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


def _build_overall_feedback(corrections, assessments: Counter[str]) -> str:
    counts = ", ".join(
        f"{key}: {value}"
        for key, value in sorted(assessments.items())
    )

    if counts:
        return f"Overall assessment summary: {counts}."

    return "No reliably separated answer items were detected."
