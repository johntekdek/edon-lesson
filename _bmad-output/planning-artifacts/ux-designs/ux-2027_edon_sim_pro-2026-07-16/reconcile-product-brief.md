# Reconciliation Review — Product Brief vs UX Spines

**Source reconciled:** `_bmad-output/planning-artifacts/edon-lesson-studio-product-brief.md`
**Artifacts checked:** `DESIGN.md`, `EXPERIENCE.md` (this folder)
**Precedence context:** PRD `prd-2027_edon_sim_pro-2026-07-07/prd.md` supersedes the brief where they differ; brief consulted for user descriptions, product goals, §7 fences, and experience texture.
**Date:** 2026-07-16

## Verdict

**PASS — no critical or high findings.** The spines respect all ten out-of-scope fences (brief §7 + PRD FR-29) and honor every §3 user characterization; several fences are honored exemplarily (no login surface anywhere including the token-expiry dead end; low-spec-first degradation designed as content, not error; the diagram queue kept strictly to FR-28 governance rather than drifting toward an analytics surface; genuine scope-adjacent decisions consistently tagged `[ASSUMPTION]` and batched as Open Items instead of silently designed in). Three medium findings need attention before architecture: an ambiguity in poster-image provenance that could be misread as the banned AI image generation, a missing affordance for whole-Lesson explicit Regeneration that the spine's own copy references, and an IA inconsistency between the course-scoped Course home and Flow 4's cross-course duplication path. Nine low findings are copy-precision, missing minor states, and properly-flagged assumptions to keep in the confirmation batch. Nothing contradicts the brief's economics or quality invariants; no per-student-per-session inference appears anywhere in the designed experience.

## Out-of-scope fence check

Fence-by-fence result:

| Fence (brief §7 / PRD §8) | Result |
|---|---|
| Neural/server-side TTS UI | Clean — narration is SpeechSynthesis-only with transcript-first degradation (A-9); no voice pickers, no audio-generation UI |
| Multi-agent classroom UI | Clean — no AI persona, classmates, live Q&A, or adaptive-sequencing surface |
| Student-triggered simulation generation | Clean — students only "Run simulation" on teacher-published, review-gated code |
| Cross-tenant sharing/library | Clean — Lesson card visibility and "Duplicate as my draft" are strictly Tenant-internal per OQ-13 |
| Analytics dashboard UI | Clean — no dashboard; Diagram review queue is the FR-28 governance loop, not reporting |
| Offline/SCORM UI | Clean — absent |
| LTI / non-Moodle LMS | Clean — Moodle-only embedding contract |
| AI illustrative image generation | Ambiguity — see finding 1 |
| Text-to-3D | Clean — Model3D from the Curated Model Library only; annotations editable, geometry never generated |
| Standalone login (PRD FR-29) | Clean, exemplary — Launch-Token-only IA; Relaunch notice is a dead end with "no login form, no retry button" |

Findings:

1. **[medium] Poster provenance is ambiguous against the no-AI-image-generation fence.** EXPERIENCE (Degradation Ladder, last bullet) states "Posters are authored outputs of generation, reviewed at the Review Gate." Brief §7 bans AI illustrative image generation and PRD §8 restates it ("diagrams are SVG only"). "Outputs of generation" can be read as the pipeline producing raster poster images via an image model. The intended reading is almost certainly derived imagery (curated-asset thumbnails, simulation captures, or SVG), but as written the spine hands architecture a sentence that licenses a banned capability. Fix: one clause stating posters are derived/selected assets, never LLM/image-model-generated raster output.
2. **[low] "Unfetched Block" wording brushes the reserved streaming-delivery capability.** EXPERIENCE State Patterns ("Mid-lesson connectivity loss… moving to an unfetched Block shows an inline retry") implies Block *content* is fetched incrementally. Brief §6 reserves streaming delivery of blocks for V3 and §10(b) fixes today's posture as "returns a complete published script." The natural implementation (full script up front, lazy heavy assets) satisfies both; the state should say "a Block whose assets haven't loaded" to avoid architecture inferring incremental script delivery.

