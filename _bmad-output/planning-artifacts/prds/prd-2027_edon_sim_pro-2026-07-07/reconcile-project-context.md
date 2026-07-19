# Reconciliation Report — PRD vs project-context.md

**Run date:** 2026-07-07
**Input source (authoritative):** `_bmad-output/project-context.md`
**Targets audited:** `prd.md`, `addendum.md` (this folder)
**Auditor scope:** contradictions, capability-level gaps, duplication/drift risk, citation accuracy.

## Verdict

The PRD and addendum are well reconciled with project-context.md. Every [HARD] rule (generate-once, review gate, tenant isolation, SVG sanitisation, simulation sandboxing, no wildcard CORS, LLM adapter, cost telemetry, clean-room/licensing) and every load-bearing architecture principle (schema-first, immutable publications, async generation) is represented at capability level, and all section citations point at the correct sections — **zero miscites found**. No critical or high findings. The remaining issues are one medium sanitisation-scope loophole (the Mermaid intermediate in FR-19), one medium capability gap (per-user rate limits beyond Diagram Requests), and several drift-prone verbatim duplications of [HARD] wording.

---

## 1. Contradictions

### C-1 — FR-19's Mermaid intermediate opens a Sanitisation-scope loophole — **MEDIUM**

- **Location:** `prd.md` §4.5 FR-19 ("SVG; an intermediate text representation such as Mermaid is acceptable internally") vs FR-20 and Glossary "Sanitisation".
- **Issue:** project-context §4 [HARD] requires that "every LLM-generated SVG … passes an allowlist-based sanitiser … before storage or rendering." FR-20 faithfully repeats "Every LLM-generated SVG". But if the LLM emits Mermaid text and a local renderer produces the SVG, a literal reader can argue the resulting SVG is *renderer*-generated, not *LLM*-generated, and skips Sanitisation. FR-19 introduces exactly that path into the PRD without closing the scope question. This is a potential *weakening by construction*, not by statement — but it is the only place either target document creates room under a [HARD] security rule. Secondary issue: the Mermaid note is implementation detail, which the PRD's own §0 says belongs downstream.
- **Suggested fix:** (a) In FR-20, broaden the subject to "every SVG derived from LLM output — whether emitted directly or produced from an LLM-emitted intermediate representation — passes Sanitisation before storage or rendering." (b) Move the "Mermaid acceptable internally" note from FR-19 to `addendum.md` §1 (Architect section).

### C-2 — FR-8 consequence is narrower than the async-generation rule — **LOW**

- **Location:** `prd.md` §4.2 FR-8, consequence "no *user-facing* request blocks on a full generation run".
- **Issue:** project-context §6 says "the API never blocks a request on a full generation." "User-facing request" is a strict subset of "a request" — a machine-to-machine call (e.g., from mod_edonlesson or an operator tool) could be read as exempt. Almost certainly unintended paraphrase, but it is formally weaker.
- **Suggested fix:** Change to "no API request blocks on a full generation run."

### C-3 — Tenant-isolation restatements drop "including in admin tooling" — **LOW**

- **Location:** `prd.md` §1.1 I-4 and §4.7 FR-25 consequence.
- **Issue:** project-context §4 [HARD] reads "Cross-tenant access paths must not exist, **including in admin tooling**, except through explicit operator-role endpoints." Both PRD restatements keep the operator-endpoint exception but drop the admin-tooling call-out. Logically the PRD wording still covers admin tooling ("no cross-Tenant access path exists outside explicit Operator-role endpoints"), but the explicit call-out exists precisely because internal/admin tools are the common leak path, and A-2 establishes that a minimal internal Operator surface *will* exist.
- **Suggested fix:** Add "including internal/Operator tooling" to the FR-25 consequence (one clause; no other change needed).

