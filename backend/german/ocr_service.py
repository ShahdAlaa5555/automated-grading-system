from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Literal

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

from .config import Settings
from .schemas import OCRLine, OCRPage
from .document_loader import LoadedPage
from .line_segmenter import segment_text_lines

LOGGER = logging.getLogger(__name__)
OCRKind = Literal["printed", "handwritten"]


class OCRService:
    def __init__(self, settings: Settings):
        self.settings = settings

        self._handwritten_processor: TrOCRProcessor | None = None
        self._handwritten_model: VisionEncoderDecoderModel | None = None
        self._printed_processor: TrOCRProcessor | None = None
        self._printed_model: VisionEncoderDecoderModel | None = None
        self._device: torch.device | None = None

        self._handwritten_load_lock = threading.Lock()
        self._printed_load_lock = threading.Lock()
        self._inference_lock = threading.Lock()

    @property
    def loaded(self) -> bool:
        """The health endpoint treats the answer OCR as the main OCR model."""
        return (
            self._handwritten_model is not None
            and self._handwritten_processor is not None
        )

    @property
    def device_name(self) -> str:
        return str(self._device) if self._device is not None else "not loaded"

    def load(self) -> None:
        """Load the German handwritten model used for student answers."""
        if self.loaded:
            return

        with self._handwritten_load_lock:
            if self.loaded:
                return

            processor, model = self._load_checkpoint(
                model_id=self.settings.trocr_model_id,
                model_path=self.settings.trocr_model_path,
                label="German handwritten answer OCR",
            )
            self._handwritten_processor = processor
            self._handwritten_model = model

    def _load_printed(self) -> None:
        """Load the English printed model only when a question image needs OCR."""
        if self._printed_model is not None and self._printed_processor is not None:
            return

        with self._printed_load_lock:
            if self._printed_model is not None and self._printed_processor is not None:
                return

            processor, model = self._load_checkpoint(
                model_id=self.settings.printed_trocr_model_id,
                model_path=self.settings.printed_trocr_model_path,
                label="English printed question OCR",
            )
            self._printed_processor = processor
            self._printed_model = model

    def _load_checkpoint(
        self,
        model_id: str,
        model_path: Path,
        label: str,
    ) -> tuple[TrOCRProcessor, VisionEncoderDecoderModel]:
        if self.settings.torch_num_threads > 0:
            torch.set_num_threads(self.settings.torch_num_threads)

        if self._device is None:
            self._device = self._resolve_device()

        source = self._resolve_model_source(model_path, model_id)
        LOGGER.info("Loading %s from %s on %s", label, source, self._device)

        try:
            processor = TrOCRProcessor.from_pretrained(
                source,
                local_files_only=self.settings.trocr_offline_only,
                use_fast=False,
            )
            model = VisionEncoderDecoderModel.from_pretrained(
                source,
                local_files_only=self.settings.trocr_offline_only,
                use_safetensors=True,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Could not load {label}. Run scripts/download_models.py while online, "
                "or check the configured model path and TROCR_OFFLINE_ONLY. "
                f"Original error: {exc}"
            ) from exc

        model.to(self._device)
        model.eval()
        return processor, model

    def recognize_pages(self, pages: list[LoadedPage]) -> list[OCRPage]:
        self.load()
        results: list[OCRPage] = []
        for page_number, page in enumerate(pages, start=1):
            results.append(self._recognize_page(page, page_number))
        return results

    def _recognize_page(self, page: LoadedPage, page_number: int) -> OCRPage:
        # Prefer selectable PDF text when it exists. Only use the printed OCR model
        # when the document loader extracted the question as an image.
        question_text = page.printed_text.strip()
        question_limit_reached = False
        if page.question_image is not None:
            question_lines, question_limit_reached = self._recognize_image_lines(
                page.question_image,
                kind="printed",
            )
            question_text = "\n".join(line.text for line in question_lines)

        answer_lines, answer_limit_reached = self._recognize_image_lines(
            page.image,
            kind="handwritten",
        )
        answer_text = "\n".join(line.text for line in answer_lines)

        warnings: list[str] = []
        if not answer_lines:
            warnings.append("No handwritten text-line regions were detected on this page.")
        if question_limit_reached:
            warnings.append(
                f"Question line limit ({self.settings.max_lines_per_page}) reached."
            )
        if answer_limit_reached:
            warnings.append(
                f"Answer line limit ({self.settings.max_lines_per_page}) reached."
            )
        if page.separation_mode == "full_page" and not question_text:
            warnings.append(
                "Question and answer were not separated; the page was OCRed as one image."
            )

        return OCRPage(
            page_number=page_number,
            printed_text=question_text,
            text=answer_text,
            lines=answer_lines,
            warning=" ".join(warnings) or None,
        )

    def _recognize_image_lines(
        self,
        image: Image.Image,
        kind: OCRKind,
    ) -> tuple[list[OCRLine], bool]:
        crops = segment_text_lines(image, self.settings)
        if not crops:
            return [], False

        if kind == "printed":
            self._load_printed()
            assert self._printed_processor is not None
            assert self._printed_model is not None
            processor = self._printed_processor
            model = self._printed_model
            max_new_tokens = self.settings.printed_trocr_max_new_tokens
        else:
            self.load()
            assert self._handwritten_processor is not None
            assert self._handwritten_model is not None
            processor = self._handwritten_processor
            model = self._handwritten_model
            max_new_tokens = self.settings.trocr_max_new_tokens

        images = [crop.image for crop in crops]
        texts: list[str] = []
        batch_size = self.settings.trocr_batch_size
        for start in range(0, len(images), batch_size):
            texts.extend(
                self._recognize_batch(
                    images[start : start + batch_size],
                    processor=processor,
                    model=model,
                    max_new_tokens=max_new_tokens,
                )
            )

        lines: list[OCRLine] = []
        for index, (crop, text) in enumerate(zip(crops, texts, strict=True), start=1):
            cleaned = " ".join(text.strip().split())
            if not cleaned:
                continue
            lines.append(
                OCRLine(
                    line_number=index,
                    text=cleaned,
                    box=list(crop.box),
                )
            )

        return lines, len(crops) >= self.settings.max_lines_per_page

    def _recognize_batch(
        self,
        images: list[Image.Image],
        processor: TrOCRProcessor,
        model: VisionEncoderDecoderModel,
        max_new_tokens: int,
    ) -> list[str]:
        assert self._device is not None

        with self._inference_lock, torch.inference_mode():
            pixel_values = processor(
                images=images,
                return_tensors="pt",
            ).pixel_values.to(self._device)
            generated_ids = model.generate(
                pixel_values,
                max_new_tokens=max_new_tokens,
                num_beams=self.settings.trocr_num_beams,
                do_sample=False,
                early_stopping=self.settings.trocr_num_beams > 1,
            )
            return processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
            )

    def _resolve_model_source(self, model_path: Path, model_id: str) -> str:
        local_path = Path(model_path)
        required_candidates = [
            local_path / "config.json",
            local_path / "preprocessor_config.json",
        ]
        if all(path.exists() for path in required_candidates):
            return str(local_path)
        return model_id

    def _resolve_device(self) -> torch.device:
        configured = self.settings.trocr_device.strip().lower()
        if configured == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            if (
                getattr(torch.backends, "mps", None)
                and torch.backends.mps.is_available()
            ):
                return torch.device("mps")
            return torch.device("cpu")
        return torch.device(configured)
