"""Fixture-corpus tests — iterates the same expectations.json as the js suite."""

import json
from pathlib import Path

import pytest

from edon_lesson_schema import validate

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"
EXPECTATIONS = json.loads((FIXTURES_DIR / "expectations.json").read_text("utf-8"))


def load_fixture(relative: str):
    return json.loads((FIXTURES_DIR / relative).read_text("utf-8"))


def classify(result: dict) -> str:
    if result["unsupportedMajor"]:
        return "unsupportedMajor"
    return "valid" if result["ok"] else "invalid"


@pytest.mark.parametrize(("fixture", "expected"), sorted(EXPECTATIONS.items()))
def test_fixture_corpus_agreement(fixture: str, expected: str):
    result = validate(load_fixture(fixture))
    assert classify(result) == expected, result["errors"]


def test_unsupported_major_short_circuits_with_empty_errors():
    result = validate(load_fixture("forward-compat/future-major-invalid.json"))
    assert result == {"ok": False, "unsupportedMajor": True, "errors": []}


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