**No contradictions found against:** generate-once (I-1, NFR-6, FR-7, FR-21 all conform, including the diagram-only exception), review gate (I-2, FR-12 exception wording matches exactly), immutable publications (FR-11), schema-first (Feature 4.1), LLM adapter (§6 Integrations), cost telemetry (FR-27 field list matches §3 [HARD]), no-wildcard-CORS (NFR-3), clean-room/licensing (NFR-7, GPLv3-thin plugin correctly carved out), self-hosting/VPS constraint (addendum §1 restates it correctly), external-systems boundary (§6/§8 match §8 of project-context). Note that FR-17's requirement of automated pre-publish checks for Simulations is *stronger* than project-context — permissible (it derives from the brief) and not flagged.

---

## 2. Gaps

### G-1 — Per-user rate limits appear only for Student Diagram Requests — **MEDIUM**

- **Location:** `prd.md` §4.7 FR-26 (Operator config set), Glossary "Quota" ("per-Tenant or per-Student cap").
- **Issue:** project-context §4 requires "per-tenant budgets and **per-user** rate limits are enforceable at the adapter layer, not only at UI level." The PRD carries per-Student rate limits solely for Diagram Requests (FR-21) and per-Tenant Quotas/Budget Ceilings (FR-26). No FR establishes per-user (notably per-Teacher) rate limiting as a platform capability — e.g., a single Teacher script-looping Generation Jobs can burn the entire Tenant budget with nothing between UI and the Tenant ceiling. This has product-level implications (abuse control, humane limit messaging, Operator configuration surface) that downstream UX/epics will not plan for if the PRD is silent.
- **Suggested fix:** In FR-26, add per-user rate limits to the Operator-configurable set (or add a consequence: "per-user rate limits are enforceable platform-side for all LLM-spending actions, not only Diagram Requests"), and generalise the Glossary "Quota" entry to "per-Tenant or per-user".

### G-2 — Teacher-initiated Diagram Requests are defined but never granted by an FR — **LOW**

