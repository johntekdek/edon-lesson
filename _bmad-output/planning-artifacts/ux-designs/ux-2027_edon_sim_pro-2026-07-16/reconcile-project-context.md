# Reconciliation Review — UX Spines vs `project-context.md`

**Reviewed:** `DESIGN.md`, `EXPERIENCE.md` (ux-2027_edon_sim_pro-2026-07-16) against `_bmad-output/project-context.md` (authoritative; [HARD] rules win).
**Date:** 2026-07-16

## Verdict

The spines are compliant with every [HARD] rule in `project-context.md` — no critical findings. Both documents actively reinforce the two economic/quality invariants (generate-once, review gate) rather than merely avoiding them, and they are unusually disciplined about deferring ADR territory (component library explicitly disclaimed, bundle budget explicitly "architecture-set", backend stage labels explicitly optional). One high-severity gap exists against §6 architecture principles: the schema-first requirement that "players ignore unknown block types gracefully" has no UX specification, and it collides with the Player's completion rules. One medium finding (an undefined "device budget" concept) and six low findings round out the review. Nothing requires redesign; the high and medium items need spine amendments before architecture consumes these documents.

## [HARD] rule compliance

- **Generate-once economics — COMPLIANT.** No Player or chat affordance implies per-student-per-session LLM inference beyond Diagram Requests. Narration is client-side SpeechSynthesis (zero marginal cost); quiz "instant client-side feedback" is deterministic (option keys / accepted-answer lists), and server re-scoring is validation, not inference; regeneration and "Try again" are teacher-explicit only, matching §3 "regeneration is always an explicit user action"; FR-7 idempotency routing (identical request → existing Draft) and the cache-hit diagram flow (Flow 3, "don't count against the Rate Limit") actively reinforce the invariant. No finding.
- **Review gate — COMPLIANT.** The gold/green provenance system exists to make the gate legible (DESIGN § Brand & Style). Students never see Drafts ("Lesson not available" state, FR-12); the Preview overlay exposes Drafts only to the Teacher inside the Authoring UI; chat diagrams — the sanctioned exception — always carry the verbatim, non-dismissible FR-28 label; sanitisation failure "never partial or raw output". The reviewed lesson Diagram block correctly drops the AI label ("passed the Review Gate"). No finding.
- **No TypeScript — COMPLIANT.** EXPERIENCE § Foundation states "React (JSX, no TypeScript — `project-context.md` §2 [HARD])" verbatim. No finding.
- **Self-contained embeddable Player — COMPLIANT.** Foundation item 2 ("script + mount API, no host framework") and the entire Moodle Embedding Contract (container-native, no viewport ownership, namespaced classes, no global resets, self-managed height) match §2. No Next.js host assumption anywhere. No finding.
- **SVG sanitisation — COMPLIANT.** Every diagram rendering path (Diagram block, diagram chat message, review queue thumbnail) is specified as "sanitised SVG"; the failure state rejects rather than passes through. No finding.
- **Simulation sandboxing — COMPLIANT, one edge unspecified.** Simulation frame is a sandboxed iframe; parameter controls live inside it; lifecycle "via the postMessage protocol" — consistent with §4.
  - **[low]** EXPERIENCE says "any runtime error inside the sandbox collapses the frame to the Poster fallback card", but with a strict-CSP sandbox whose only channel is postMessage, a hard-crashed or hung simulation emits nothing. The spine should state the experience requirement (e.g., "a simulation that does not signal readiness within a bounded time renders the poster fallback") without dictating the detection mechanism.
- **Tenant isolation — COMPLIANT.** Course home scopes to "the Teacher's own Drafts + the Tenant's Published Versions"; the diagram review queue is "Tenant-scoped"; the Flow 3 cache hit is between classmates at the same college (consistent with §3 tenant-scoped diagram cache); duplication (OQ-13) operates on Tenant Published Versions only; no login screen or course picker exists to leak across tenants. No UX surface implies cross-tenant visibility. No finding.
- **No wildcard CORS — NOT TOUCHED.** No spine statement addresses origins; the Moodle-embedded Player is compatible with per-tenant allowed-origin configuration. No finding.

## Consistency with tech standards