Also verified at fence level: the I-1 economics invariant survives the experience design — the only student-side LLM touchpoint is the Diagram Request, cache hits are rate-limit-exempt and rendered identically, and quiz feedback is explicitly client-side with deterministic server re-score (no LLM judging, OQ-4).

## User-posture check

Brief §3 characterizations against the experience decisions:

- **Teachers: no prompt-engineering skill.** Honored, exemplary. Generate form is two plain fields (Topic + optional Guidance) with Course Context as a read-only chip; DESIGN's Don't column bans "prompt-engineering affordances (temperature, model pickers, token counts)"; Block regeneration guidance is a plain "What should change?" field.
- **Teachers: moderate digital literacy.** Honored. No icon-only primary actions (stated as a rule with the literacy rationale), labeled buttons everywhere, confirmation only on destructive actions, overlays never stack, error copy in Voice-and-Tone table is human-readable ("we couldn't find enough course material on this topic") rather than technical.
- **Teachers: time-poor.** Honored. Async generation with leave-safe copy, the gold/green split built expressly so a reviewer "can see at a glance what still needs their eyes," session-local unseen dots as a navigation aid, block-scoped regeneration that keeps the rest of the Draft editable, preview that returns without losing editor state.
- **Students: low-spec Android hardware.** Honored, exemplary. Capability-tier ladder with degraded states as designed states; no webfonts/shadows/component library in the Player; text-before-assets; tap-to-load with download sizes shown (metered-data respect); tap-only gestures, ≥48px targets, no swipe; feature detection never user-agent; Floor tier reaches 100% completion; Teacher previews exactly what the Floor sees (A-27).
- **Admins: evidence, not dashboards.** Honored. No reporting surface designed; UX-visible actions (discard, mark-reviewed, report) explicitly emit Structured Events, keeping the future-reporting substrate intact per brief §3.3/FR-F.24.

Findings:

3. **[low] "Usually ready in under 5 minutes" hardens a median target into a copy promise.** SM-1 is a *median*; the approved p90 is 2× that (A-34) — a meaningful share of jobs will exceed the promise, eroding trust with exactly the time-poor audience the copy serves. Suggest softening ("typically a few minutes") or driving the estimate from observed tenant timings.
4. **[low] Quota copy hardcodes "20 diagram requests."** The 20/Student/day figure is a tunable per-Tenant config default (OQ-2/FR-26). The Voice-and-Tone exemplar is fine as an example, but the spine should state the number is interpolated from Tenant config (the NFR-8 externalised-strings rule makes this cheap) so the copy never lies at a Tenant with a different quota.
5. **[low] Next-gating on quiz submission interacts with attempt limits.** EXPERIENCE disables Next until "Quiz: submitted." Combined with Teacher-configurable attempt limits (OQ-15), a Student who wants to read ahead before answering is forced to spend a submission. Clarify whether an in-lesson submission consumes an attempt or attempts are per lesson run — the student posture (low confidence, formative stakes per A-21) argues for not punishing read-ahead.

## Dropped ideas

