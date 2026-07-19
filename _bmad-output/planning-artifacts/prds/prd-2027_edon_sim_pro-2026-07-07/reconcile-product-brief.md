# Reconciliation Report — PRD vs. Product Brief

**Input source:** `_bmad-output/planning-artifacts/edon-lesson-studio-product-brief.md` (authoritative scope contract)
**Targets:** `prd.md` and `addendum.md` in this directory
**Also consulted:** `_bmad-output/project-context.md` (stakeholder seed; the PRD/addendum delegate build rules to it — delegation targets were verified against its actual contents)
**Date:** 2026-07-07

---

## Verdict

The PRD is a high-fidelity derivation of the brief. All 24 brief §5 functional requirements map 1:1 onto PRD FR-4–FR-27 with correct citations; §6 schema rules are FR-1–FR-3; all nine §7 out-of-scope items are carried verbatim into PRD §8 with no promotion into MVP; all five §4 metrics are carried as SM-1–SM-5; all §11 risks/assumptions are carried in PRD §11 and NFR-8. The three items the brief §12.2 forbids de-scoping (review gate, schema-first design, tenant isolation) are not merely present but elevated to load-bearing invariants (I-2, I-3, I-4). The assumption-tagging discipline is strong: nearly every inference is tagged and indexed (A-1–A-16) with matching open questions.

The findings below are real but modest: one medium-severity semantic distortion (sanitisation strip vs. reject), a handful of low-severity unflagged additions/strengthenings, and small qualitative drops. **No critical or high-severity issues found.**

---

## 1. GAPS — brief content not captured in prd.md or addendum.md

### GAP-1 — Schema *documentation* as part of the first-class package
- **Brief location:** §6, final bullet: "The schema, its validators, **and its documentation** live in the new repository as a first-class package consumed by both backend and player."
- **What's missing:** PRD FR-3 and §9.1 carry the validators and the shared-package requirement, but the schema's documentation as a package deliverable is dropped. (FR-2 requires a "documented compatibility note" for *changes*, which is narrower; `project-context.md` §8 defines `/docs` for ADRs/runbooks, not schema docs.)
- **Severity:** Low.
- **Suggested placement:** Add to FR-3 (e.g., a consequence: "the schema package ships with documentation sufficient for a renderer author to implement each Block type") or to §9.1's schema bullet.

### GAP-2 — "Moderate digital literacy" user attribute
- **Brief location:** §3.1: Lecturers have "moderate digital literacy, time-poor… The authoring UX must assume no prompt-engineering skill."
- **What's missing:** The PRD (§2.1) and addendum (§3) carry "no prompt-engineering skill" and "time-poor" faithfully, but the broader "moderate digital literacy" constraint — which bounds *all* authoring UX complexity, not just prompting — is silently dropped. A UX workflow reading only the PRD could ship a review/edit surface that assumes power-user fluency while technically satisfying "plain fields."
- **Severity:** Low.
- **Suggested placement:** PRD §2.1 Teacher JTBD preamble and addendum §3 first bullet.

### GAP-3 — Architect's duty to extend `project-context.md` after architecture
- **Brief location:** §12.3: "Generate `project-context.md` at the end of architecture, including the team standards and the clean-room constraint from §9 verbatim."
- **What's missing:** The addendum §1 ADR agenda (which otherwise carries §12.3 completely) omits this instruction. Mitigation already in place: `project-context.md` exists as a stakeholder seed and its own status line instructs the Architect to extend it without weakening [HARD] rules — so the practical risk is near zero, but the handover chain in the PRD run's own artifacts has a dangling link.
- **Severity:** Low.
- **Suggested placement:** One line in addendum §1 ("At the end of architecture, extend `project-context.md` with ADR decisions; never weaken [HARD] rules").

### GAP-4 — Minor factual detail drops (informational)
- Brief §8.1: edon-rag "hosted on a VPS" — dropped from addendum §1's edon-rag line. Immaterial; the stack details that matter (FastAPI, pgvector, Ollama, per-tenant keys) are carried.
- Brief §1 header metadata (planning level, codename): codename is carried via repo plan; planning level is process metadata not needed in the PRD.
- **Severity:** Low (informational). No action strictly required.

