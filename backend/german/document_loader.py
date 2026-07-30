from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageOps, ImageSequence

from .config import Settings


SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


class DocumentError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedPage:
    """Images and text required to OCR one exam page.

    ``image`` is the region that should be treated as the student's answer.
    ``question_image`` is an optional separately embedded/cropped question region.
    ``printed_text`` is used for PDFs whose printed question exists as selectable text.
    """

    image: Image.Image
    question_image: Image.Image | None = None
    printed_text: str = ""
    separation_mode: str = "full_page"


def load_document_pages(
    data: bytes,
    filename: str,
    settings: Settings,
) -> list[LoadedPage]:
    if not data:
        raise DocumentError("The uploaded file is empty.")
    if len(data) > settings.max_upload_bytes:
        raise DocumentError(
            f"File is larger than the configured limit of {settings.max_upload_mb} MB."
        )

    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(data, settings)
    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        return _load_image(data, settings)
    raise DocumentError(
        "Unsupported file type. Upload PDF, PNG, JPG, JPEG, WEBP, BMP, TIF, or TIFF."
    )


def _load_pdf(data: bytes, settings: Settings) -> list[LoadedPage]:
    try:
        document = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:  # pragma: no cover - depends on malformed PDFs
        raise DocumentError(f"Could not open PDF: {exc}") from exc

    if document.page_count == 0:
        document.close()
        raise DocumentError("The PDF contains no pages.")
    if document.page_count > settings.max_pages:
        count = document.page_count
        document.close()
        raise DocumentError(
            f"The PDF has {count} pages; the configured maximum is {settings.max_pages}."
        )

    scale = settings.pdf_render_dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    pages: list[LoadedPage] = []

    try:
        for page in document:
            separated_blocks = _extract_question_and_answer_regions(
                page,
                matrix,
            )

            if separated_blocks:
                # One physical PDF page may contain several question-answer blocks.
                # Each block becomes one logical page for the German OCR pipeline.
                for question_image, answer_image in separated_blocks:
                    pages.append(
                        LoadedPage(
                            image=answer_image,
                            question_image=question_image,
                            printed_text="",
                            separation_mode="embedded_regions",
                        )
                    )

                continue

            # Fallback for ordinary text PDFs: read selectable printed text and mask
            # its coordinates from the rendered page before handwriting OCR.
            printed_text = page.get_text("text", sort=True).strip()
            printed_words = page.get_text("words", sort=True)
            rendered = _render_page(page, matrix)

            if printed_text and printed_words:
                answer_image = _mask_selectable_text(rendered, printed_words, scale)
                mode = "selectable_text_mask"
            else:
                answer_image = rendered
                mode = "full_page"

            pages.append(
                LoadedPage(
                    image=answer_image,
                    question_image=None,
                    printed_text=printed_text,
                    separation_mode=mode,
                )
            )
    finally:
        document.close()

    return pages


