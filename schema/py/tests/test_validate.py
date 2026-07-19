"""Fixture-corpus tests — iterates the same expectations.json as the js suite."""

import json
from importlib import resources
from pathlib import Path

import pytest

from edon_lesson_schema import validate
from edon_lesson_schema.validator import _SCHEMA_FILES

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"
CANONICAL_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "lesson" / "1.0"
CORPUS_DIRS = ("valid", "invalid", "forward-compat")
EXPECTATIONS = json.loads((FIXTURES_DIR / "expectations.json").read_text("utf-8"))


def load_fixture(relative: str):
    return json.loads((FIXTURES_DIR / relative).read_text("utf-8"))


def classify(result: dict) -> str:
    if result["unsupportedMajor"]:
        return "unsupportedMajor"
    return "valid" if result["ok"] else "invalid"


@pytest.mark.parametrize(("fixture", "spec"), sorted(EXPECTATIONS.items()))
def test_fixture_corpus_agreement(fixture: str, spec):
    result = validate(load_fixture(fixture))
    expected = spec if isinstance(spec, str) else spec["outcome"]
    assert classify(result) == expected, result["errors"]
    if isinstance(spec, dict):
        # Negative-space DoD: the fixture must fail for its documented reason.
        contains = spec.get("messageContains")
        assert any(
            e["path"] == spec["errorPath"]
            and (contains is None or contains in e["message"])
            for e in result["errors"]
        ), f"expected an error at {spec['errorPath']}, got {result['errors']}"


def test_every_fixture_on_disk_has_an_expectations_entry():
    on_disk = sorted(
        f"{d}/{p.name}" for d in CORPUS_DIRS for p in (FIXTURES_DIR / d).glob("*.json")
    )
    assert on_disk == sorted(EXPECTATIONS)


def test_unsupported_major_short_circuits_with_empty_errors():
    result = validate(load_fixture("forward-compat/future-major-invalid.json"))
    assert result == {"ok": False, "unsupportedMajor": True, "errors": []}


@pytest.mark.parametrize("version", ["2.0\n", "1.0\n", "١.٠"])
def test_version_string_engine_parity(version: str):
    """Python's re lets $ match before a trailing newline and \\d match Unicode
    digits; ECMA does neither. Both wrappers must reject these identically as
    plain invalid (never valid, never unsupportedMajor)."""
    script = load_fixture("valid/minimal-slide-quiz.json")
    script["schema"] = version
    result = validate(script)
    assert result["unsupportedMajor"] is False
    assert result["ok"] is False
    assert any(e["path"] == "/schema" for e in result["errors"])


def test_packaged_schema_documents_match_canonical():
    """B1 drift guard: the copies shipped as package data must stay
    byte-identical to the canonical documents in schema/lesson/1.0."""
    packaged_root = resources.files("edon_lesson_schema").joinpath(
        "schemas", "lesson", "1.0"
    )
    canonical = sorted(
        str(p.relative_to(CANONICAL_SCHEMA_DIR)).replace("\\", "/")
        for p in CANONICAL_SCHEMA_DIR.rglob("*.json")
    )
    assert canonical == sorted(_SCHEMA_FILES)
    for relative in canonical:
        packaged_text = packaged_root.joinpath(*relative.split("/")).read_text("utf-8")
        canonical_text = (CANONICAL_SCHEMA_DIR / relative).read_text("utf-8")
        assert packaged_text == canonical_text, f"packaged copy of {relative} drifted"


def test_missing_excerpt_is_pinned_to_the_citation_path():
    result = validate(load_fixture("invalid/citation-missing-excerpt.json"))
    assert not result["ok"]
    assert any(e["path"].startswith("/blocks/0/citations/0") for e in result["errors"])


def test_dangling_correct_option_is_pinned_to_the_question_field():
    result = validate(load_fixture("invalid/quiz-mc-dangling-correct-option.json"))
    assert not result["ok"]
    assert result["errors"] == [
        {
            "path": "/blocks/0/questions/0/correctOptionId",
            "message": "must reference the id of one of the question's options",
        }
    ]


def test_missing_tenant_reports_the_field():
    result = validate(load_fixture("invalid/missing-tenant.json"))
    assert not result["ok"]
    assert any("tenantId" in e["message"] for e in result["errors"])
