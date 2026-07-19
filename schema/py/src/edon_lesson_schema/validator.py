"""Validator with semantics identical to the js wrapper (schema/js).

Contract (both languages): ``validate(script) -> {ok, unsupportedMajor, errors}``.
The major-version check runs FIRST and short-circuits: a script with a higher
major than SUPPORTED_MAJOR returns ``{ok: False, unsupportedMajor: True,
errors: []}`` even if it also has schema errors. Same-major future minors
validate — unknown block types and unknown fields pass through.

The JSON Schema documents ship inside the package (``schemas/lesson/1.0``) as
package data, so standard non-editable installs work; the test suite asserts
the packaged copies stay byte-identical to the canonical ``schema/lesson/1.0``.
"""

import json
import re
from importlib import resources

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SUPPORTED_MAJOR = 1

# fullmatch + ASCII [0-9] to mirror the js wrapper exactly: Python's `$` matches
# before a trailing newline and `\d` matches Unicode digits; ECMA does neither.
_VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+")

_SCHEMA_ROOT = resources.files("edon_lesson_schema").joinpath("schemas", "lesson", "1.0")

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
    resources_list = []
    for relative in _SCHEMA_FILES:
        document = json.loads(
            _SCHEMA_ROOT.joinpath(*relative.split("/")).read_text("utf-8")
        )
        if relative == "lesson.schema.json":
            lesson_schema = document
        resources_list.append((document["$id"], Resource.from_contents(document)))
    registry = Registry().with_resources(resources_list)
    return Draft202012Validator(lesson_schema, registry=registry)


_VALIDATOR = _build_validator()


def _referential_errors(script) -> list[dict]:
    """Referential rules JSON Schema cannot express — mirrored in the js wrapper:
    correctOptionId membership, and uniqueness of block ids, question ids (per
    quiz block), and option ids (per question). Loop structure mirrors the js
    wrapper so both languages emit the same errors in the same order."""
    errors = []
    blocks = script.get("blocks") if isinstance(script, dict) else None
    if not isinstance(blocks, list):
        return errors
    seen_block_ids = set()
    for block_index, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        block_id = block.get("id")
        if isinstance(block_id, str):
            if block_id in seen_block_ids:
                errors.append(
                    {
                        "path": f"/blocks/{block_index}/id",
                        "message": "must not duplicate another block's id",
                    }
                )
            seen_block_ids.add(block_id)
        if block.get("type") != "quiz":
            continue
        questions = block.get("questions")
        if not isinstance(questions, list):
            continue
        seen_question_ids = set()
        for question_index, question in enumerate(questions):
            if not isinstance(question, dict):
                continue
            question_id = question.get("id")
            if isinstance(question_id, str):
                if question_id in seen_question_ids:
                    errors.append(
                        {
                            "path": f"/blocks/{block_index}/questions/{question_index}/id",
                            "message": "must not duplicate another question's id in the same quiz block",
                        }
                    )
                seen_question_ids.add(question_id)
            options = question.get("options")
            if not isinstance(options, list):
                continue
            seen_option_ids = set()
            for option_index, option in enumerate(options):
                if not isinstance(option, dict) or not isinstance(option.get("id"), str):
                    continue
                option_id = option["id"]
                if option_id in seen_option_ids:
                    errors.append(
                        {
                            "path": f"/blocks/{block_index}/questions/{question_index}/options/{option_index}/id",
                            "message": "must not duplicate another option's id in the same question",
                        }
                    )
                seen_option_ids.add(option_id)
            if question.get("type") == "multipleChoice" and isinstance(
                question.get("correctOptionId"), str
            ):
                option_ids = [
                    option.get("id") for option in options if isinstance(option, dict)
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
        if isinstance(declared, str) and _VERSION_PATTERN.fullmatch(declared):
            if int(declared.split(".")[0]) > SUPPORTED_MAJOR:
                return {"ok": False, "unsupportedMajor": True, "errors": []}

    errors = []
    for error in _VALIDATOR.iter_errors(script):
        path = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append({"path": path, "message": error.message})
    errors.extend(_referential_errors(script))

    return {"ok": not errors, "unsupportedMajor": False, "errors": errors}
