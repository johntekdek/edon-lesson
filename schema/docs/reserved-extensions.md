# Reserved Extensions — Record Only

> These names are **recorded, not designed**. Do not define schemas, fields, fixtures, or
> renderer behaviour for them. They exist so future work lands as planned additive minors
> (or a planned major) instead of colliding with ad-hoc extensions. (AD-2; stakeholder
> amendments 2026-07-18.)

## Reserved for V2

- Dialogue block types: `teacher_turn`, `classmate_turn`
- AI Teacher persona/avatar treatment
- Scripted AI-classmate moments

## Reserved for V3

- Reactive live multi-agent behaviour
- Adaptive replanning / branching metadata
- Streaming delivery

Unknown-block-type tolerance (see [versioning.md](versioning.md)) is the mechanism that
makes these non-precluded by construction: a V2 dialogue block ships as a schema minor bump
plus a Player block-registry entry, and older players simply omit it.
