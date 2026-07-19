# ADR-014: Player Composition Interfaces (V3 Seams a/b/c/e)

**Status:** Proposed (pending stakeholder sign-off, architecture run 2026-07-17)

## Context
Brief §12.3 requires ADR rationale for the §10 extension points. AD-10 fixes the Player's composition invariants; this ADR records the decisions and their reasoning. The Player is the component most exposed to V3 (dialogue blocks, streaming, TTS, SCORM), so its seams must be interfaces the MVP itself exercises — a seam only V3 would use is a seam nobody notices breaking.

## Decision
Four interfaces, all consumed by the MVP's own single implementation of each:

1. **`BlockRegistry`** (seam a): `register(type, rendererModule)`; the shell resolves renderers only through it. Unknown types are omitted from the sequence and the "Block n of N" count (FR-2). Heavy renderers register a lazy loader, which is how the chunk split (AD-11) falls out naturally. V3 dialogue-turn blocks = schema minor bump + one registry entry.
2. **`LessonDeliverySource`** (seam b): `getMeta()` + `blocks()` returning an async iterator that MVP's `CompleteScriptSource` fulfils from one fetched, complete Published Version. The shell renders as blocks arrive from the iterator — trivially instant today, incremental tomorrow. The V3 streaming source is a new implementation (SSE/WebSocket) chosen at mount; **backend-side the streaming variant is an additive new endpoint**, not a change to the complete-script endpoint.
3. **`NarrationProvider`** (seam c): `available() / speak(text, lang) / stop() / events`; MVP registers `SpeechSynthesisProvider` including the bounded-start watchdog (3 s) and voice-selection chain (en-NG → en-GB → any en); the Floor transcript rung is the provider reporting unavailability, not an error path. Neural/streaming TTS = new provider + optional schema minor bump for audio refs.
4. **`ResultsSink`** (seam e, completing it): the Player emits view marks, quiz submissions, and completion **only** through `ResultsSink`; MVP registers `PlatformResultsSink` (playback API + localStorage outbox + sendBeacon per AD-15). A SCORM/offline package swaps in an RTE-backed sink (SCORM grade/completion reporting) with the same at-most-once semantics — without this sink abstraction, seam (e) would be static assets with a dead results path.

## Consequences
- Every interface has exactly one MVP implementation — the abstraction cost is four small modules, and each is exercised on every lesson play (no rot).
- The canonical mount signature is `EdonPlayer.mount(el, {scriptUrl, token, locale})` (AD-22); `source`/`sink`/`narration` are **optional overrides** on the same options object, defaulting to the platform implementations — the Moodle embed passes nothing special, and runtime state (resume, flags, attempt ids) always arrives via the bootstrap endpoint, never via mount options.
- The preview overlay reuses the same composition with a Draft-backed source and a no-op sink — preview writes nothing (FR-9 fidelity with zero risk of preview results reaching the gradebook).
