"""Lesson Script Schema v1.0 — jsonschema validator wrapper.

Monorepo-internal package: it reads the JSON Schema documents from
``schema/lesson/1.0`` relative to the repo layout, so install it editable
(``uv pip install -e './schema/py[dev]'``).
"""

from edon_lesson_schema.validator import SUPPORTED_MAJOR, validate

__all__ = ["SUPPORTED_MAJOR", "validate"]
