# Versioning & Compatibility Policy

The `schema` field is a `"MAJOR.MINOR"` string (e.g. `"1.0"`). It is validated by **pattern
only** (`^[0-9]+\.[0-9]+(?!\n)$`) — never by `const`/`enum` — so scripts stamped with future
versions still reach the semantics below instead of failing on the version literal. The
pattern uses ASCII `[0-9]` (never `\d`) and a `(?!\n)$` end guard so the ECMA (ajv) and
Python (`re`) regex engines classify identically — Python's `$` matches before a trailing
newline and its `\d` matches Unicode digits; ECMA's do neither.

## Minor versions — additive only

A minor bump may add: new optional fields (lesson-level or on existing block types) and new
block types. It may never remove fields, change types, or add new *required* fields to
existing structures.

Consumer behaviour on a same-major, higher-minor script:
- **Validators:** validate normally. Unknown block types pass via the base block envelope
  (`id`, `type`, `title`, `citations`); unknown fields on known structures are tolerated
  (block schemas never set `additionalProperties: false` — this is a design rule, not an
  accident).
- **Players:** unknown block types are omitted from the sequence and the "Block n of N"
  count entirely — no gap card, no error (FR-2). A script with zero renderable blocks
  renders the major-version can't-play state, never an empty Player.

**Quiz question types are a closed set within a major** (stakeholder-ruled 2026-07-19):
unlike block types, the quiz question `type` enum (`multipleChoice`, `shortAnswer`) is
deliberately closed — a v1.x minor may never add a question type. New interactive forms
ship as **new block types**, riding the block-level unknown-type fallback above, so older
players omit them gracefully instead of hard-failing inside a known quiz block.

## Major versions — breaking

A script whose major exceeds what the consumer supports yields the **defined can't-play
state** — never partial render, never silent corruption. The wrappers report this as the
distinct `unsupportedMajor` outcome, short-circuiting before schema validation (empty
`errors`).

The cannot-play state applies **only to scripts newer than the consumer**. Players never
drop renderer support for a shipped major: published lessons stay playable forever (I-3).

## Change process

Every schema change requires:
1. A version bump (minor for additive, major for breaking — expect never to need a major).
2. A dated migration/compatibility note in this directory recording what changed and how
   existing consumers behave.
3. New or updated fixtures in `fixtures/` covering the change, with `expectations.json`
   entries, passing both wrappers.

## Compatibility notes

| Version | Date | Note |
| --- | --- | --- |
| 1.0 | 2026-07-19 | Initial schema. Six block types (slide, narration, quiz, diagram, model3d, simulation). |
| 1.0 | 2026-07-19 | Pre-release hardening (review fix pass, stakeholder-approved; no bump — no published scripts exist): regex patterns rewritten for ECMA/Python engine parity (`[0-9]` classes, `(?!\n)$` end guards on `schema` and `language`); `assetRef.ref` tightened to `^asset://.+` (empty asset id no longer validates); wrappers' referential layer now also enforces uniqueness of block ids, question ids (per quiz block), and option ids (per question). |