- **Location:** `prd.md` §3 Glossary "Diagram Request" ("a Student- **or Teacher-**initiated request") vs Feature 4.5 (titled and scoped Student-only; FR-19 grants the capability to Students only).
- **Issue:** The Glossary (and project-context §4's "teacher- or student-side" sanitisation wording) implies Teacher-side on-demand diagrams exist, but no FR covers them. Downstream readers cannot tell whether Teacher chat-initiated diagrams are in scope, or whether "Teacher-side" refers only to Diagram Blocks produced inside the generation pipeline. Sanitisation coverage (FR-20) is safe either way; the scope of the *capability* is the ambiguity.
- **Suggested fix:** Either add a sentence to FR-19 ("Teachers may issue Diagram Requests through the same surface under the same caching/quota rules") or trim "or Teacher-initiated" from the Glossary and note that Teacher-side SVGs arise only via the generation pipeline.

### G-3 — Cache-hit telemetry vs the per-LLM-call definition of Cost Telemetry — **LOW**

- **Location:** `prd.md` FR-21 consequence ("Cache hits and misses are recorded in Cost Telemetry") vs FR-27 / Glossary ("per-LLM-call structured records").
- **Issue:** project-context §3 [HARD] defines cost telemetry as fields on every LLM call (with a cache hit/miss field). A cache *hit* involves no LLM call, so FR-21's requirement is unsatisfiable under FR-27's own definition as written. This is an internal PRD tension that could lead downstream to either dilute the [HARD] per-call requirement or skip hit-rate instrumentation (which SM-5 needs).
- **Suggested fix:** In FR-27, note that cache-hit events are additionally recorded as zero-cost Structured Events (or telemetry events without token fields); keep the per-LLM-call [HARD] definition intact.

**No other gaps.** Checked and found adequately reflected at capability level: API key rotation (NFR-3), replay independence from LLM availability (NFR-4), prompts-as-configuration (Risk §11 mitigation), structured tenant+user-attributed logging (FR-27/NFR-5), embeddable player (FR-22 + addendum §1), V3 seams (addendum §1 lists all six), 3D asset licence metadata (FR-16/NFR-7), operator-role exception (I-4/FR-25). Correctly *omitted* as implementation detail (not gaps): No-TypeScript, stack/deployment, test standards, repo layout, ADR mechanics, adapter internals.

---

## 3. Duplication Risk

| ID | Location | What is duplicated | Risk | Severity | Suggested fix |
|----|----------|--------------------|------|----------|---------------|
| D-1 | `prd.md` §3 Glossary "Sanitisation" | Verbatim allowlist mechanism list from §4 [HARD] ("strip scripts, event handlers, `foreignObject`, external references") | Security-load-bearing list; if project-context's allowlist evolves (e.g., adds `use`/href restrictions), the Glossary silently diverges and downstream tests get written against the stale copy | **MEDIUM** | Keep one exemplar clause but append "(authoritative list: project-context.md §4 [HARD])" and drop the implication of completeness |
| D-2 | `addendum.md` §1 "Cost-economics rationale" | Near-verbatim copy of §3 migration path: ~60–70% trigger, two consecutive months, 24 GB GPU, Qwen3-32B-class, INT4, vLLM, guided decoding | The most drift-prone duplication in either target — five specific numbers/identifiers restated; a threshold or model-class change in project-context leaves a contradicting addendum | **MEDIUM** | Replace the parameter recital with "migration trigger and target stack per project-context.md §3 (authoritative)"; keep only the design consequence ("config change + eval pass, or the adapter is wrong") |
| D-3 | `prd.md` FR-17 description | Sandbox properties reworded from §4 [HARD]: description says "no network access, strict content-security policy, communication only via a defined message protocol" — omits the storage-API ban and softens "postMessage protocol" to "message protocol"; only the consequence restores storage APIs | A reader treating the description sentence as the requirement gets a weaker sandbox spec | **MEDIUM** | Add "no storage APIs" and "postMessage" to the FR-17 description sentence so description and consequence match §4 |
| D-4 | `prd.md` §3 Glossary "Cost Telemetry" | Field list from §3 [HARD] (tokens in/out, cost, tenant, user, workload, cache hit/miss, latency) | Field-list drift if telemetry schema evolves | **LOW** | Append "(per project-context.md §3 [HARD])" |
| D-5 | `prd.md` NFR-3 | Aggregate restatement of several §4 rules (CORS, secrets-via-env, key rotation) | Multiple rules in one sentence; moderate drift surface but already cites §4 [HARD] | **LOW** | None required; citation already present |
| D-6 | `prd.md` §1.1 I-1–I-4 | Close paraphrase of the four core invariants; I-1 adds "in the MVP" scoping absent from project-context §1 | Acceptable framing for a scoped-to-MVP PRD (project-context itself anticipates V3 per-session economics), but the invariants block carries no pointer to the authoritative source | **LOW** | Add one line under §1.1: "Authoritative wording: project-context.md §§1, 4, 6 [HARD]" |
| D-7 | `prd.md` FR-2 consequence | "documented compatibility note" vs §6's "documented migration/compatibility note" | "Migration" dropped; trivially narrower | **LOW** | Restore "migration/compatibility note" |
| D-8 | `prd.md` FR-21 | Restates §3 caching rule ("cached Tenant-scoped on a normalised request key before any LLM call") | Currently word-exact; standard drift exposure only | **LOW** | Optionally cite §3 |

---

## 4. Citation Check (project-context section references)

All references verified against the section numbering of `_bmad-output/project-context.md` (§1 What This Project Is, §2 Stack, §3 LLM/Inference, §4 Security, §5 Legal/Licensing, §6 Architecture Principles, §7 Quality/Testing, §8 Repo Conventions).

| Where | Cited as | Claimed content | Correct? |
|-------|----------|-----------------|----------|
| prd.md FR-18 / NFR-2 | §7 | low-spec profile exercised in automated testing | ✅ (§7 low-spec CI profile) |
| prd.md FR-20 | §4 [HARD] | SVG Sanitisation | ✅ |
| prd.md FR-25 / I-4 | §4 [HARD] | tenant isolation, operator-role exception | ✅ |
| prd.md FR-26 | §4 (no [HARD] claimed) | platform-layer budget/quota enforcement | ✅ (§4 adapter-layer bullet; PRD correctly does not tag it [HARD]) |
| prd.md FR-27 | §3 [HARD] | cost telemetry on every LLM call | ✅ |
| prd.md NFR-3 | §4 [HARD] | sanitisation, sandboxing, isolation, CORS, secrets, rotation | ✅ |
| prd.md NFR-5 | §3 | telemetry as model-migration instrument | ✅ (matches §3 wording) |
| prd.md NFR-7 | §5 [HARD] | clean-room, licensing | ✅ |
| prd.md §6 (LLM provider) | §3 [HARD] | provider-agnostic adapter, per-workload config, no hardcoded identifiers | ✅ |
| addendum.md §1 (cost-economics) | §3 | migration path | ✅ |
| addendum.md §2 | §8 | repo layout | ✅ |
| addendum.md §4 | §§2, 6–8 | "tech stack, deployment, testing standards, repo conventions" | ✅ range / ⚠ see M-1 |
| addendum.md §4 | §5 [HARD] | clean-room/licensing | ✅ |
| addendum.md §4 | §3 | model/provider specifics, migration path | ✅ |

**Miscites: none.**

### M-1 — Addendum §4 topic list is imprecise for the §§2, 6–8 range — **LOW**

- **Location:** `addendum.md` §4, first bullet.
- **Issue:** The bullet names "tech stack, deployment, testing standards, repo conventions" for §§2, 6–8, but §6 is *Architecture Principles* (schema-first, async, immutable publications, extension seams) — a topic not in the list, and one whose principles **are** (correctly) reflected in the PRD at capability level (I-3, FR-8, FR-11). So the claim "deliberately not in the PRD" is inaccurate for §6 as blanket-stated.
- **Suggested fix:** Change to "…: `project-context.md` §§2, 7–8 (authoritative). Architecture principles (§6) are reflected in the PRD at capability level only; their build-rule form remains authoritative in project-context."

---

## 5. Finding Index

| ID | Severity | One-line summary |
|----|----------|------------------|
| C-1 | Medium | FR-19 Mermaid intermediate creates a scope loophole under the [HARD] SVG-sanitisation rule |
| G-1 | Medium | Per-user rate limits (§4) surface only as Student Diagram limits; no per-Teacher/per-user capability in FR-26 |
| D-1 | Medium | Glossary duplicates the [HARD] sanitisation allowlist verbatim — drift-prone security wording |
| D-2 | Medium | Addendum restates §3 migration-path numbers (60–70%, 24 GB, Qwen3-32B, INT4, vLLM) — most drift-prone copy |
| D-3 | Medium | FR-17 description omits the storage-API ban present in §4 [HARD] (consequence restores it) |
| C-2 | Low | FR-8 "user-facing request" narrower than §6 "the API never blocks a request" |
| C-3 | Low | I-4/FR-25 drop "including in admin tooling" from the isolation rule |
| G-2 | Low | Teacher-initiated Diagram Requests defined in Glossary but granted by no FR |
| G-3 | Low | FR-21 cache-hit telemetry unsatisfiable under FR-27's per-LLM-call definition as written |
| D-4–D-8 | Low | Minor duplication/paraphrase exposures (telemetry field list, NFR-3, invariants block, FR-2, FR-21) |
| M-1 | Low | Addendum §4 topic list imprecise for §6 (architecture principles) |

**Critical findings: 0. High findings: 0.** The document set does not weaken any [HARD] rule by statement; C-1 is the only construction that creates room under one, and it is a one-clause fix.
