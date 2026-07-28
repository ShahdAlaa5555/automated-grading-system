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
            # The Pearson exemplar PDF stores the question and handwritten answer as
            # two separate embedded images. Detect and crop those first.
            separated = _extract_question_and_answer_regions(page, matrix)
            if separated is not None:
                question_image, answer_image = separated
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
) -> tuple[Image.Image, Image.Image] | None:
    """Split layouts where question and answer are separate embedded images.

    This matches the uploaded Pearson exemplar: a decorative banner at the top,
    followed by one large question image and one or more large answer images below.
    The same TrOCR model can later OCR both regions; the split preserves their roles.
    """

    page_width = page.rect.width
    page_height = page.rect.height
    candidate_rects: list[fitz.Rect] = []

    for image_info in page.get_images(full=True):
        xref = image_info[0]
        for rect in page.get_image_rects(xref):
            rect = rect & page.rect
            if rect.is_empty:
                continue

            width_ratio = rect.width / page_width
            height_ratio = rect.height / page_height

            # Ignore logos, icons, tiny decorations, and the full-width top banner.
            if width_ratio < 0.45 or height_ratio < 0.06:
                continue
            if rect.y0 < page_height * 0.08:
                continue
            if rect.y1 > page_height * 0.96:
                continue

            if not any(_rects_almost_equal(rect, existing) for existing in candidate_rects):
                candidate_rects.append(rect)

    candidate_rects.sort(key=lambda rect: (rect.y0, rect.x0))
    if len(candidate_rects) < 2:
        return None

    question_rect = candidate_rects[0]
    answer_rects = [
        rect
        for rect in candidate_rects[1:]
        if rect.y0 >= question_rect.y1 - page_height * 0.01
    ]
    if not answer_rects:
        return None

    # Combine all answer image rectangles below the question into one page clip.
    answer_union = fitz.Rect(answer_rects[0])
    for rect in answer_rects[1:]:
        answer_union.include_rect(rect)

    question_image = _render_clip(page, matrix, question_rect)
    answer_image = _render_clip(page, matrix, answer_union)
    return question_image, answer_image


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
