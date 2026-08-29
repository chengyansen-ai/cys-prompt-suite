"""Shared input validation for the public prompt-generation API."""

from collections.abc import Collection
from numbers import Real

MAX_TEXT_LENGTH = 20_000


def validate_choice(name: str, value: str, choices: Collection[str]) -> str:
    """Return *value* when it is one of *choices*, otherwise raise clearly."""
    if not isinstance(value, str) or value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {allowed}")
    return value


def validate_optional_text(name: str, value: str | None) -> str | None:
    """Reject non-string and unreasonably large optional text fields."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string or None")
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"{name} exceeds the {MAX_TEXT_LENGTH}-character limit")
    return value


def validate_lora_strength(value: float) -> float:
    """Validate the normalized LoRA weight used by the prompt helpers."""
    if isinstance(value, bool) or not isinstance(value, Real) or not 0 <= value <= 1:
        raise ValueError("lora_strength must be a number between 0 and 1")
    return float(value)


def validate_positive_duration(value: float | None) -> float:
    """Validate a positive video duration and return it as float."""
    if value is None:
        raise ValueError("duration_seconds is required for this mode")
    if isinstance(value, bool) or not isinstance(value, Real) or value <= 0:
        raise ValueError("duration_seconds must be a positive number")
    return float(value)
