"""Validator with semantics identical to the js wrapper (schema/js).

Contract (both languages): ``validate(script) -> {ok, unsupportedMajor, errors}``.
The major-version check runs FIRST and short-circuits: a script with a higher
major than SUPPORTED_MAJOR returns ``{ok: False, unsupportedMajor: True,
errors: []}`` even if it also has schema errors. Same-major future minors
validate — unknown block types and unknown fields pass through.
"""

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SUPPORTED_MAJOR = 1

_SCHEMA_DIR = Path(__file__).resolve().parents[3] / "lesson" / "1.0"
_VERSION_PATTERN = re.compile(r"^\d+\.\d+$")

_SCHEMA_FILES = [
    "lesson.schema.json",
    "defs.schema.json",
    "blocks/slide.schema.json",
    "blocks/narration.schema.json",
    "blocks/quiz.schema.json",
    "blocks/diagram.schema.json",
    "blocks/model3d.schema.json",
    "blocks/simulation.schema.json",
]


def _build_validator() -> Draft202012Validator:
    lesson_schema = None
    resources = []
    for relative in _SCHEMA_FILES:
        document = json.loads((_SCHEMA_DIR / relative).read_text("utf-8"))
        if relative == "lesson.schema.json":
            lesson_schema = document
        resources.append((document["$id"], Resource.from_contents(document)))
    registry = Registry().with_resources(resources)
    return Draft202012Validator(lesson_schema, registry=registry)


_VALIDATOR = _build_validator()


def _referential_errors(script) -> list[dict]:
    """Referential rules JSON Schema cannot express — mirrored in the js wrapper."""
    errors = []
    blocks = script.get("blocks") if isinstance(script, dict) else None
    if not isinstance(blocks, list):
        return errors
    for block_index, block in enumerate(blocks):
        if not isinstance(block, dict) or block.get("type") != "quiz":
            continue
        questions = block.get("questions")
        if not isinstance(questions, list):
            continue
        for question_index, question in enumerate(questions):
            if (
                isinstance(question, dict)
                and question.get("type") == "multipleChoice"
                and isinstance(question.get("options"), list)
                and isinstance(question.get("correctOptionId"), str)
            ):
                option_ids = [
                    option.get("id")
                    for option in question["options"]
                    if isinstance(option, dict)
                ]
                if question["correctOptionId"] not in option_ids:
                    errors.append(
                        {
                            "path": f"/blocks/{block_index}/questions/{question_index}/correctOptionId",
                            "message": "must reference the id of one of the question's options",
                        }
                    )
    return errors


def validate(script) -> dict:
    if isinstance(script, dict):
        declared = script.get("schema")
        if isinstance(declared, str) and _VERSION_PATTERN.match(declared):
            if int(declared.split(".")[0]) > SUPPORTED_MAJOR:
                return {"ok": False, "unsupportedMajor": True, "errors": []}

    errors = []
    for error in _VALIDATOR.iter_errors(script):
        path = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append({"path": path if path != "/" else "/", "message": error.message})
    errors.extend(_referential_errors(script))

    return {"ok": not errors, "unsupportedMajor": False, "errors": errors}
