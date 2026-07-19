"""Lesson Script Schema v1.0 — jsonschema validator wrapper.

The JSON Schema documents ship inside the package as package data
(``schemas/lesson/1.0``), so both editable and standard installs work. The
canonical documents live at ``schema/lesson/1.0`` in the monorepo; the test
suite asserts the packaged copies stay byte-identical to them.
"""

from edon_lesson_schema.validator import SUPPORTED_MAJOR, validate

__all__ = ["SUPPORTED_MAJOR", "validate"]