### Verified delegations (checked, NOT gaps)
These brief items are absent from prd.md/addendum.md but the delegation target was verified to contain them, and the PRD/addendum explicitly declare `project-context.md` authoritative for build rules:
- No TypeScript; JS/JSX; embeddable bundle → `project-context.md` §2 ✓
- PostgreSQL; object storage with tenant-scoped paths → §2 ✓
- Deployment (VPS/nginx/systemd/Let's Encrypt; single-VPS start, worker horizontal-scaling path) → §2 ✓
- Committed `.env.example`; API key rotation; no wildcard CORS → §4 ✓
- Clean-room constraint verbatim incl. "must not fetch, quote, or reference OpenMAIC source" → §5 ✓
- Draco compression example → §2 ✓

---

## 2. DISTORTIONS — materially different statements

### DIST-1 — Sanitisation: brief specifies *stripping*; PRD consequence specifies *whole-SVG rejection* (MEDIUM)
- **Brief §5.17:** "All generated SVG passes a mandatory sanitisation pass (**script/foreignObject/event-handler stripping**, allowlist-based) before rendering." `project-context.md` §4 [HARD] matches: strip the offending constructs; *failures* (only) are rejected.
- **PRD FR-20 consequence:** "An SVG **containing** a script, event handler, `foreignObject`, or external reference **never reaches storage or a rendering surface**."
- **Why it's material:** Under strip semantics, an SVG that arrived with an event handler is cleaned and the safe remainder renders — the student still gets a diagram. Read as a test, the PRD consequence rejects the entire SVG the moment any disallowed construct is present. LLM-generated SVG frequently contains benign-but-disallowed constructs; blanket rejection would measurably raise diagram denial/failure rates (directly pressuring SM-5 and counter-metric SM-C3) and is a stronger requirement than either source, with no `[ASSUMPTION]` tag.
- **Fix:** Reword the consequence to strip semantics, e.g. "No SVG reaching storage or a rendering surface contains a script, event handler, `foreignObject`, or external reference; inputs containing them are sanitised by stripping, and outputs that cannot be made conforming are rejected."

### DIST-2 — Offline/SCORM non-goal carries invented sentiment and a promotion nudge (LOW)
- **Brief §7:** offline/SCORM export is out of scope, "designed-for but not built… cheap to add as a fast-follow." Brief §12.2: "do not pull §7 items into MVP" without explicit stakeholder confirmation.
- **PRD §8:** adds "`[NOTE FOR PM]` **Emotionally load-bearing** for low-bandwidth institutions; **revisit early if timeline permits**."
- **Why it's material:** "Emotionally load-bearing" is an invented stakeholder-sentiment claim with no basis in the brief, and "revisit early if timeline permits" softly invites exactly the promotion §12.2 forbids. It stops short of promoting, but the editorial posture differs from the brief's.
- **Fix:** Replace with the brief's own framing: "fast-follow; schema and static-asset discipline must keep it cheap to add" — or tag the note as PM commentary.

### DIST-3 — Vision promises "minutes of review"; brief promises minutes of *production* (LOW)
- **Brief §2:** "…lessons **in minutes rather than weeks**" (production time); §4 sets <5 min to *ready for review*; review duration is uncommitted.
- **PRD §1:** "collapses weeks of content production into **minutes of review**."
- **Why it's material (mildly):** It sets an expectation of near-trivial review effort that the brief never makes — and the PRD's own counter-metric SM-C1 explicitly warns that review time trending toward zero signals a rubber-stamped Review Gate. The vision sentence and SM-C1 pull in opposite directions.
- **Fix:** "collapses weeks of content production into minutes of generation plus a focused review."

### Checked and cleared (not distortions)
- FR-20 "failures reject the output; nothing passes through raw" — matches `project-context.md` §4 [HARD] (sourced, correctly cited).
- FR-17 "communication only via a defined message protocol" — matches `project-context.md` §4 [HARD] postMessage rule (sourced).
- NFR-3 "allowed origins are per-Tenant configuration" and "issue/revoke without downtime" — both match `project-context.md` §4 (sourced).
- Addendum ADR-002 (model benchmark, "do not default to GPT-4o"), the GPU-spend migration trigger, mini/small-tier diagram model, "CPU-only VPS is never a generation host" — none are in the brief, but all are verbatim from `project-context.md` §3, and the addendum attributes them there. One looseness: the addendum's cost-economics block cites "brief §1/§11 + project-context §3" jointly; the specifics come *only* from project-context §3. Cosmetic — consider splitting the citation.
- FR-7 idempotency-returns-existing-Draft, FR-15 deterministic scoring/no LLM judging, FR-11 latest-wins versioning, FR-23 retriable writeback, budget-exhaustion semantics — all are inferences beyond the brief's letter, and all are properly `[ASSUMPTION]`-tagged with OQ backlinks. This is the tagging discipline working as intended.

---

## 3. SCOPE LEAKS

### 3a. §7 items promoted into MVP — NONE
All nine §7 items (server-side/neural TTS; multi-agent classroom features; student-triggered simulation generation; cross-tenant sharing/library; analytics dashboard UI; offline/SCORM export; LTI 1.3; AI illustrative image generation; text-to-3D) appear in PRD §8 as non-goals and nowhere in §9.1 In Scope. PRD §9.2 additionally re-states the no-promotion rule. Clean.

### 3b. Brief-mandated items de-scoped or watered down — NONE
- **Review gate:** intact and strengthened (I-2, Feature 4.3, FR-12; Simulation checks gate publish per FR-17).
- **Schema-first design:** intact and strengthened (I-3, Feature 4.1 as keystone, FR-1–FR-3, first bullet of §9.1). (See GAP-1 for the one dropped sub-item: documentation.)
- **Tenant isolation:** intact and strengthened (I-4, FR-25, NFR-3; woven through FR-4, FR-19, FR-21, FR-24).
- Block-level regeneration correctly carried as "desirable, uncommitted" (FR-10 + OQ-3) — matches the brief exactly, neither promoted nor dropped.

### 3c. Unflagged MVP additions beyond the brief (all LOW)
- **LEAK-1 — Counter-metrics SM-C1–SM-C3 (PRD §10).** Review-time floor, block-type richness, diagram denial rate — none exist in brief §4. They are sensible guardrails, but they establish evaluation targets downstream workflows will treat as binding, and only SM-C1's *derivability* is tagged (A-16), not the counter-metric set itself. **Fix:** tag the "Counter-metrics" subsection as a PM addition requiring stakeholder confirmation, or add an OQ.
- **LEAK-2 — FR-26 consequence: feature flags togglable "without redeploying."** Brief §5.23 says only "feature flags." Runtime toggling is an implementation-strength requirement added untagged (A-14 covers flag granularity, not this). **Fix:** tag or soften.
- **LEAK-3 — PRD §2.2 Non-Users.** "No self-serve sign-up," exclusion of independent teachers and the general public are reasonable inferences from the brief's context (~60 institutions, Moodle-mediated access) but are stated as fact without a tag. **Fix:** one `[ASSUMPTION]` on the section.
- (Properly handled, not leaks: OQ-7 accessibility and OQ-8 NDPR are framed as *potential* scope additions requiring explicit confirmation rather than smuggled in — correct per brief §12.2.)

---

## 4. FR SOURCE-CITE VERIFICATION

Brief §5 numbering runs 1–24 continuously across FR-A (1–5), FR-B (6–9), FR-C (10–15), FR-D (16–18), FR-E (19–21), FR-F (22–24). Every PRD cite was checked against the brief text at that number:

| PRD FR | Cites | Brief content at cite | Verdict |
|---|---|---|---|
| FR-1 | §6 | schema v1.0, metadata, six block types | ✓ |
| FR-2 | §6 | forward compatibility, V3 reservations | ✓ |
| FR-3 | §6 | validators, shared package | ✓ (see GAP-1: docs sub-item dropped) |
| FR-4 | §5.1 | topic/context/guidance + edon-rag retrieval | ✓ |
| FR-5 | §5.2 | pipeline: plan → blocks → validation | ✓ |
| FR-6 | §5.3 | citations stored | ✓ |
| FR-7 | §5.4 | drafts, idempotent/cached, explicit regeneration | ✓ |
| FR-8 | §5.5 | async queue + progress | ✓ |
| FR-9 | §5.6 | faithful preview | ✓ |
| FR-10 | §5.7 | block-level editing; regeneration desirable | ✓ |
| FR-11 | §5.8 | explicit publish, immutable versions | ✓ |
| FR-12 | §5.9 | nothing student-visible until published | ✓ |
| FR-13 | §5.10 | player renders all block types | ✓ |
| FR-14 | §5.11 | SpeechSynthesis, swappable provider | ✓ |
| FR-15 | §5.12 | quiz types, client-side scoring, reporting | ✓ |
| FR-16 | §5.13, §8.4 | curated glTF library / 3D asset sources + licence metadata | ✓ both |
| FR-17 | §5.14 | sandboxed iframes, params, checks | ✓ |
| FR-18 | §5.15 | low-spec performance, compression, budgets | ✓ |
| FR-19 | §5.16 | student diagram requests in chat | ✓ |
| FR-20 | §5.17 | mandatory sanitisation (see DIST-1 on semantics) | ✓ cite itself correct |
| FR-21 | §5.18 | caching, rate limits, quotas | ✓ |
| FR-22 | §5.19 | mod_edonlesson placement/embedding | ✓ |
| FR-23 | §5.20 | completion + gradebook writeback | ✓ |
| FR-24 | §5.21 | tenant-scoped auth, identity | ✓ |
| FR-25 | §5.22 | full tenant isolation | ✓ |
| FR-26 | §5.23 | per-tenant config | ✓ |
| FR-27 | §5.24 | structured event logging, tenant/user IDs | ✓ |

Also verified: NFR-3/NFR-7 → brief §9 ✓; NFR-8 → §11 ✓; PRD §8 → §7 ✓; PRD §10 → §4 ✓; PRD §11 → §11 ✓; addendum cites to §3.1, §8, §9, §10, §11, §12.3–§12.5 ✓; all `project-context.md` section cites (§§2–8) ✓.

**Miscites found: none.** One cosmetic looseness: addendum §1 "Cost-economics rationale (brief §1/§11 + project-context §3)" — the migration-trigger specifics exist only in project-context §3, not in the brief; consider splitting the attribution so readers don't hunt the brief for them.

---

## 5. Recommended actions (priority order)

1. **DIST-1 (medium):** Fix FR-20's consequence to strip-then-reject-on-failure semantics matching brief §5.17 / project-context §4.
2. **LEAK-1 (low):** Tag SM-C1–SM-C3 as PM additions (or add an OQ) for stakeholder confirmation.
3. **DIST-2 (low):** Rewrite the offline/SCORM `[NOTE FOR PM]` to the brief's fast-follow framing.
4. **GAP-1 (low):** Add schema documentation to FR-3 / §9.1.
5. **DIST-3, GAP-2, GAP-3, LEAK-2, LEAK-3 (low):** one-line wording fixes as described above.
