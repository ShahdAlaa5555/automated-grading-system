from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class OCRLine(BaseModel):
    line_number: int
    text: str
    box: list[int] = Field(description="[x1, y1, x2, y2]")


class OCRPage(BaseModel):
    page_number: int
    printed_text: str = ""
    text: str
    lines: list[OCRLine]
    warning: str | None = None


class CorrectionItem(BaseModel):
    number: str = ""
    question_or_context: str = ""
    answer_type: Literal["multiple_choice", "written", "unknown"] = "unknown"
    student_answer: str = ""
    language_feedback: str = ""
    content_feedback: str = ""
    assessment: Literal[
        "likely_correct", "likely_incorrect", "unclear", "cannot_verify"
    ] = "cannot_verify"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class PageCorrection(BaseModel):
    page_number: int
    corrected_transcription: str = ""
    items: list[CorrectionItem] = Field(default_factory=list)
    page_feedback: str = ""
    warnings: list[str] = Field(default_factory=list)
    raw_model_response: str | None = None


class AnalyzeResult(BaseModel):
    filename: str
    page_count: int
    models: dict[str, str]
    processing_seconds: float
    note: str
    ocr_pages: list[OCRPage]
    corrections: list[PageCorrection]
    overall_feedback: str
    warnings: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
