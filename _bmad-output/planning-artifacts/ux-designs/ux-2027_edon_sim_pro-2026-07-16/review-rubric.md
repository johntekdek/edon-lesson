# Spine Pair Review — 2027_edon_sim_pro

## Overall verdict

The spine pair is a genuinely source-extractable contract: all five UJs are accounted for (UJ-4's exclusion stated three times), the 24-component vocabulary matches exactly across both files, every frontmatter token carries a value and every `{path.to.token}` reference resolves, and every stated contrast ratio was verified computationally and is correct. One high-severity internal contradiction (Flow 1 uses the exact copy string the Voice and Tone table bans) and three medium gaps (unseen gold dot has behavior but no visual spec and brushes the gold-contrast rule; Completion summary surface has states but no visual anatomy; Authoring UI has no failed-save/offline state) should be fixed before the pair is marked final — none of them blocks architecture from starting.

## 1. Flow coverage — strong

Extracted UJ-1..UJ-5 from PRD §2.3 and walked FR-1..FR-29 against Key Flows, Component Patterns, and State Patterns. Flows 1–4 map to UJ-1, UJ-2, UJ-3, UJ-5 with journey names and protagonist names (Dr. Amina, Chinedu, Ngozi) verbatim from the PRD; each has numbered steps, a bold **Climax** beat, and failure paths. UJ-4 exclusion is stated where required: EXPERIENCE.md line 213 ("UJ-4 (Operator onboarding) has no UX surface in scope (A-2)"), plus the Foundation operator fence (line 24) and the IA surface-closure line (line 56). Flow 5 (Reported diagram triage, FR-28) is an earned addition — it closes the governance loop no UJ names. FR sweep: every Teacher/Student-surfaced FR (FR-2–FR-23, FR-26 UX consequences, FR-28, FR-29) lands in a flow, component row, or state row; FR-24/FR-25/FR-27 are correctly left as backend concerns with only their UX edges (discard event, writeback retry) surfaced.

### Findings
- **low** UJ-1's one PRD-named edge case ("the generated lesson is off-target; she discards the Draft, refines her guidance, and explicitly regenerates," PRD §2.3) is realized mechanically — Generate form row cites "whole-Lesson Regeneration (FR-7, UJ-1 edge)" (EXPERIENCE.md line 114) and a Discard Draft state exists (line 150) — but Flow 1's failure paths (line 226) don't walk it. *Fix:* add one sentence to Flow 1's failure paths: off-target draft → discard → reopen prefilled Generate form → explicit regenerate.
- **low** Flow 4's "*Failure path*" (line 254) is a colleague-duplication alternate path, not a failure. *Fix:* relabel "Alternate path" so consumers don't scan for an error state that isn't one.

## 2. Token completeness — strong

Extracted all frontmatter tokens (16 colors, 8 typography roles, 4 radii, 8 spacing entries, 17 component token objects) and every `{path.to.token}` reference in the prose of both files. All color tokens carry hex values — no critical misses. Every reference resolves: all 17 component objects reference only defined tokens; DESIGN.md prose references (`{colors.*}`, `{typography.*}`, `{spacing.*}`, `{rounded.*}`, `{components.*}`) all resolve; EXPERIENCE.md's sole literal token reference (`{typography.player-ui}`, line 21) resolves. The `player-ui` note-form token correctly follows the design-md-spec platform-convention pattern. Stated contrast ratios were recomputed and all check out: primary on white 6.9:1 ✓, accent-ink on accent 7.6:1 ✓, ink-secondary on white 6.7:1 ✓, error on white 6.4:1 ✓, gold on white 1.7:1 (documented as a prohibition) ✓.

### Findings
- **low** Two token references carry inline size overrides that exist only in prose: buttons use "`{typography.label}` at 15px" (DESIGN.md line 200) and Player slides use "`{typography.body}` at 17px on phones" (line 213). A consumer generating a theme from the frontmatter alone misses both. *Fix:* either add tokens (e.g., `label-button`, `body-player`) or state the deltas in the frontmatter component objects.
- **low** Two meaning-carrying pairs used by components have no stated ratio: `primary-deep` on `primary-wash` (quiz-correct, info banner, Published chip — computes to ≈8.7:1, passes) and `error` on `error-wash` (error banner, quiz-incorrect — ≈5.7:1, passes). The Do's table pledges "Meet AA contrast on every text/fill pair listed in § Colors" (line 236) but these pairs aren't listed with ratios. *Fix:* add the two ratios to § Colors so the pledge is checkable.

## 3. Component coverage — adequate

Extracted every component name used anywhere in either spine. The two tables match exactly: 24 rows in DESIGN.md § Components (lines 198–223) and 24 rows in EXPERIENCE.md § Component Patterns (lines 108–133), identical names, even identical order. Each row carries real rules on both sides — visual anatomy with token references in DESIGN, behavioral contracts with FR citations in EXPERIENCE. No one-word descriptions. The misses are elements referenced outside the tables:

### Findings
- **medium** The session-local "unseen" gold dot is behaviorally specified (EXPERIENCE.md Block rail row line 116; Block regenerating state line 146; Flow 1 step 4 line 220) but has no visual spec — DESIGN.md's Block rail row (line 206) lists index, glyph, excerpt, chip, and selection state only. Worse, a small solid-gold dot on the white/light rail is a meaning-carrying gold element on a light surface at 1.7:1 — DESIGN.md's own rule bans gold "as text or a meaning-carrying hairline on light surfaces" (line 158) and WCAG 1.4.11 needs 3:1 for UI indicators. *Fix:* spec the dot in DESIGN.md's Block rail row and resolve the contrast tension (e.g., gold-wash pill with `{colors.accent-ink}` dot/outline, or fold "unseen" into the Needs-review chip treatment).
- **medium** Completion summary is an IA surface (EXPERIENCE.md line 46) with behavioral coverage (Completion reached state, line 159; Flow 2 climax) but no visual spec in DESIGN.md and no Component Patterns row — the only Student-facing screen with no anatomy anywhere (tick list, score status line, attempts line, jump-back links). *Fix:* add a Completion summary row to both component tables.
- **low** Cold-load skeletons are prescribed (EXPERIENCE.md line 139) but no skeleton visual exists in DESIGN.md (fill token, shimmer or static). *Fix:* one line in DESIGN.md (e.g., `{colors.surface-subtle}` static blocks, no shimmer in the Player).
- **low** Three small elements referenced in prose lack specs: the persistent header Course Context chip (IA line 28 — the chip treatment is specced only inside the Generate form row), the Lesson card "version history line" (line 113), and the Diagram review queue badge (Flow 5, line 258). *Fix:* a clause each in the relevant DESIGN.md rows.

## 4. State coverage — adequate

Walked every IA surface against the 33-row State Patterns table plus component-row states. Coverage is unusually complete: Course home (cold, empty, generating, failed, budget-paused, idempotent-route), Review Workspace (regenerating, validation error, check failed, discard, admin banner), Publish dialog (pass/fail/succeeded), Relaunch notice, Player (cold, connectivity loss, unknown Block, major-version mismatch, version pinning, flagged-off Simulations, not-available), Quiz (syncing, writeback failure, attempts exhausted), completion, and eight diagram-message states including the Rate Limit vs Quota split the PRD Glossary demands. Focus states covered via DESIGN focus ring + Accessibility Floor. Misses:

### Findings
- **medium** No failed-save/offline state for the Authoring UI. Inline edit promises "save is automatic on valid input with visible 'Saved' text" (EXPERIENCE.md line 183) — but there is no treatment for a save that fails or connectivity loss mid-review, on a product whose own context is constrained bandwidth. A Teacher could lose edits silently, which the spine elsewhere prohibits as a principle. *Fix:* add a State Patterns row (e.g., "Edit save failed / offline — Review Workspace — persistent 'Not saved — retrying' state on the field/banner; edits retained locally; never silent").
- **low** The Cold load row (line 139) names Course home and Player only; Review Workspace cold load (rail + editor skeleton) is unspecified. *Fix:* extend the row.
- **low** Generate form field validation (FR-4: "a request without a topic … is rejected with a clear message") has no explicit state row — Draft validation errors are covered (line 147) but not the pre-submit empty-topic case. *Fix:* one row or a clause in the Generate form component row.
- **low** Player script-load failure (the bundle or Published Version itself failing to fetch, vs. lazy assets, which line 156 covers) is untreated. *Fix:* one row; can reuse the calm can't-play voice of the major-version state.

## 5. Visual reference coverage — adequate

`mockups/` and `wireframes/` do not exist yet; `imports/` and `.working/` exist and are empty. Per `.memlog.md` (line 21) key-screen mocks are being rendered in parallel: Review Workspace (desktop), Player on low-spec phone including fallback states, Diagram chat message. Not penalized. Spine sections that reference visuals: only the EXPERIENCE.md header note ("Spines win on conflict with any mock or import," line 14) — neither spine carries the exemplars' `→ Composition reference: mockups/…` pointers yet.

### Findings
- **low** No composition-reference pointers in the IA section (the pattern both experience exemplars demonstrate). *Fix:* when the three mocks land, add `→ Composition reference:` lines under Information Architecture naming them, keeping the spine-wins rule.

## 6. Bloat & overspecification — strong

DESIGN.md carries editorial voice where allowed (Brand & Style, Colors) and stays tabular in Components; pixel values present (44/48px targets, 280/320/640/720px panes) are load-bearing under the device floor and accessibility floor, not decoration. EXPERIENCE.md prose is functional — tables for V&T, components, states, responsive; the only narrative flourishes are inside Key Flows climaxes, which the exemplars sanction. No source restatement beyond traceability parentheticals (A-21, OQ-16 citations), which earn their keep as inheritance anchors.

### Findings
- **low** The no-webfonts/flat-Player rule is restated in ~7 places (DESIGN.md lines 66, 151, 174, 188, 212, 233; EXPERIENCE.md lines 21, 84). Deliberate emphasis, but a future change touches seven sites. *Fix:* keep `{typography.player-ui}` as the single normative statement and let the others reference it.

## 7. Inheritance discipline — adequate

All four frontmatter source paths resolve from the repo root (verified on disk). UJ names, protagonist names, and journey titles are verbatim PRD §2.3. Spot-checked ~30 FR/OQ/A/I citations across both spines against the PRD — all accurate, including the subtle ones (A-27 fallback preview, A-28 editability map, A-34 p90, A-35 check intent, OQ-15 completion semantics, project-context §2 [HARD] no-TypeScript, §6 unknown-block rule). Glossary terms (Tenant, Teacher, Student, Draft, Published Version, Block, Generation Job, Launch Token, Diagram Request, Review Gate, Rate Limit vs Quota, Budget Ceiling, Tenant Admin, Grounding Chunk, Curated Model Library) are used verbatim and correctly capitalized in both files. Component names identical across all four sections. EXPERIENCE token references resolve to DESIGN tokens by name. One real break:

### Findings
- **high** Internal copy contradiction: Flow 1 step 2 has the Generation progress card read "**Usually ready in under 5 minutes.** You can close this — we'll keep working." (EXPERIENCE.md line 218) — the exact promise the Voice and Tone table bans ("don't promise 'under 5 minutes' — SM-1 is a median; p90 is 2× it, A-34," line 93) and the State Patterns row re-bans ("never promise a hard number," line 142). Flow copy is what story-dev lifts verbatim; the spine currently ships both the rule and its violation. *Fix:* change the Flow 1 string to the V&T Do-column copy: "Usually ready in a few minutes."
- **low** The header vocabulary list (line 14) names 10 Glossary terms "verbatim" but the spine correctly relies on ~7 more (Citations, Grounding Chunk, Budget Ceiling, Rate Limit, Quota, Tenant Admin, Course Context). Usage is correct throughout; the list is just incomplete. *Fix:* either say "PRD Glossary §3 verbatim throughout" without enumerating, or complete the list.
- **low** DESIGN.md line 169 grounds the SIL OFL font licences in "project-context.md §5," but §5's dependency rule names MIT/BSD/Apache-2.0-or-compatible and never mentions OFL. OFL webfonts are almost certainly fine (and the Player ships none), but the citation overstates what §5 grants. *Fix:* rephrase as "licence metadata recorded when the dependency lands; OFL acceptability to be confirmed in architecture per §5."

## 8. Shape fit — strong

DESIGN.md: all eight body sections present in canonical order (Brand & Style → Colors → Typography → Layout & Spacing → Elevation & Depth → Shapes → Components → Do's and Don'ts). Frontmatter carries `name` and `description` per spec, plus the spine-pair extensions (status/sources/updated) the exemplars use.

EXPERIENCE.md: all required defaults present — Foundation, IA, Voice and Tone, Component Patterns, State Patterns, Interaction Primitives, Accessibility Floor, Key Flows — plus Responsive & Platform (warranted: three surfaces, container-vs-viewport distinction is load-bearing).

**Omitted default — Inspiration & Anti-patterns: defensible.** Its rejected-pattern payload already lives in three enforced homes: the "Banned everywhere" list (line 186), DESIGN's Do's/Don'ts, and the PRD §8 fences the Foundation restates (no-dashboard, operator exclusion). A standalone section would mostly restate PRD non-goals — exactly the bloat category 6 polices. The only thing genuinely lost is named product inspirations for the Review Workspace, which is a nice-to-have, not contract material.

**Invented sections — all three earn their place.** *Capability Tiers & Degradation Ladder* converts the product's hardest constraint (FR-18/OQ-16) into a testable three-tier contract with detection rules and the "degraded states are designed states" principle — this is the section architecture will quote. *Moodle Embedding Contract* makes "feels native" (FR-22/A-12) verifiable behavior (inherit page scroll, self-managed height, namespaced CSS, one instance per page). *Open Items for Stakeholder* operationalizes the run's batched-confirmation discipline; all 13 items are traceable to inline `[ASSUMPTION]` tags or PRD OQs, none silently adopted (OQ-7 handling is exemplary — floor stands regardless, WCAG adoption flagged as scope addition).

### Findings
- **low** The two invented constraint sections sit between IA and Voice and Tone, splitting the default sequence the exemplars keep contiguous. Harmless, but Capability Tiers reads naturally right after Foundation. *Fix:* optional reorder; do not block on it.

## Mechanical notes

- **Component parity:** 24/24 names identical across DESIGN.md § Components and EXPERIENCE.md § Component Patterns, same order — matches the `.memlog.md` claim exactly.
- **Cross-references:** all four `sources:` paths resolve on disk; `EXPERIENCE.md` → `DESIGN.md § Brand & Style / § Colors / § Components / § Layout & Spacing` section references all exist; `.memlog.md` (referenced at line 266) exists; `{typography.player-ui}` resolves. No broken references found.
- **Contrast verification:** all five stated ratios recomputed and correct (6.9, 7.6, 6.7, 6.4, 1.7). Unstated pairs also pass: primary-deep/primary-wash ≈8.7:1, error/error-wash ≈5.7:1, primary fill vs border track ≈5.3:1 (non-text 3:1 ✓).
- **Copy interpolation braces:** `{retry window}`, `{n}` (State Patterns) are Tenant-config interpolation slots, not token paths — no dot-path shape, and the shadcn exemplar uses the same convention (`{user_name}`). No action.
- **Frontmatter:** both spines `status: draft` — correct per the run discipline (no final without batched sign-off). DESIGN has name + description (spec-required); EXPERIENCE mirrors the exemplar frontmatter shape.
- **Nit:** DESIGN.md § Layout & Spacing calls the scale an "8px scale" (line 180) but the values (4/8/12/16/24/32/48) are the standard 4-based hybrid. Cosmetic.
- **Naming watch:** the "College library" tab (Tenant-internal, OQ-13-granted) superficially collides with PRD §8's non-goal "no cross-Tenant lesson sharing or library." The spine's scoping is correct; keep the within-Tenant framing when the tab name is confirmed (Open Item 13).
- **Workspace:** `imports/` and `.working/` empty; `mockups/`, `wireframes/` not yet created — mocks in flight per `.memlog.md`.
