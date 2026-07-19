#!/usr/bin/env python3
"""i18n lint gate, backend half (AD-20): no inline user-facing copy in API code.

Scans backend/src/edon/api/** for string literals that look like user copy
(a word, a space, another word). Machine tokens ("ok", "not_found", header names)
pass; docstrings are exempt. Escape hatch: append `# i18n-ok` to the line, for
strings that are genuinely not user-facing (log fragments, content types).

User-facing copy belongs in language catalogs under `surface.component.slug` keys;
API responses carry `code + params` for first-party UIs (AD-20).
"""

import ast
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
API_ROOT = REPO_ROOT / "backend" / "src" / "edon" / "api"
COPY_RE = re.compile(r"[A-Za-z]+ [A-Za-z]+")


def docstring_constants(tree: ast.AST) -> set[int]:
    """Line numbers of docstring constants (exempt)."""
    exempt: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                exempt.add(body[0].value.lineno)
    return exempt


def main() -> int:
    failures: list[str] = []
    for path in sorted(API_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        tree = ast.parse(source, filename=str(path))
        exempt_lines = docstring_constants(tree)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            if node.lineno in exempt_lines or not COPY_RE.search(node.value):
                continue
            if "# i18n-ok" in lines[node.lineno - 1]:
                continue
            failures.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {node.value!r}")
    if failures:
        sys.stdout.write(
            "i18n gate FAILED (AD-20) — inline user copy in API code; move it to a language\n"
            "catalog key, or mark genuinely non-user-facing strings with `# i18n-ok`:\n"
        )
        sys.stdout.write("\n".join(failures) + "\n")
        return 1
    sys.stdout.write("i18n gate passed (backend API)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
