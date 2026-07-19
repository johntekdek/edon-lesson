# Reconciliation Review — UX Spines vs PRD + Addendum

Sources reconciled: `prd.md` (FR-1..FR-29, UJ-1..UJ-5, NFR-1..NFR-9, §12 OQ resolutions) and `addendum.md` §3, against `DESIGN.md` and `EXPERIENCE.md` (this folder). Date: 2026-07-16.

## Verdict

The spines are a faithful, disciplined carry of the PRD: every FR with a user-facing consequence is represented, all five UJs map to designed flows or a conscious exclusion (UJ-4 per A-2), all resolved OQ decisions with UX surface are honored, and every addendum §3 experience directive — humane quota copy, poster-fallbacks-as-designed-states, citation visibility, moderate-digital-literacy bounding — is present, most of them verbatim. No critical or high findings. Four medium findings need attention before sign-off: the FR-2 major-version "cannot play this lesson" Player state is missing; the diagram chat states conflate Rate Limit (temporal throttle) with the daily Quota, losing the PRD's Glossary distinction and FR-21's "when can I retry" message for the throttle case; and two borderline scope expansions (per-Block regeneration guidance input; a "mark reviewed" Structured Event not in FR-27's canonical taxonomy) must be confirmed or trimmed. Nine low findings are noted; several are already self-flagged by the spine's own Open Items list, which is exemplary scope-fence discipline.

## Coverage table

| PRD item | Spine location | Status |
|---|---|---|
| FR-1 (versioned contract, six Block types) | EXPERIENCE § Foundation, § Component Patterns (Slide/Narration/Quiz/Diagram/Model3D/Simulation rows); DESIGN § Components | Covered |
| FR-2 (forward compatibility) | Unknown-Block ignore needs no UX; **major-version "cannot play this lesson" Player state MISSING** | **PARTIAL [medium]** — see Dropped ideas D1 |
| FR-3 (shared validation) | EXPERIENCE § State Patterns "Generation failed", "Draft validation error after edit" | Covered |
| FR-4 (grounded generation request) | EXPERIENCE § Component Patterns "Generate form"; DESIGN "Generate form" (Course Context read-only chip) | Covered |
| FR-5 (schema-conforming pipeline) | § State Patterns "Generation failed" ("No partial Draft exists") | Covered |
| FR-6 (Citations stored/visible) | § Component Patterns "Citations panel" (per-Block, delete drops Citations), "Sources section" (Student, lesson-level) | Covered |
| FR-7 (idempotency, explicit Regeneration) | § State Patterns "Identical request while Draft exists"; Generate form rule; "Try again" on failure | Covered — lesson-level Regeneration affordance only referenced in banner copy, not specified as a component/state [low] (G5) |
| FR-8 (async generation + progress) | § Component Patterns "Generation progress card" (queued→generating→complete/failed per A-8); § State Patterns | Covered |
| FR-9 (faithful preview) | § Component Patterns "Preview overlay" (real Player, Low-spec view per A-27, Simulation interactive); § Capability Tiers "The Teacher sees what the Floor sees" | Covered |
| FR-10 (Block-level editing, A-28 map, discard) | "Block editor", "Block rail" (reorder w/ keyboard equivalent), "Regenerate control" (Diagram/Model3D/Simulation only), § State Patterns "Discard Draft" | Covered |
| FR-11 (explicit immutable publication) | "Publish dialog"; § State Patterns "Publish succeeded"; Flow 4 (v1 archived, still playable) | Covered |
| FR-12 (Review Gate enforcement) | § State Patterns "Lesson not available" (never Draft content) | Covered |
| FR-13 (render all Block types) | "Player shell" + six per-Block component rows | Covered |
| FR-14 (narration, swappable provider) | "Narration control" (transcript default when no voices, A-9); provider seam correctly left to architecture | Covered |
| FR-15 (quiz, server-authoritative) | "Quiz block" (instant client feedback; provisional "Saving your score…"; server authoritative); accepted-answer lists editable in "Block editor" (OQ-4) | Covered |
| FR-16 (Curated Model Library 3D) | "Model3D viewer" (orbit/zoom + button equivalents, annotations, attribution/licence line from asset metadata) | Covered |
| FR-17 (sandboxed Simulations + checks) | "Simulation frame" (postMessage lifecycle, runtime error → poster); "Publish dialog" checks; § State Patterns "Simulation check failed" (A-11 exits) | Covered |
| FR-18 (low-spec performance, poster fallback) | § Capability Tiers & Degradation Ladder; "Poster fallback card" (never error-styled); DESIGN player-ui note (no webfonts), § Elevation (no shadows) | Covered |
| FR-19 (grounded diagram requests in chat) | § Foundation #3; IA Student surfaces "Diagram message"; "Diagram chat message" component. Identity-stripping is server-side — correctly no UX surface | Covered |
| FR-20 (mandatory Sanitisation) | § State Patterns "Sanitisation/generation failure" ("Couldn't produce that diagram", never partial output) | Covered |
| FR-21 (diagram cache/Rate Limit/Quota) | § State Patterns "Diagram cache hit" (instant, exempt per OQ-2), "Rate Limit reached", "Tenant diagram quota/budget cache-only" | **PARTIAL [medium]** — Rate Limit vs Quota conflated; see Glossary GL1 |
| FR-22 (course placement, embedded playback) | § Moodle Embedding Contract (A-12 semantics); IA "Lesson picker" (Moodle-native, unbranded) | Covered |
| FR-23 (completion + gradebook writeback, OQ-15) | "Player shell" (completion definition), § State Patterns "Quiz submitted, score syncing" (retriable, A-13), "Attempts exhausted", "Completion reached", "Version pinning" (A-4); attempt limits in Lesson picker (self-flagged, Open Item 7) | Covered |
| FR-24 (Tenant-scoped auth, attribution) | No dedicated surface — backend; visible consequence (correct gradebook attribution) exercised in Flow 2 | Consciously excluded — acceptable |
| FR-25 (full Tenant isolation) | IA "Course home" scopes to own Drafts + Tenant's Published Versions only | Covered at UX level (rest is backend) |
| FR-26 (per-Tenant config) | § State Patterns "Budget Ceiling exhausted" (in-flight jobs finish, A-29), "Tenant diagram quota/budget cache-only", "Diagram feature flagged off"; Operator surface excluded per A-2 (§ Foundation) | **PARTIAL** — Simulation-Block flag-off UX undesigned [low] (G3); $2 soft-alert surface unrepresented [low] (G4) |
| FR-27 (Structured Events / Cost Telemetry) | Events referenced where user actions emit them (discard, report, mark-reviewed); no dashboard designed (NON-GOAL respected) | Covered where user-facing; mark-reviewed event is a taxonomy extension — see Scope S2 |
| FR-28 (diagram governance) | DESIGN/EXPERIENCE "AI content label" (verbatim string, never removable), "Diagram chat message" report control, IA "Diagram review queue", Flow 5; spot checks correctly given no Student surface | Covered |
| FR-29 (Moodle-initiated launch) | § Foundation #1; IA "Relaunch notice", "Authoring entry point"; § State Patterns "Expired/invalid Launch Token" (no login form, no retry) | Covered |
| UJ-1 | § Key Flows, Flow 1 (incl. off-target-discard edge via Discard Draft + Generate form) | Covered |
| UJ-2 | Flow 2 (incl. over-budget-asset edge via Constrained tier) | Covered |
| UJ-3 | Flow 3 (incl. limit edge; but see GL1 on Rate Limit vs Quota) | Covered |
| UJ-4 | Excluded per A-2 (§ Foundation, § Key Flows preamble); its Teacher/Student-facing consequences (budget pause, cache-only diagrams, replay unaffected) designed in State Patterns | Consciously excluded — acceptable |
| UJ-5 | Flow 4 (v-history line, A-4 pinning, no activity touch needed) | Covered |
| NFR-1 (gen < 5 min) | § State Patterns "Generation queued/running"; Voice & Tone ("Usually ready in under 5 minutes") | Covered |
| NFR-2 (playback low-spec) | § Capability Tiers; § Responsive & Platform "Performance as UX"; DESIGN player-ui (no webfonts), Elevation (no shadows) | Covered |
| NFR-3 (security) | User-facing outcomes only: Sanitisation failure state, sandboxed Simulation frame; remainder backend | Covered where UX-relevant |
| NFR-4 (reliability/durability) | Flow 4 ("v1 archived, still playable"); "Block regenerating" failure retains previous content | Covered |
| NFR-5 (observability) | Backend-only — no UX surface required | N/A — acceptable |
| NFR-6 (cost discipline) | Respected: spines add no per-Student inference; tap-to-load reduces spend | Covered (by absence) |
| NFR-7 (legal/licensing) | "Model3D viewer" attribution/licence line (FR-16 metadata) | Covered |
| NFR-8 (localisation-readiness) | § Voice and Tone (every string externalised with language key); DESIGN Typography (never bakes text into images) | Covered |
| NFR-9 (data protection) | Server-side (identity-stripping, pseudonymisation, retention) — no user-facing surface required | Consciously excluded — acceptable |
| OQ-1 (cost config) | Budget states covered; **$2 soft-alert surface unrepresented** — presumed Operator-side (A-2) but the exclusion is not stated | PARTIAL [low] (G4) |
| OQ-2 (diagram quota/rate limits) | Cache-hit exemption in "Diagram chat message"; 20/day copy in State Patterns | Covered — but see GL1 conflation and C1 hardcoded values |
| OQ-3 (Block-level Regeneration) | "Regenerate control" — Diagram/Model3D/Simulation only, never Slide/Quiz/Narration | Covered |
| OQ-4 (deterministic short-answer) | "Block editor" — accepted-answer lists editable | Covered |
| OQ-8 (data protection) | See NFR-9 | N/A — acceptable |
| OQ-9 (budget exhaustion) | "Budget Ceiling exhausted" (persistent gold banner, form disabled, in-flight finish, replay unaffected, never silent), "Tenant diagram quota/budget cache-only" | Covered |
| OQ-10 (citation display split) | "Citations panel" (Teacher, per-Block) vs "Sources section" (Student, lesson-level only) | Covered |
| OQ-11 (Moodle-initiated launch only) | § Foundation (no login, no course picker, never enumerates courses), Relaunch notice | Covered |
| OQ-12 (block_edon_ai minimal surface) | § Foundation #3 ("chat's own chrome untouched; this spine specifies only the diagram message") | Covered |
| OQ-13 (creator-owns model) | "Lesson card" (own Drafts private; duplicate others' Published Versions), "Tenant Admin on another's lesson" banner | Covered |
| OQ-14 (server-authoritative scoring) | "Quiz block" provisional score → server confirmation | Covered |
| OQ-15 (completion/attempt semantics) | "Player shell" completion rule; "Attempts exhausted"; highest attempt; "Version pinning" | Covered |
| OQ-16 (device floor) | § Capability Tiers (feature-detect, never user-agent); DESIGN Brand (low-bandwidth respect) | Covered |
| OQ-17 (diagram governance bundle) | Verbatim label, report → queue → Flow 5; spot checks correctly surface-free | Covered |
| OQ-7 (accessibility target — still open) | § Accessibility Floor: correctly flags as stakeholder-owned scope addition, recommends WCAG 2.1 AA, ships a floor regardless; Open Item 1 | Correctly deferred, not silently adopted |
| Addendum §3 — no prompt-engineering / moderate literacy | Generate form (two plain fields); Interaction Primitives (no icon-only primaries); DESIGN Do/Don't (no temperature/model pickers/token counts) | Covered |
| Addendum §3 — reported-diagram queue + label | Diagram review queue, AI content label (verbatim) | Covered |
| Addendum §3 — low-spec first-class, posters as designed states | § Capability Tiers ("designed states, not error states" — verbatim intent); DESIGN Do/Don't | Covered |
| Addendum §3 — chat rides block_edon_ai, humane quota copy | § Foundation #3; § Voice and Tone table (SM-C3-aware denial copy) | Covered |

## Scope expansions

- **S1 [medium] — Per-Block Regeneration guidance input.** EXPERIENCE "Regenerate control" opens a "What should change?" optional guidance field (and Flow 1 step 5 shows it used: "label R1 and R2 explicitly"). FR-10/OQ-3 commit Block-level Regeneration but say nothing about accepting steering text; this implies a new pipeline input (per-Block regeneration guidance) — backend scope the PRD does not require. Either confirm as a scope addition with the stakeholder or reduce the control to plain re-run (the PRD-minimal form). Not self-flagged by the spine.
- **S2 [medium] — "Mark reviewed" Structured Event outside the canonical taxonomy.** EXPERIENCE "Diagram review queue row": "'Mark reviewed' clears it from the queue and emits the Structured Event." A dequeue action is a fair minimal implication of FR-28's queue, but FR-27 states its event list "is the single canonical taxonomy — an event referenced anywhere in this PRD appears here," and no diagram-review-cleared event exists there. Needs a PRD taxonomy extension (stakeholder confirmation) or removal of the event claim. Note the spine *did* correctly flag the adjacent cache-eviction question (Open Item 2) rather than designing it — good fence discipline on the harder half.
- **S3 [low] — Tap-to-load on all tiers.** § Capability Tiers mandates poster-first + explicit load even on capable devices; the PRD requires the fallback path (FR-18) but not universal tap-to-load. Client-only, cost-friendly (I-1-aligned), and properly self-flagged (assumption tag + Open Item 5). Acceptable pending confirmation.
- **S4 [low] — Attempt limits configured in the Moodle Lesson picker.** FR-23/OQ-15 require Teacher-configurable attempt limits but not where; placement in mod_edonlesson settings is a design decision affecting the plugin's scope. Self-flagged (assumption tag + Open Item 7). Acceptable pending confirmation.
- **S5 [low] — Forced linear progression.** "Player shell": Next disabled until the current Block's minimum interaction is met (Quiz: submitted). Stricter than OQ-15's completion definition, which requires submission for *completion*, not for *advancing*. Client-only, no backend scope; note it prevents skip-and-return on quizzes — worth a conscious yes.
- **S6 [low] — Queue badge count and report-count chip.** Flow 5 / DESIGN queue row show an unread badge and per-diagram report counts — trivial aggregates within FR-28's queue capability. Borderline-fine; no action needed.
- Not expansions (checked and cleared): version-history line on the Lesson card (PRD Glossary: a Lesson *is* a version history); session-local "unseen" gold dot (explicitly never persisted); device-width/Low-spec preview toggles (A-27 vehicle); mid-lesson inline retry (in-session only — does not pre-empt the resume-after-disconnect architecture decision, FR-23/A-22); asset download size on load buttons (inherent metadata); new-tab launch (self-flagged, Open Item 8); phone-functional authoring (self-flagged, Open Item 6); light-mode-only and no-webfonts-in-Player (self-flagged, Open Items 3–4).

## Contradictions

- **C1 [low] — Hardcoded config values in Student-facing copy.** Voice & Tone / State Patterns bake "You've used today's 20 diagram requests" and "this month" into exemplar copy. 20/Student/day is a *tunable config default* (OQ-2), as is the budget period framing. If implemented literally, the copy contradicts tunability; the spine should state that quota numbers and periods in copy are templated from Tenant config. (The "this month" period itself matches A-29's calendar month — only the hardcoding is at issue.)
- No other contradictions found. Spot-checked and consistent: no-AI-label on lesson Diagram Blocks (they passed the Review Gate — matches FR-28's chat-only scope); cache hits exempt from Rate Limits (OQ-2); in-flight budget overrun (A-29); version pinning and latest-wins (A-4); regeneration never offered on Slide/Quiz/Narration (OQ-3/A-28); preview via the real Player (FR-9); publish blocked on Simulation check failure with Regenerate/delete exits (A-11); idempotent resubmission routing to the existing Draft (FR-7); replay never blocked on budget exhaustion (OQ-9).

## Dropped ideas

- **D1 [medium] — FR-2 major-version mismatch state.** The PRD defines a user-facing "cannot play this lesson" state for a major-version mismatch ("never silent corruption"). No spine state, component, or copy exists for it — State Patterns covers "Lesson not available" (FR-12) but not version incompatibility. Add a designed state (Player-side, poster-calm, Voice-and-Tone copy) or record a conscious exclusion with rationale.
- **D2 [low] — Block-type feature flag off (A-14/FR-26).** Only the Diagram flag has a designed state ("Diagram feature flagged off"). A-14 names Simulation Blocks as minimum flag granularity; the UX consequence (generation omits the type? existing Published Versions with the Block?) is undesigned. PRD leaves mechanism to architecture, so [low] — but the spine should either add the state or flag it as an open item.
- **D3 [low] — $2 soft-alert surface (OQ-1/FR-26).** Unrepresented in the spines. Almost certainly Operator-side telemetry (out of UX scope per A-2), but the exclusion is silent; record it as conscious.
- **D4 [low] — Lesson-level Regeneration affordance (FR-7/Glossary).** The idempotency banner copy says "Regenerate from here if you want a fresh one," but no component or Review Workspace affordance specifies whole-lesson Regeneration (which must bypass the idempotency cache). The intent is present; the specification is not.
- Everything else survived: humane quota copy (Voice & Tone, addendum §3 verbatim intent), poster-fallbacks-as-designed-states (verbatim), citation visibility (per-Block panel), narration-availability risk carried as a designed Floor-tier default (PRD §11 "known experience fact"), progress feedback with leave-safe copy, the FR-28 label string carried character-for-character.

## Glossary issues

- **GL1 [medium] — Rate Limit vs Quota conflated.** The PRD Glossary sharply separates **Rate Limit** (temporal throttle, actions per window) from **Quota** (countable cap; diagram default 20/Student/day is a Quota). EXPERIENCE's "Rate Limit reached" state carries Quota-exhaustion copy ("today's 20 diagram requests… more available tomorrow"), and no state exists for a true short-window throttle with FR-21's required "when you can retry" message. Rename the state and add the distinct throttle message (or consciously collapse the two with stakeholder sign-off, since both are PRD-mandated user messages).
- **GL2 [low] — "Diagram message" surface naming.** IA and components name the surface "Diagram message"/"Diagram chat message" without anchoring to the Glossary term **Diagram Request** (which appears only in FR citations and lowercase user copy). Cosmetic; one line tying the surface to the term would close it.
- Otherwise clean: Tenant, Teacher, Student, Draft, Published Version, Block, Generation Job, Launch Token, Review Gate, Course Context, Grounding Chunk, Curriculum Reference, Tenant Admin, Sanitisation (spelling consistent), mod_edonlesson, block_edon_ai are all used verbatim; the EXPERIENCE header declares Glossary discipline explicitly and largely delivers it.

## Finding counts

- Critical: 0
- High: 0
- Medium: 4 — D1 (FR-2 state missing), GL1 (Rate Limit/Quota conflation, = FR-21 partial), S1 (regeneration guidance input), S2 (mark-reviewed event vs FR-27 taxonomy)
- Low: 9 — S3, S4, S5, S6, C1, D2, D3, D4, GL2
