from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

from .config import Settings


@dataclass(frozen=True)
class LineCrop:
    image: Image.Image
    box: tuple[int, int, int, int]


def segment_text_lines(page: Image.Image, settings: Settings) -> list[LineCrop]:
    """Segment a page into approximate text-line images for TrOCR.

    The checkpoint is intended for single-line input, so this uses classical image
    processing to remove long form/table rules, connect nearby characters, and merge
    contours that occupy the same vertical band.
    """

    rgb = np.asarray(page.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape

    # Downscale extremely large scans only for detection; coordinates are mapped back.
    detection_scale = min(1.0, 2400.0 / max(width, 1))
    if detection_scale < 1.0:
        detection = cv2.resize(
            gray,
            (int(width * detection_scale), int(height * detection_scale)),
            interpolation=cv2.INTER_AREA,
        )
    else:
        detection = gray

    dh, dw = detection.shape
    blurred = cv2.GaussianBlur(detection, (3, 3), 0)
    block_size = max(31, (min(dw, dh) // 45) | 1)
    block_size = min(block_size, 101)
    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size,
        15,
    )

    # Handwritten answer sheets often have dotted horizontal writing guides.
    # When a regular set of guides is found, the spaces between them are much
    # more reliable line crops than generic contour merging.
    ruled_bands = _detect_ruled_line_bands(binary, settings)

    # Suppress long horizontal/vertical borders common in exam forms.
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (max(40, dw // 8), 1)
    )
    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, max(40, dh // 12))
    )
    horizontal_rules = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_rules = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
    rules = cv2.bitwise_or(horizontal_rules, vertical_rules)
    text_mask = cv2.subtract(binary, rules)

    # Join letters and words into line-level components.
    join_width = max(18, dw // 65)
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (join_width, 3))
    connected = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, close_kernel)
    connected = cv2.dilate(
        connected,
        cv2.getStructuringElement(cv2.MORPH_RECT, (max(5, dw // 250), 3)),
        iterations=1,
    )

    if ruled_bands:
        merged = ruled_bands
    else:
        contours, _ = cv2.findContours(
            connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        min_h = max(5, int(settings.line_min_height * detection_scale))
        max_h = max(min_h + 1, int(dh * settings.line_max_height_ratio))
        min_w = max(12, int(dw * settings.line_min_width_ratio))

        boxes: list[tuple[int, int, int, int]] = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < min_w or h < min_h or h > max_h:
                continue
            # Reject huge near-page blocks and tiny isolated punctuation.
            if w > dw * 0.98 and h > dh * 0.12:
                continue
            boxes.append((x, y, x + w, y + h))

        merged = _merge_vertical_bands(boxes, dh)
        merged.sort(key=lambda b: (b[1], b[0]))
        merged = merged[: settings.max_lines_per_page]

        if not merged:
            # A conservative fallback: use horizontal projection to detect occupied bands.
            merged = _projection_bands(text_mask, settings)

    output: list[LineCrop] = []
    inv_scale = 1.0 / detection_scale
    for x1, y1, x2, y2 in merged[: settings.max_lines_per_page]:
        ox1 = max(0, int(x1 * inv_scale) - settings.line_padding_x)
        oy1 = max(0, int(y1 * inv_scale) - settings.line_padding_y)
        ox2 = min(width, int(x2 * inv_scale) + settings.line_padding_x)
        oy2 = min(height, int(y2 * inv_scale) + settings.line_padding_y)
        if ox2 <= ox1 or oy2 <= oy1:
            continue

        raw_crop = page.crop((ox1, oy1, ox2, oy2)).convert("L")
        if not _has_meaningful_text(raw_crop):
            continue

        crop = ImageOps.autocontrast(raw_crop, cutoff=1)
        crop = ImageEnhance.Contrast(crop).enhance(1.25)
        crop = _pad_to_readable_line(crop)

        output.append(
            LineCrop(
                crop.convert("RGB"),
                (ox1, oy1, ox2, oy2),
            )
        )

    return output


def _detect_ruled_line_bands(
    binary: np.ndarray,
    settings: Settings,
) -> list[tuple[int, int, int, int]]:
    """Return text bands between regularly spaced dotted horizontal guides."""

    height, width = binary.shape
    connector_width = max(7, width // 140)
    connector = cv2.getStructuringElement(cv2.MORPH_RECT, (connector_width, 1))
    connected_dots = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, connector)

    long_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (max(40, width // 8), 1)
    )
    horizontal = cv2.morphologyEx(
        connected_dots, cv2.MORPH_OPEN, long_kernel
    )
    coverage = (horizontal > 0).sum(axis=1)
    active = coverage >= width * 0.40

    centers: list[int] = []
    start: int | None = None
    for row, is_active in enumerate(active):
        if is_active and start is None:
            start = row
        elif not is_active and start is not None:
            centers.append((start + row - 1) // 2)
            start = None
    if start is not None:
        centers.append((start + height - 1) // 2)

    if len(centers) < 3:
        return []

    spacings = np.diff(np.asarray(centers, dtype=np.float32))
    median_spacing = float(np.median(spacings))
    if median_spacing < max(18, settings.line_min_height * 1.5):
        return []

    # Reject irregular detections such as box borders and random long strokes.
    regular = [centers[0]]
    for center in centers[1:]:
        gap = center - regular[-1]
        if median_spacing * 0.65 <= gap <= median_spacing * 1.35:
            regular.append(center)
    if len(regular) < 3:
        return []

    bands: list[tuple[int, int, int, int]] = []
    min_ink = max(20, int(width * 0.01))
    for top_guide, bottom_guide in zip(regular, regular[1:]):
        top = max(0, top_guide + 2)
        bottom = min(height, bottom_guide - 2)
        if bottom - top < max(8, settings.line_min_height):
            continue

        band = binary[top:bottom]
        ys, xs = np.where(band > 0)
        if len(xs) < min_ink:
            continue

        left = max(0, int(xs.min()))
        right = min(width, int(xs.max()) + 1)
        if right - left < max(12, int(width * settings.line_min_width_ratio)):
            continue
        bands.append((left, top, right, bottom))

    return bands[: settings.max_lines_per_page]


def _merge_vertical_bands(
    boxes: list[tuple[int, int, int, int]], page_height: int
) -> list[tuple[int, int, int, int]]:
    if not boxes:
        return []
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    bands: list[list[int]] = []
    tolerance = max(5, page_height // 250)

    for x1, y1, x2, y2 in boxes:
        center = (y1 + y2) / 2
        matched = False
        for band in bands:
            by1, by2 = band[1], band[3]
            band_center = (by1 + by2) / 2
            vertical_overlap = max(0, min(y2, by2) - max(y1, by1))
            smaller_height = max(1, min(y2 - y1, by2 - by1))
            same_line = vertical_overlap / smaller_height >= 0.30
            close_center = abs(center - band_center) <= max(y2 - y1, by2 - by1) * 0.65 + tolerance
            if same_line or close_center:
                band[0] = min(band[0], x1)
                band[1] = min(band[1], y1)
                band[2] = max(band[2], x2)
                band[3] = max(band[3], y2)
                matched = True
                break
        if not matched:
            bands.append([x1, y1, x2, y2])

    return [tuple(band) for band in bands]


def _projection_bands(mask: np.ndarray, settings: Settings) -> list[tuple[int, int, int, int]]:
    h, w = mask.shape
    occupancy = (mask > 0).sum(axis=1)
    active = occupancy > max(3, int(w * 0.004))
    bands: list[tuple[int, int, int, int]] = []
    start: int | None = None

    for y, is_active in enumerate(active):
        if is_active and start is None:
            start = y
        elif not is_active and start is not None:
            if y - start >= max(4, int(settings.line_min_height * 0.7)):
                bands.append((0, start, w, y))
            start = None
    if start is not None and h - start >= max(4, int(settings.line_min_height * 0.7)):
        bands.append((0, start, w, h))
    return bands


def _has_meaningful_text(image: Image.Image) -> bool:
    gray = np.asarray(image.convert("L"))

    _, binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    component_count, _, stats, _ = cv2.connectedComponentsWithStats(
        (binary > 0).astype(np.uint8),
        connectivity=8,
    )

    crop_height, crop_width = gray.shape
    min_component_height = max(7, int(crop_height * 0.18))

    meaningful_components: list[tuple[int, int, int, int, int]] = []

    for component_index in range(1, component_count):
        x, y, width, height, area = stats[component_index]

        # Dotted guides normally produce very small 4–5 pixel components.
        if height < min_component_height:
            continue

        if width < 2:
            continue

        if area < max(15, height * 2):
            continue

        # Reject a flat horizontal rule if one remains.
        if width > crop_width * 0.80 and height <= 4:
            continue

        meaningful_components.append(
            (
                int(x),
                int(y),
                int(width),
                int(height),
                int(area),
            )
        )

    if not meaningful_components:
        return False

    total_area = sum(component[4] for component in meaningful_components)

    left = min(component[0] for component in meaningful_components)
    right = max(
        component[0] + component[2]
        for component in meaningful_components
    )
    text_span = right - left

    has_multiple_letters = (
        len(meaningful_components) >= 2
        and total_area >= 80
        and text_span >= 20
    )

    has_one_large_character = any(
        area >= 120 and height >= 12
        for _, _, _, height, area in meaningful_components
    )

    return has_multiple_letters or has_one_large_character


def _pad_to_readable_line(image: Image.Image) -> Image.Image:
    w, h = image.size
    min_height = 48
    target_h = max(min_height, h + 16)
    target_w = max(w + 24, int(target_h * 2.2))
    canvas = Image.new("L", (target_w, target_h), 255)
    canvas.paste(image, ((target_w - w) // 2, (target_h - h) // 2))
    return canvas
