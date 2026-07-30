from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .config import get_settings
from .pipeline import ExamPipeline


ProgressCallback = Callable[[str, int], None]

_pipeline: ExamPipeline | None = None


def _get_pipeline() -> ExamPipeline:
    global _pipeline

    if _pipeline is None:
        _pipeline = ExamPipeline(get_settings())

    return _pipeline


def analyze_german_exam(
    file_path: str,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"German exam file was not found: {path}"
        )

    return _get_pipeline().analyze_for_grading_system(
        data=path.read_bytes(),
        filename=path.name,
        progress_callback=progress_callback,
    )