6. **[medium] Whole-Lesson explicit Regeneration has no designed affordance — and the spine's own copy references one.** Brief FR-A.4 and PRD FR-7 make lesson-level Regeneration an explicit Teacher action that "always re-runs the pipeline, bypassing the idempotency cache"; UJ-1's edge case is discard → refine guidance → regenerate. The spine's Regenerate control is explicitly restricted to Diagram/Model3D/Simulation Blocks, and no other surface offers lesson-level regeneration — yet the idempotency Notice copy says "Regenerate from here if you want a fresh one," pointing at an affordance that does not exist. Either design the path explicitly (e.g., discard-then-resubmit as the sanctioned route, or a lesson-level Regenerate action in the Review Workspace) or correct the copy; as written, downstream will invent it.
7. **[low] Teacher "monitor results" (brief §3.1) has no in-product surface.** This is arguably correct — Flow 2 lands the score "in the gradebook his lecturer already uses," and the no-dashboard fence forbids more — but the spine never states the delegation. One sentence ("Teachers monitor results in the Moodle gradebook; no in-product results surface in MVP") turns an omission into a decision.
8. **[low] Simulation-Block feature flag has no designed off-state.** PRD A-14/FR-26 commits flag granularity covering at least the Diagram feature *and* Simulation Blocks. The spine designs "Diagram feature flagged off" but no equivalent for Simulations — what generation produces, and what a Published Version containing a Simulation Block renders, when the flag is off for a Tenant. The poster path plausibly covers playback, but it should be said.
9. **[low] Curriculum Reference provenance is unshown.** DESIGN's Lesson card displays "course + curriculum reference," and the brief §6 schema carries it, but the Generate form collects only Topic + Guidance and no surface shows where the Curriculum Reference comes from or whether the Teacher can correct it during review. Likely pipeline-derived; note it so architecture owns it consciously.

Otherwise the brief's qualitative texture survives intact: preview "exactly as students will see it" (same Player, FR-9), block deletion/reordering, citations visible in review with per-Block panels and a Student-side Sources section (OQ-10), diagram-in-the-chat-they-already-use, poster fallback per block, budget/quota exhaustion as honest institutional copy, licence attribution on 3D assets, and localisation-ready externalised strings.

## Contradictions / expansions

10. **[medium] Course-scoped Course home vs Flow 4's cross-course duplication.** The IA defines Course home as "Lessons for the launch course," but Flow 4's failure path has a colleague duplicating Dr. Amina's Published Version "for another course" — undiscoverable from a home scoped to the colleague's own launch course. Both readings are PRD-legal (OQ-13 permits Tenant-wide duplication; cross-*tenant* stays untouched either way), but the spine currently asserts both. Decide: Course home lists the launch course's lessons only (and Flow 4's path needs a discovery mechanism), or it lists Tenant-wide Published Versions (and the IA row needs rewording).
11. **[low] Universal tap-to-load is a real expansion beyond FR-18 — correctly quarantined.** The PRD requires the fallback path but not tap-to-load on capable devices; the spine's choice is well-argued (metered data, universal exercise of the poster path), tagged `[ASSUMPTION]`, and batched as Open Item 5. Keep it in the confirmation batch; do not let it slide into architecture unconfirmed.
12. **[low] WCAG 2.1 AA is recommended, not adopted — correct handling of OQ-7.** The spine's pragmatic floor stands regardless and formal adoption is flagged as a scope addition needing confirmation, exactly as the PRD requires. Observation, no action beyond the batch.
13. **[low] Gold on the Low-spec view toggle stretches DESIGN's own gold rule.** DESIGN reserves gold "exclusively for AI output awaiting your judgment," then uses gold-wash for the Preview overlay's Low-spec toggle-on state — a device-simulation control, not AI provenance. Minor internal-consistency leak in the system's one big idea; use the standard selected/active green treatment instead.
14. **[low] Assumption-flagged placement decisions are consistent with the brief but need the batch.** Attempt limits configured in the Moodle Lesson picker (Open Item 7) and new-tab launch (Open Item 8) are both reasonable, both flagged, neither PRD-specified. No spine change needed; confirm in the batch.

No contradiction was found with the brief's two load-bearing principles (generate-once economics; teacher review gate), with the PRD's four invariants, or with the greenfield/external-systems boundary. No §7 item is designed in as a feature; the two medium fence-adjacent items (1, 6) are wording/omission risks, not designs.

---
**Totals:** 0 critical · 0 high · 3 medium (findings 1, 6, 10) · 9 low.