- **Three.js / glTF / Draco, per-block budgets, poster fallback (§2) — largely consistent.** Poster-first, tap-to-load-with-size, and "degraded states are designed states" language strengthens the §2 poster-fallback standard; the Full tier keys on "asset within its per-Block budget", matching §2.
  - **[medium]** The Constrained tier is defined by "asset over **device budget** or load fails" (EXPERIENCE § Capability Tiers). `project-context.md` §2 defines only **per-block size budgets** (an authoring/build-time constraint); "device budget" is a new runtime concept the spine neither defines nor sources, and it quietly implies a per-device asset-budget mechanism that architecture would have to invent. Rephrase as an experience requirement ("asset too heavy for the detected device class, or load fails") or explicitly hand the definition to architecture.
- **Schema-first (§6): unknown block types — GAP.**
  - **[high]** §6 requires "players ignore unknown block types gracefully" and reserves the player block registry seam (§6 extension points), so a shipped Player meeting a block type it doesn't know is an anticipated, first-class scenario — yet neither spine specifies what the Student sees. Worse, the gap interacts with two Player-shell rules: "Next is disabled until the current Block's minimum interaction is met" and "Completion = all Blocks viewed". An unknown block with no defined rendered/viewed state could strand a Student short of 100% completion, indirectly violating the FR-18 spirit that every tier can complete. The spine needs an "Unknown block" entry in Component Patterns/State Patterns (e.g., render nothing or a neutral skip card, count as viewed, never block Next, never styled as an error) — the visual answer likely reuses the poster-fallback/first-class-content posture already established.
- **Async generation with progress (§6) — CONSISTENT.** Queued → generating → complete/failed states, elapsed time, "you can close this — we'll keep working", failure with readable reason and explicit retry all match "queued jobs with progress reporting; the API never blocks". "Shows finer stage labels only if the backend provides them" correctly avoids over-promising queue internals. No finding.
- **Immutable publications (§6) — CONSISTENT.** Publish dialog produces an "explicit immutable publication"; Flow 4 shows "v2 current · v1 archived, still playable" (matches "published lessons remain playable forever"); version pinning (in-flight sessions keep their version, A-4) is coherent with immutability. No finding.

## Architecture-boundary violations

No ADR-reserved decision is made by the spines. Checked and clean: no UI component library is mandated (explicitly disclaimed as "ADR territory" — React itself is set by §2, so naming React is legitimate); queue mechanics are not dictated (states only, backend-provided stage labels optional); no schema fields are invented (the "unseen" dot is explicitly session-local and never persisted; attribution rendering cites the §5-mandated asset metadata rather than inventing it); the Player bundle budget is deferred as "architecture-set, CI-enforced"; the Operator surface is left to architecture per PRD A-2. DESIGN's "Don't: expose prompt-engineering affordances (temperature, model pickers, token counts)" actively protects the §3 adapter/config-only policy. Two minor encroachments:

- **[low]** EXPERIENCE § Responsive & Platform prescribes the mechanism "measured via JS, not CSS container queries". The UX-owned fact is the constraint (must behave correctly on Android 8-era WebViews that lack container-query support); how container width is obtained is an implementation choice. Restate as a constraint, not a technique.
- **[low]** The Capability Tiers table names SpeechSynthesis as the narration mechanism. This is PRD-sourced (A-9) and the surrounding pattern (explicit play/pause + always-available transcript) is provider-agnostic, so the §6 narration-provider seam is not foreclosed — but keep future edits mechanism-neutral so the seam stays open. Informational; no change strictly required.

## Other findings

- **[low]** The Accessibility Floor requires "sliders adjustable by arrow keys", which for Simulation blocks constrains controls rendered *inside* the sandboxed iframe — i.e., AI-generated simulation code the Player cannot retrofit. The requirement is right, but the spine should route it to the generation prompt contract and the FR-17/A-35 pre-publish simulation checks, not leave it implied as a Player guarantee.
- **[low]** "Instant client-side feedback per question — no server round-trip" implies correct answers and accepted-answer lists ship inside the delivered lesson script, readable by a motivated Student. Server-authoritative re-scoring (A-13) protects the gradebook, so this is acceptable, but architecture should inherit it as an explicit, eyes-open trade-off rather than discover it.
- **[low]** DESIGN loads Inter and Plus Jakarta Sans in the Authoring UI (correctly excluded from the Player bundle). Both are SIL OFL — compatible with §5's permissive-licence rule — but their licences should be recorded when the dependency is added, per §5's expectations. No blocker.

## Summary counts

| Severity | Count |
|---|---|
| critical | 0 |
| high | 1 |
| medium | 1 |
| low | 6 |
