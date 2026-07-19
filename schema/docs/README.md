# Lesson Script Schema v1.0 — Package Documentation

The Lesson Script Schema is the single content contract of e-DON Lesson Studio (AD-2, I-3):
the versioned JSON shape shared by the generation pipeline, the Authoring UI, the embeddable
Player, and every future renderer. **No Lesson Script persists without passing this package's
validator; Published Versions stay playable forever.**

## Package layout

| Path | What it is |
| --- | --- |
| `lesson/1.0/` | JSON Schema 2020-12 documents (`$id` base: `https://schema.edon.education/lesson/1.0/`) |
| `fixtures/` | The shared fixture corpus + `expectations.json` (the cross-language agreement manifest) |
| `js/` | `@edon/lesson-schema` — ajv wrapper, **toolchain/CI only** (the Player performs no runtime validation, AD-10). Plain JavaScript — no TypeScript ([HARD] §2) |
| `py/` | `edon-lesson-schema` — jsonschema wrapper for the backend. The schema documents ship inside the package as package data, so standard (non-editable) installs work; a test asserts the packaged copies stay byte-identical to `lesson/1.0` |
| `docs/` | This documentation: [block-types.md](block-types.md), [versioning.md](versioning.md), [reserved-extensions.md](reserved-extensions.md) |

## Validator contract (identical in both languages)

```
validate(script) -> { ok: bool, unsupportedMajor: bool, errors: [{path, message}] }
```

- The **major-version check runs first and short-circuits**: a script whose `schema` major
  exceeds the package's supported major returns `{ok: false, unsupportedMajor: true, errors: []}`
  even if the script also has schema errors. Consumers map this to the designed can't-play state.
- `errors[].path` is a JSON-pointer-style instance path (`/blocks/0/citations/0`) — validation
  failures are attributable to a specific block and field (inline error pinning in Authoring).
- Referential rules JSON Schema cannot express are implemented **inside `validate()` in both
  wrappers with identical semantics**: a multiple-choice question's `correctOptionId` must
  reference the id of one of its `options`; block ids must be unique across the script
  (AD-23 — they key citations, view marks, patches, progress rows); question ids must be
  unique within their quiz block; option ids must be unique within their question.
- Both test suites iterate the same `fixtures/expectations.json`; agreement between the two
  validators is asserted mechanically, per fixture.

## Design decisions of record

- **Citations are stored per-Block only** (embedded copy authoritative, AD-5). The lesson-level
  "Citations" of FR-1 is satisfied by aggregation of per-Block citations — there is no duplicate
  lesson-level storage. The Student-facing "Sources" list is that aggregation.
- **Diagram SVG is stored inline in the script** (stakeholder-ratified 2026-07-18): this
  guarantees byte-exact review-gate integrity — what the Teacher approved is frozen in the
  Published Version, with no swappable asset path for diagrams. The 200 kB per-diagram budget
  is the size bound, enforced by pipeline validators (`budgets.json`), not by the schema.
- **"At least one Citation per Draft"** (FR-6) is a pipeline invariant, not a schema rule: the
  schema requires the `citations` array on every block but allows it to be empty.
- Asset size budgets (`transferSize` bounds, audio/model/SVG/poster caps) live in `budgets.json`
  (AD-11) and are enforced by pipeline validators and CI — never hardcoded in schema documents.
