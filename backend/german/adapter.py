from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import get_settings
from .pipeline import ExamPipeline


_pipeline: ExamPipeline | None = None


def _get_pipeline() -> ExamPipeline:
    global _pipeline

    if _pipeline is None:
        _pipeline = ExamPipeline(get_settings())

    return _pipeline


def analyze_german_exam(file_path: str) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"German exam file was not found: {path}"
        )

    result = _get_pipeline().analyze(
        data=path.read_bytes(),
        filename=path.name,
    )

    return result.model_dump(mode="json")