def _extract_question_and_answer_regions(
    page: fitz.Page,
    matrix: fitz.Matrix,
) -> list[tuple[Image.Image, Image.Image]]:
    """
    Extract multiple question-answer pairs from one physical PDF page.

    This supports Pearson-style pages where the printed question and
    handwritten answer are stored as separate embedded images.

    Example detected order:

        question 1
        answer 1
        question 2
        answer 2

    The returned list contains:

        [
            (question_1_image, answer_1_image),
            (question_2_image, answer_2_image),
        ]
    """

    page_width = page.rect.width
    page_height = page.rect.height

    candidate_rects: list[fitz.Rect] = []

    for image_info in page.get_images(full=True):
        xref = image_info[0]

        for raw_rect in page.get_image_rects(xref):
            rect = raw_rect & page.rect

            if rect.is_empty:
                continue

            width_ratio = rect.width / page_width
            height_ratio = rect.height / page_height

            # Ignore logos, icons, and very small decorations.
            if width_ratio < 0.45 or height_ratio < 0.06:
                continue

            # Ignore page footer images.
            # if rect.y1 > page_height * 0.98:
            #     continue

            # Ignore wide, shallow decorative Pearson banners wherever
            # they appear on the combined page.
            is_decorative_banner = (
                width_ratio >= 0.90
                and height_ratio <= 0.13
            )

            if is_decorative_banner:
                continue

            # The same image xref may appear more than once in the list.
            # Do not add duplicate rectangles.
            already_added = any(
                _rects_almost_equal(rect, existing)
                for existing in candidate_rects
            )

            if already_added:
                continue

            candidate_rects.append(fitz.Rect(rect))

    candidate_rects.sort(
        key=lambda region: (
            region.y0,
            region.x0,
        )
    )

    if len(candidate_rects) < 2:
        return []

    question_indexes: list[int] = []

    for index, rect in enumerate(candidate_rects):
        aspect_ratio = rect.width / max(rect.height, 1)
        height_ratio = rect.height / page_height

        # Pearson question boxes are wide and relatively short.
        # The handwritten response regions are normally taller.
        looks_like_question = (
            aspect_ratio >= 2.60
            and height_ratio <= 0.30
        )

        if looks_like_question:
            question_indexes.append(index)

    if not question_indexes:
        return []

    result: list[tuple[Image.Image, Image.Image]] = []

    for position, question_index in enumerate(question_indexes):
        question_rect = candidate_rects[question_index]

        if position + 1 < len(question_indexes):
            next_question_index = question_indexes[position + 1]
        else:
            next_question_index = len(candidate_rects)

        # Everything between this question and the next question belongs
        # to this question's handwritten answer.
        answer_rects = candidate_rects[
            question_index + 1 : next_question_index
        ]

        if not answer_rects:
            continue

        answer_union = fitz.Rect(answer_rects[0])

        for answer_rect in answer_rects[1:]:
            answer_union.include_rect(answer_rect)

        question_image = _render_clip(
            page,
            matrix,
            question_rect,
        )

        answer_image = _render_clip(
            page,
            matrix,
            answer_union,
        )

        result.append(
            (
                question_image,
                answer_image,
            )
        )

    return result

def _rects_almost_equal(first: fitz.Rect, second: fitz.Rect, tolerance: float = 1.0) -> bool:
    return all(
        abs(a - b) <= tolerance
        for a, b in zip(
            (first.x0, first.y0, first.x1, first.y1),
            (second.x0, second.y0, second.x1, second.y1),
            strict=True,
        )
    )


def _render_page(page: fitz.Page, matrix: fitz.Matrix) -> Image.Image:
    pixmap = page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
    return ImageOps.exif_transpose(
        Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    )


def _render_clip(
    page: fitz.Page,
    matrix: fitz.Matrix,
    rect: fitz.Rect,
) -> Image.Image:
    pixmap = page.get_pixmap(
        matrix=matrix,
        clip=rect,
        alpha=False,
        colorspace=fitz.csRGB,
    )
    return ImageOps.exif_transpose(
        Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    )


def _mask_selectable_text(
    image: Image.Image,
    words: list[tuple],
    scale: float,
) -> Image.Image:
    """Paint selectable PDF words white on the rendered page."""

    masked = image.copy().convert("RGB")
    draw = ImageDraw.Draw(masked)
    width, height = masked.size
    padding = max(2, round(scale * 1.2))

    for word in words:
        if len(word) < 5:
            continue

        x0, y0, x1, y1 = word[:4]
        left = max(0, int(x0 * scale) - padding)
        top = max(0, int(y0 * scale) - padding)
        right = min(width, int(x1 * scale) + padding)
        bottom = min(height, int(y1 * scale) + padding)

        if right > left and bottom > top:
            draw.rectangle((left, top, right, bottom), fill="white")

    return masked


def _load_image(data: bytes, settings: Settings) -> list[LoadedPage]:
    try:
        source = Image.open(BytesIO(data))
    except Exception as exc:
        raise DocumentError(f"Could not open image: {exc}") from exc

    pages: list[LoadedPage] = []
    try:
        for frame in ImageSequence.Iterator(source):
            image = ImageOps.exif_transpose(frame.copy()).convert("RGB")
            pages.append(
                LoadedPage(
                    image=image,
                    question_image=None,
                    printed_text="",
                    separation_mode="full_page",
                )
            )
            if len(pages) >= settings.max_pages:
                break
    finally:
        source.close()

    if not pages:
        raise DocumentError("The image contains no readable frames.")
    return pages
