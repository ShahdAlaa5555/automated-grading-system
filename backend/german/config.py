from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


GERMAN_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = GERMAN_ROOT.parent


class Settings(BaseSettings):
    """Configuration for the German correction module."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "German Exam Corrector"
    app_version: str = "1.0.0"

    max_upload_mb: int = Field(default=30, ge=1, le=200)
    max_pages: int = Field(default=12, ge=1, le=100)
    pdf_render_dpi: int = Field(default=220, ge=100, le=400)

    # German handwritten answer OCR
    trocr_model_id: str = (
        "EpsilonGreedy/TrOCR_small_german_handwritten"
    )
    trocr_model_path: Path = (
        GERMAN_ROOT
        / "models"
        / "trocr-small-german-handwritten"
    )

    # English printed question OCR
    printed_trocr_model_id: str = (
        "microsoft/trocr-small-printed"
    )
    printed_trocr_model_path: Path = (
        GERMAN_ROOT
        / "models"
        / "trocr-small-printed"
    )
    printed_trocr_max_new_tokens: int = Field(
        default=64,
        ge=16,
        le=256,
    )

    # Shared TrOCR settings
    trocr_offline_only: bool = False
    trocr_device: str = "auto"
    trocr_batch_size: int = Field(default=4, ge=1, le=32)
    trocr_max_new_tokens: int = Field(
        default=48,
        ge=16,
        le=256,
    )
    trocr_num_beams: int = Field(default=1, ge=1, le=5)
    torch_num_threads: int = Field(default=0, ge=0, le=64)

    # Line segmentation
    max_lines_per_page: int = Field(default=90, ge=1, le=300)
    line_min_height: int = Field(default=12, ge=4, le=100)
    line_max_height_ratio: float = Field(
        default=0.18,
        gt=0.01,
        le=0.8,
    )
    line_min_width_ratio: float = Field(
        default=0.05,
        gt=0.0,
        le=1.0,
    )
    line_padding_x: int = Field(default=18, ge=0, le=200)
    line_padding_y: int = Field(default=8, ge=0, le=100)

    # Ollama / Qwen
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:1.5b-instruct"
    ollama_timeout_seconds: int = Field(
        default=300,
        ge=10,
        le=1800,
    )
    ollama_keep_alive: str = "10m"
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
    )
    llm_num_ctx: int = Field(
        default=8192,
        ge=2048,
        le=131072,
    )
    llm_num_predict: int = Field(
        default=1400,
        ge=128,
        le=8192,
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()