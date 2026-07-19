# Adversarial Review (Cynical Review) — e-DON Lesson Studio PRD

- **Targets:** `prd.md` + `addendum.md` (run `prd-2027_edon_sim_pro-2026-07-07`)
- **Method:** bmad-review-adversarial-general (Cynical Review persona); severity-ranked per requesting instruction
- **Reviewer stance:** Reconciliation against the brief and project-context has already passed, so fidelity to sources is *not* re-litigated here. This review attacks the PRD's own quality: internal contradictions, untestable requirements, journey/metric failures, and gaps that will detonate in UX, architecture, and epic/story creation. Per the scope fence (brief §12.2), no finding proposes new scope; missing capability is framed as an open question / stakeholder decision.
- **Date:** 2026-07-07
- **Verdict:** Structurally strong PRD with disciplined traceability, but it is not ready to feed epics: three critical holes (Teacher identity/authoring entry path, the diagram feature's undeclared chat-surface dependency, untriaged phase-blocking open questions) plus a cluster of high-severity semantic gaps (completion, editing, metrics denominators) will force downstream agents to invent product decisions the PM should own.

---

## CRITICAL

### C-1. The entire authoring journey rests on an entry path no FR provides: Teacher identity, Authoring UI authentication, and "course context" are all undefined

- **Location:** §2.3 UJ-1; §4.2 FR-4; §3 Glossary; §4.6 FR-24
- **Quote:** UJ-1: *"logs into the Authoring UI. She enters a topic ('Ohm's Law and simple circuits'), picks the course context"*; FR-4: *"A request without a topic or course context is rejected with a clear message."*
- **Why it matters:** Three unknowns stack here. (1) *How does a Teacher log in?* FR-24 covers only mod_edonlesson↔platform authentication; no FR, assumption, or OQ covers Teacher authentication/identity for the Authoring UI — yet §2.2 asserts "all access is mediated by institutional Moodle accounts." Moodle SSO? Separate accounts? Operator-issued credentials? (2) *What is a "course context"?* It is a mandatory field with a rejection rule, appears in the Lesson Script metadata as "course reference," and drives grounding and Moodle placement — and it is absent from a Glossary that downstream workflows must use "verbatim." (3) *Where does the picker's course list come from?* The Authoring UI is outside Moodle, and §6 confines Moodle integration to mod_edonlesson — so the UI has no specified way to know the Tenant's courses. UX cannot design a login or a picker, the Architect cannot design an identity model, and no authoring epic can be written until these are answered. This is the single largest hole in the document and it is invisible in §12.
- **Suggested fix:** Add an open question (phase-blocking, pre-architecture) covering Teacher identity/authentication for the Authoring UI and the source of course context data; define **course context**, **course reference**, and **curriculum reference** in the Glossary at capability level (defining terms the brief already uses is not new scope). If the intended answer is "same block_edon_ai/edon-rag credential pattern," say so as a tagged assumption.

### C-2. FR-19's delivery surface — the existing AI chat — is an external system the PRD never lists, colliding with its own "no modification of external systems" non-goal

- **Location:** §4.5 FR-19; §6 Integrations; §8 Non-Goals; addendum §3
- **Quote:** FR-19: *"A Student can request a labelled technical diagram … from within the existing AI chat experience"*; §8: *"No modification of external systems — edon-rag and Moodle core are consumed via API only (§6)"*; addendum §3: *"Diagram chat experience rides the existing block_edon_ai chat surface."*
- **Why it matters:** §6 purports to list all external dependencies (edon-rag, Moodle, LLM provider, 3D sources). block_edon_ai — an existing, deployed production plugin — is not on the list, yet an entire MVP feature (4.5) renders inside it. Someone must modify block_edon_ai to surface diagram requests and render SVGs, and the PRD is silent on whether that plugin is in-scope-modifiable, whose repository/backlog absorbs the change, and what the integration contract is. Either §6 is incomplete or §8's non-goal is violated; both cannot be true as written. The Diagram epic (a headline Student feature and the only Review-Gate exception) stalls at story creation with no owner for half its surface area.
- **Suggested fix:** Add block_edon_ai to §6 with its dependency status (modifiable companion vs. API-only external), and raise an open question for the stakeholder to confirm which. If modifiable, the required change belongs in the repository plan (addendum §2), which currently names only `edon-lesson` and `mod_edonlesson`.

### C-3. Open questions are untriaged: several are phase-blockers for epics/stories, but nothing marks them as blocking, owned, or deadlined

- **Location:** §12 Open Questions; §10; §4.3 FR-10; §4.4 FR-15
- **Quote:** §12 lists ten OQs flatly, e.g. OQ-3: *"Commit to MVP or defer? Scope decision — requires explicit confirmation"*; OQ-4: *"confirm deterministic normalised matching."*
- **Why it matters:** These are not equal. **OQ-3** (Block-level Regeneration) changes the epic decomposition of Features 4.2/4.3 — the story set is materially different with and without it, and H-8 below shows the review experience degrades sharply without it. **OQ-4** gates quiz Block schema design (accepted-alternates authoring is a schema question, and the Schema is the first story per addendum §2 sequencing). **OQ-1/OQ-2** gate the acceptance criteria of every quota/budget story ("a Tenant at quota stops incurring diagram LLM spend" cannot be tested without values or at least defaults) and the validation of primary metric SM-4. **OQ-9** gates the enforcement behavior of FR-26. A downstream agent picking up this PRD has no way to know which questions it may proceed past and which it must halt on — so it will guess, and the scope fence exists precisely to prevent guessing.
- **Suggested fix:** Add a blocking classification to each OQ (blocks architecture / blocks epics / blocks specific stories / launch decision), an owner (stakeholder vs. PM), and a resolve-by phase. Explicitly resolve OQ-3 and OQ-4 before epic creation begins.

---

## HIGH

### H-1. Intra-Tenant authorization is completely unspecified: who may edit, publish, or place whose lessons?

- **Location:** §4.3; §4.6 FR-22; §4.7 FR-25
- **Quote:** FR-22: *"A published Lesson is placeable as a course activity by a Teacher with normal Moodle course-editing rights and no platform-side help."*
- **Why it matters:** The PRD specifies Tenant isolation exhaustively (I-4, FR-25) and Teacher-level permissions not at all. Can Teacher B open, edit, or publish Teacher A's Draft? Can any course editor place any of the Tenant's Published Versions, or only their own? Does the Authoring UI list all Tenant lessons or per-Teacher lessons? Every Authoring UI story and the mod_edonlesson picker story hits this immediately. The brief is silent too — so this is a stakeholder decision, not scope invention, and the PRD failed to surface it.
- **Suggested fix:** Add an open question for the intra-Tenant permission model, or state the simplest default (all Teachers in a Tenant share authoring rights over all the Tenant's Lessons) as a tagged `[ASSUMPTION]` requiring confirmation.

### H-2. Client-side quiz scoring makes gradebook scores forgeable and ships answers to the Student device — and the PRD never acknowledges it

- **Location:** §4.4 FR-15; §4.6 FR-23; §10 SM-3; §2.1
- **Quote:** FR-15: *"Scoring happens client-side against the Published Version"*; §2.1 Student JTBD: *"know my scores count."*
- **Why it matters:** The Published Version — including correct answers, accepted alternates, and feedback — is delivered to the client so it can score offline of the server. Any student with DevTools can read the answers or POST a fabricated perfect score, which then writes to the institutional gradebook (FR-23) that the PRD promises "counts." Client-side scoring is brief-mandated (brief §5.12), so it is not the PRD's job to change it — but it *is* the PRD's job to surface the integrity limitation as a risk and get the stakeholder's explicit acceptance that MVP gradebook scores are low-stakes/forgeable, or to ask whether server-side plausibility checks are wanted. §11 Risks and §12 OQs are both silent. Downstream, this ambiguity will surface as a security-review bounce on the writeback story.
- **Suggested fix:** Add to §11 as an accepted-risk entry and add an OQ: confirm stakeholder acceptance of client-trust scoring for MVP gradebook writes (and whether answer exposure in the delivered script is acceptable), without proposing new scope.

### H-3. "Completion" — the thing SM-3 measures and FR-23 reports — is never defined, and the playback lifecycle (attempts, retakes, resume, republish attribution) is undefined with it

- **Location:** §4.6 FR-23; §10 SM-3; §2.3 UJ-2, UJ-5; §4.4 FR-15
- **Quote:** FR-23: *"mod_edonlesson reports lesson completion to Moodle completion tracking"*; UJ-2: *"his score is written to the Moodle gradebook and his completion is tracked."*
- **Why it matters:** No FR states what constitutes completing a lesson (all Blocks viewed? final Block reached? quiz submitted? quizzes optional?). Nor: whether a Student may retake a quiz, which score wins (first/best/latest), whether playback resumes after a dropped connection (on infrastructure whose bandwidth §11 itself flags as an assumption), or whether completion/grades persist when the Teacher republishes a new version with a different quiz (UJ-5). SM-3 ("completion tracking … functioning") is untestable against an undefined event, and the mod_edonlesson epic cannot write acceptance criteria for any of it. These are product semantics, not architecture decisions.
- **Suggested fix:** Define completion criteria and attempt/which-score-wins/republish-attribution semantics at capability level in FR-23 (or as tagged assumptions + one consolidated OQ if the stakeholder must rule). Resume behavior may defer to architecture, but say so explicitly.

### H-4. FR-7's idempotency cache contradicts explicit Regeneration, and the "discard" action the journeys and metrics rely on exists in no FR

- **Location:** §4.2 FR-7; §2.3 UJ-1 edge case; §10 SM-2
- **Quote:** FR-7: *"Submitting an identical generation request while a matching Draft exists does not invoke the LLM again"*; UJ-1: *"she discards the Draft, refines her guidance, and explicitly regenerates."*
- **Why it matters:** Two collisions. (1) Regeneration is "an explicit Teacher action that re-runs generation" — but if a Teacher explicitly regenerates with *identical* inputs (a legitimate move given LLM stochasticity: same request, hoping for a better roll), the idempotency rule says the LLM is not invoked and she gets the same Draft back. Which rule wins? The FR is self-contradictory as written, and the pipeline story will have to pick arbitrarily. (2) UJ-1 has her "discard the Draft" and SM-2's rationale says "if Teachers discard most Drafts, generation is failing" — but no FR provides a discard/delete-Draft capability, and FR-27's event list has no discard event, so discard behavior is both unbuildable and unmeasurable as specified.
- **Suggested fix:** State explicitly that explicit Regeneration bypasses the idempotency cache (idempotency guards *accidental* resubmission only), or the opposite; and either add Draft discard at capability level under FR-10's editing family (it is implied by the brief's draft lifecycle, arguably not new scope) or raise it as an OQ and rewrite UJ-1/SM-2's rationale to stop depending on it.

### H-5. SM-2's denominator is undefined, making the flagship quality metric ambiguous and gameable in both directions

- **Location:** §10 SM-2; §3 Glossary ("Lesson"); §2.3 UJ-1
- **Quote:** SM-2: *"Share of generated Lessons reaching a Published Version — ≥ 70%."*
- **Why it matters:** Per the Glossary, a Lesson owns "a version history of Drafts and Published Versions" — so a Lesson with five discarded Drafts and one publish counts as one success (100%), and per-Lesson counting hides exactly the generation-quality failure the metric exists to catch. Counted per Generation Job instead, UJ-1's *endorsed* edge-case behavior (discard, refine guidance, regenerate, publish) yields 50% — healthy iteration reads as failure. The 70% target means entirely different things under the two readings, and whoever implements the metric will pick whichever flatters the number. SM-C1/SM-C2 do not resolve the denominator.
- **Suggested fix:** Define the unit of measure explicitly (recommend per-Generation-Job, with the iterate-then-publish pattern acknowledged in the target rationale, or a paired per-Lesson + drafts-per-published-lesson reading) and state the measurement window.

### H-6. The counter-metrics cannot be computed from the committed instrumentation — SM-C1's stated derivation measures the wrong thing outright

- **Location:** §10 SM-C1, SM-C3; §13 A-16; §4.7 FR-27
- **Quote:** A-16: *"Teacher review time is derivable from existing Structured Events (generated→published timestamps); no extra instrumentation implied"*; FR-27: *"(lesson generated / published / started / completed, quiz submitted, diagram requested)."*
- **Why it matters:** Generated→published elapsed time measures calendar delay, not review effort: a Teacher who generates Monday and rubber-stamps Friday after 90 seconds shows four days of "review time." SM-C1 exists to detect rubber-stamping and, as instrumented, cannot — A-16 is simply false, and the counter-metric the PRD calls "as load-bearing as primaries" is decorative. Likewise SM-C3 (denial rate) needs rate-limit/quota *rejection* events, which are absent from FR-27's canonical list. Meanwhile FR-20 and FR-23 introduce additional Structured Events (sanitisation failure, writeback failure) outside that list, so the "canonical" event taxonomy is scattered across four FRs and provably incomplete against the PRD's own metrics — which also undercuts FR-27's unfalsifiable claim of being "sufficient to power a future analytics dashboard."
- **Suggested fix:** Consolidate one authoritative event list in FR-27 that includes every event other FRs reference (rejections/denials, generation failure, sanitisation failure, writeback failure), and either add a review-session signal to the list or strike A-16 and downgrade SM-C1 to "time-to-publish" with honest naming.

### H-7. FR-9's "exactly as Students will see it" is contradicted by FR-18's degradation design — Teachers can never preview the degraded lesson most at-risk Students will actually get

- **Location:** §4.3 FR-9; §4.4 FR-18; §2.3 UJ-2 edge case; addendum §3
- **Quote:** FR-9: *"preview the full Draft exactly as Students will see it"*; consequence: *"a lesson that previews correctly plays identically for Students"*; FR-18: *"When a heavy Block cannot run on a device, its poster image displays."*
- **Why it matters:** The target population is on low-spec Android; the Teacher previews on whatever she authors on. When the Model3D Block degrades to a poster on a Student device, the Student sees content the Teacher never reviewed in that form — the addendum even insists poster states are "designed states, not error states," yet no requirement lets a Teacher see them. "Plays identically" is untestable and false across device classes; the Review Gate's quality premise (Teacher saw what Students see) is overstated for exactly the flagship constraint. This will surface as a contested acceptance criterion in the preview story.
- **Suggested fix:** Weaken FR-9's claim to "same Player, same Published Version content" and either require poster/fallback states be visible in preview (a faithful-preview clarification, not new scope) or raise it as an OQ.

### H-8. Per-Block-type editability is undefined — "text edits" cannot fix a wrong Diagram label or a broken Simulation, so the review "fix" affordance quietly collapses to delete-or-discard

- **Location:** §4.3 FR-10; §2.3 UJ-1; §12 OQ-3; §13 A-11
- **Quote:** FR-10: *"text edits, Block deletion, and Block reordering are required."*
- **Why it matters:** What does a "text edit" mean per Block type? Slide/Quiz text, plausibly. But a Diagram Block is an SVG, a Model3D Block is asset-reference-plus-annotations, and a Simulation Block is generated code — none is meaningfully "text-editable" by a no-prompt-skill, moderate-digital-literacy Teacher. With Block-level Regeneration uncommitted (OQ-3), a Teacher facing one mislabelled diagram has exactly two options: delete the Block or discard the whole Draft and regenerate everything — directly contradicting UJ-1's "stay in control … correct … everything" narrative and pressuring SM-2 downward. The edit surface per Block type is a product decision the epic breakdown cannot proceed without.
- **Suggested fix:** Enumerate, per Block type, what is editable at capability level (even if the answer for Diagram/Simulation is "nothing — delete or regenerate"), and feed that honestly into the OQ-3 decision, whose stakes this gap raises considerably.

### H-9. FR-17's "automated checks" — the publication gate for the PRD's self-declared highest-variance feature — have no stated purpose or criteria

- **Location:** §4.4 FR-17; §11 Risks; §13 A-11
- **Quote:** FR-17: *"must pass the Review Gate plus automated checks before publish"*; §11: *"Simulation safety/quality is the highest-variance MVP feature."*
- **Why it matters:** The checks are named in the FR title role of a gate, blocked-publish behavior is specified (A-11), and the addendum hands "the automated pre-publish checks" to the Architect — but nowhere is it stated *what property the checks assure*: sandbox-protocol conformance? crash-freedom? resource bounds? parameter-schema validity? content safety? The Architect can design a mechanism; only the PM can say what it must catch. As written, the acceptance criterion "fails automated pre-publish checks" is a test against an undefined oracle, in the exact feature §11 flags as most likely to fail.
- **Suggested fix:** State the checks' intent at capability level (e.g., "verify the Simulation loads, respects the postMessage protocol, and exposes its authored parameters without runtime errors") and leave the mechanism to architecture.

### H-10. "Low-spec Android" is never defined — the product's signature constraint has no measurable form anywhere in the PRD

- **Location:** §5 NFR-2; §4.4 FR-18; §2.3 UJ-2
- **Quote:** NFR-2: *"the Player is usable on low-spec Android hardware"*; FR-18: *"The Player performs acceptably on low-spec Android devices."*
- **Why it matters:** "Usable" and "acceptably" on an unspecified device class are vacuous. No reference device profile (RAM, CPU class, Android/browser version), no measurable proxy (time-to-interactive, minimum frame rate, memory ceiling), no explicit statement of who sets one. FR-18 defers *asset size budgets* to architecture — fine — but performance *acceptability* is a product bar, and project-context §7's CI profile ("throttled CPU, constrained memory") is equally numberless, so nothing downstream supplies the answer either. Every performance acceptance criterion in the Player epic will be improvised, and SM-level claims about the primary consumer experience are unfalsifiable.
- **Suggested fix:** Pin a reference device/browser profile and one or two measurable acceptability proxies in NFR-2 (making an existing requirement testable, not new scope), or add an explicit OQ assigning that definition to the stakeholder before the Player epic.

### H-11. Schema evolution is half-specified: unknown Block types are handled, unknown schema *versions* are not, and "playable forever" is never reduced to testable MVP obligations

- **Location:** §4.1 FR-2; §1.1 I-3; §5 NFR-4
- **Quote:** FR-2: *"Players ignore unknown Block types gracefully; Published Versions remain playable forever."*
- **Why it matters:** What does a v1.0 Player do when handed a Lesson Script declaring `"schema": "1.1"` or `"2.0"`? Refuse? Best-effort render? The forward-compatibility FR covers unknown *Blocks* but not version mismatch — the more fundamental case, and the one the keystone-schema stories must encode from day one. Meanwhile "forever" and "after any later schema version ships" are untestable in an MVP that ships exactly one schema version; without concrete proxies (fixture scripts with unknown blocks and future version stamps in CI), FR-2's acceptance criteria are promissory notes.
- **Suggested fix:** Specify version-mismatch behavior at capability level (e.g., minor versions render with unknown fields ignored; major mismatch yields a defined "cannot play" state, never silent corruption) and restate "forever" as its testable MVP consequences.

---

## MEDIUM

### M-1. Budget Ceiling has no period, no reset semantics, no mid-flight rule, and no failed-job accounting

- **Location:** §3 Glossary; §4.7 FR-26; §2.3 UJ-4
- **Quote:** Glossary: *"Budget Ceiling — a per-Tenant monetary cap on LLM spend, enforced by the platform"*; UJ-4: *"a Tenant exhausts its monthly budget."*
- **Why it matters:** "Monthly" appears only in a journey edge case, never in the Glossary or FR-26 — cap-per-what-window is undefined, so enforcement is untestable. Also unspecified: what happens to a multi-call Generation Job in flight when the ceiling is crossed mid-run (kill = wasted spend and a failed job; complete = overrun), and whether failed jobs consume generation Quota and Budget. Every enforcement story needs these answers.
- **Suggested fix:** Define the period/reset in the Glossary, and add mid-flight and failed-job accounting semantics to FR-26 or OQ-9.

### M-2. Cache-hit vs. rate-limit interaction is unspecified — and UJ-3's wording implies cached hits burn the Student's limit

- **Location:** §4.5 FR-21; §2.3 UJ-3
- **Quote:** UJ-3: *"caches it, and renders it — within her per-Student rate limit."*
- **Why it matters:** Do zero-cost cache hits count against the per-Student rate limit? If yes, SM-C3's denial rate inflates on requests that cost nothing (throttling students out of a headline feature — the exact failure SM-C3 watches). If no, the limit only guards LLM spend and the ordering (rate-limit check vs. cache check) must say so. FR-21 fixes cache-before-LLM but not limit-vs-cache ordering; the story will guess.
- **Suggested fix:** State whether rate limits apply to cache hits (recommend: no, limits guard spend) in FR-21; fold defaults into OQ-2.

### M-3. There is no correction path for a bad cached diagram — the only unreviewed channel is also the only uncorrectable one

- **Location:** §4.5 FR-21; §1.1 I-2; §2.3 UJ-3
- **Quote:** UJ-3: *"A classmate requesting the same diagram minutes later gets the cached result instantly."*
- **Why it matters:** Sanitisation guards against script injection, not wrongness. An inaccurate labelled diagram (the feature's whole value claim is "accurate") gets cached Tenant-wide and served to every subsequent requester at zero cost — an error amplifier in the one channel that bypasses the Review Gate, with no Teacher/Operator purge, report, or expiry capability anywhere in the FRs. The brief is silent, so this is an OQ, not scope — but the PRD should have raised it.
- **Suggested fix:** Add an OQ: is a cache-entry purge/report mechanism (or TTL) required for MVP, and who wields it?

### M-4. Citation integrity under editing is unaddressed — FR-1 promises Citations "survive publish unchanged" while FR-10 lets Teachers rewrite the content they cite

- **Location:** §4.1 FR-1; §4.2 FR-6; §4.3 FR-10
- **Quote:** FR-1: *"Citations are representable in the Lesson Script and survive publish unchanged."*
- **Why it matters:** A Teacher substantially rewrites a Block's text; its Citation now attributes Teacher prose to a Grounding Chunk that no longer grounds it. Are Citations per-Block or per-Lesson? Removed with a deleted Block? Editable? Invalidated by edits? The grounding story ("content traceable to Corpus") quietly degrades to "content *originally derived* from Corpus" after any edit, and nothing says which claim the product makes. Schema and editing stories both need the answer.
- **Suggested fix:** State Citation granularity and edit semantics at capability level (per-Block recommended; edits preserve Citations as provenance-of-generation, documented as such), or add to OQ-10's remit.

### M-5. SM-4's "near-zero marginal cost per Student replay" is unmeasurable by its own stated instrument — and trivially true by design

- **Location:** §10 SM-4; §4.7 FR-27
- **Quote:** SM-4: *"near-zero marginal cost per Student replay. Validates FR-7, FR-27; measured from Cost Telemetry alone."*
- **Why it matters:** Replay involves no LLM calls by design (I-1), so Cost Telemetry — a per-LLM-call record — contains nothing about replay. The claim is either vacuous (absence of telemetry = zero cost, always passes) or unmeasurable (bandwidth/storage/serving costs aren't captured). Similarly "fully-loaded generation cost per Lesson" never says whether failed jobs, discarded Drafts, and regenerations amortise into the per-Lesson figure — the honest number and the flattering number differ severalfold, and the metric owner will pick the flattering one.
- **Suggested fix:** Define "fully-loaded" (recommend: all Generation Job spend for the Lesson, including failures and regenerations, divided by Published Versions) and restate the replay claim as the structural assertion it is (no LLM calls on the replay path — testable), not a measured cost.

### M-6. SM-3's "100%" target contradicts FR-23's own expected-failure-and-retry design

- **Location:** §10 SM-3; §4.6 FR-23
- **Quote:** SM-3: *"functioning for 100% of Published Versions placed in courses"*; FR-23: *"Writeback failures are logged as Structured Events and are retriable without Student rework."*
- **Why it matters:** The FR anticipates transient writeback failures (Moodle outages, network) and mandates retriability; the metric demands 100% with no time bound or eventual-consistency definition. Read literally, one transient failure breaches a primary success metric; read charitably, "functioning" means "capability works," which is a different (and near-vacuous) metric. Downstream QA will not know which to test.
- **Suggested fix:** Restate SM-3 as eventual success within a defined window (e.g., "100% of scores/completions durably recorded, with retries, within N hours"), keeping the 100% intent testable.

### M-7. All three counter-metrics lack thresholds or response rules — "watch this number" with no trigger is not load-bearing

- **Location:** §10 SM-C1–SM-C3
- **Quote:** §10: *"counter-metrics are as load-bearing as primaries"*; SM-C1: *"Should not trend toward zero."*
- **Why it matters:** No counter-metric has a target, alert threshold, or defined consequence when it moves the wrong way. "Should not trend toward zero" is undetectable without a floor; SM-C2 has no minimum richness share; SM-C3 no acceptable denial ceiling. A metric with no trigger cannot counterbalance anything — the primaries will be optimized and the counters narrated away.
- **Suggested fix:** Attach a provisional threshold or explicit review trigger to each (values can be stakeholder-set alongside OQ-1/OQ-2).

### M-8. SM-1 is median-only with no load context, and queue-time inclusion is implicit — a metric begging to be gamed by definition

- **Location:** §10 SM-1; §5 NFR-1; §4.2 FR-8
- **Quote:** SM-1: *"Median time from Teacher initiation to 'Draft ready for review' — under 5 minutes."*
- **Why it matters:** FR-8 makes generation queued; under contention across ~60 Tenants, queue wait can dominate. "From Teacher initiation" *should* include queueing, but nothing says so explicitly, and the tempting implementation measures job-start→completion. Median alone hides a brutal tail (half of Teachers may wait arbitrarily long while the metric glows green). No stated load assumption makes the target untestable pre-launch.
- **Suggested fix:** State explicitly that the clock starts at request submission (queue included), add a tail percentile (e.g., p90), and note the assumed concurrency envelope for the target.

### M-9. Narration's chosen mechanism is weakest on the primary consumer's device class, and §11 doesn't carry the risk

- **Location:** §4.4 FR-14; §2.3 UJ-2; §11 Risks
- **Quote:** UJ-2: *"he steps through slides with narration (browser speech synthesis)."*
- **Why it matters:** SpeechSynthesis support on low-end Android browsers/WebViews is patchy — often absent, voice-less, or dependent on online TTS services. The happy-path journey showcases narration on exactly the device class where it is least likely to work; the graceful-degradation consequence (A-9) exists, but §11's device-performance risk covers only 3D/Simulations. If narration is effectively text for most of the target population, that is a product-experience fact the stakeholder should see stated, not discover.
- **Suggested fix:** Extend §11's device risk to name narration availability on low-spec Android, with A-9's text fallback as the stated mitigation.

### M-10. The assumption-confirmation process is undefined and inconsistently applied — A-14 strengthens scope beyond the brief with no OQ behind it

- **Location:** §13 Assumptions Index; §0; §12
- **Quote:** A-14: *"toggling takes effect without redeploying (a strengthening beyond the brief's bare 'feature flags')."*
- **Why it matters:** §0 declares scope changes "in either direction" need explicit confirmation, and §13 says assumptions are "surfaced for explicit confirmation" — but only some assumptions map to OQs (A-3→OQ-9, A-6→OQ-10…), while others that also bind downstream work (A-11, A-12, A-13, A-14) have no confirmation vehicle at all. A-14 even self-identifies as a scope strengthening, which by the document's own rule requires stakeholder sign-off it never requests. Eighteen assumptions with no owner, mechanism, or deadline will simply harden into requirements by default.
- **Suggested fix:** Give the Assumptions Index a disposition column (confirmed / pending-OQ-n / accepted-by-default-on-date) and route the self-declared strengthening (A-14) through an explicit OQ.

### M-11. FR-26 requires per-user rate limits on "all LLM-spending actions" but its configuration list doesn't include them — who sets the Teacher's limit, and where?

- **Location:** §4.7 FR-26
- **Quote:** Consequence: *"Per-user rate limits are enforceable at the platform layer for all LLM-spending actions — not only Diagram Requests"*; FR body: *"configure, per Tenant: LLM Budget Ceilings, generation Quotas, diagram Quotas, and feature flags."*
- **Why it matters:** The consequence introduces per-Teacher generation throttling as a testable requirement, but the Operator-configurable surface in the same FR omits per-user limits (project-context §4 says "enforceable," which is a capability, not a configured policy). Is there a default? Operator-set? Hardcoded? The quota story cannot define its config schema from this FR.
- **Suggested fix:** Either add per-user rate limits to FR-26's configurable list or state they are platform defaults not exposed to the Operator in MVP; fold values into OQ-2.

### M-12. No latency expectation exists for Diagram Requests — the only interactive LLM feature has no performance requirement at all

- **Location:** §4.5; §5 NFRs; §2.3 UJ-3
- **Quote:** UJ-3: *"generates an SVG grounded in the Tenant corpus, sanitises it, caches it, and renders it"* — with no time bound anywhere.
- **Why it matters:** NFR-1 covers generation (5 min), NFR-2 covers playback; the cache-miss diagram path (retrieval + LLM + sanitisation, synchronous in a chat) has nothing. A 60-second in-chat wait versus a 5-second one is the difference between a headline feature and an abandoned one, and no story will inherit a target. The brief is silent, so this is an OQ, not scope.
- **Suggested fix:** Add to OQ-2 a cache-miss latency expectation for Diagram Requests (or an explicit stakeholder decision that MVP sets none).

---

## LOW

### L-1. §0's derivation claim contradicts the document's own citations

- **Location:** §0; §5; §6; §10; §11
- **Quote:** §0: *"derived strictly from the Product Brief (…, §5–§7)"* — yet SMs cite brief §4, integrations cite §8, NFRs cite §9 and §11.
- **Why it matters:** The scope *fence* is §5–§7 (brief §12.2); the document demonstrably draws context from §1–§12. A pedantic downstream validator (or the next reconciliation run) can flag the mismatch between the claim and the citations.
- **Suggested fix:** Reword §0: FR scope derives strictly from §5–§7; metrics, constraints, and context derive from the brief at large.

### L-2. The Glossary defines "Regeneration" conditionally, pending OQ-3, in a regime where downstream must use terms verbatim

- **Location:** §3 Glossary; §12 OQ-3
- **Quote:** *"Regeneration — an explicit Teacher action that re-runs generation for a Lesson (or, if committed to scope, a single Block)."*
- **Why it matters:** A glossary entry containing an unresolved scope fork exports the ambiguity to every consumer of the term. Minor now; annoying in every downstream doc until OQ-3 resolves.
- **Suggested fix:** Define the term for the committed scope only and note the OQ-3 extension outside the definition.

### L-3. The Glossary's "Published Version" entry states an absolute that its own cited invariant carves an exception into

- **Location:** §3 Glossary; §1.1 I-2
- **Quote:** *"the only lesson content Students can ever receive (I-2)"* — while I-2 itself excepts sanitised diagrams.
- **Why it matters:** Diagrams arguably aren't "lesson content," but the entry cites I-2, whose text carries the exception; a literal reader gets two different absolutes from the same reference. Cheap to harden.
- **Suggested fix:** Append "(the I-2 diagram exception is chat content, not lesson content)" or drop the "(I-2)" cite from the superlative.

### L-4. FR-5 prescribes pipeline staging in a document that declares itself capabilities-only

- **Location:** §4 intro; §4.2 FR-5
- **Quote:** §4 intro: *"Capabilities only — technology choices live in `project-context.md` and `addendum.md`"*; FR-5: *"staged orchestration: lesson plan → per-Block content → validation."*
- **Why it matters:** The staging is *how*, not *what* (it's inherited from brief §5.2, so it's faithful — but the PRD's own framing rule says such depth belongs in the addendum, where pipeline design is indeed already listed on the ADR agenda). Small self-inconsistency that invites the Architect to treat PRD text as binding design.
- **Suggested fix:** Soften FR-5 to the capability ("produces a validated, schema-conforming script via a multi-stage pipeline") and leave stage naming to the addendum.

### L-5. FR-3's documentation-sufficiency consequence is unmeasurable as an acceptance criterion

- **Location:** §4.1 FR-3
- **Quote:** *"The package's documentation is sufficient for a renderer author to implement each Block type without reading pipeline code."*
- **Why it matters:** "Sufficient" has no test. The intent is right; the criterion will be checked by vibes.
- **Suggested fix:** Anchor it to an observable proxy (e.g., the Player implements every Block type against the schema package's docs alone — which the build itself can demonstrate).

### L-6. NFR-8's "localisation-ready text handling" is undefined and conflates UI chrome with generated content

- **Location:** §5 NFR-8
- **Quote:** *"English-language content at launch with localisation-ready text handling."*
- **Why it matters:** Localisation-readiness of the Authoring UI/Player chrome (string externalisation) and of AI-generated lesson content (a generation-pipeline property) are entirely different problems; the NFR names neither and defines readiness for neither. As written it will be checked off by whoever feels ready.
- **Suggested fix:** State which surfaces the NFR covers and the minimal testable bar (e.g., no hardcoded user-facing strings in UI code), deferring content localisation explicitly to roadmap.

---

## Summary

| Severity | Count |
|---|---|
| Critical | 3 |
| High | 11 |
| Medium | 12 |
| Low | 6 |
| **Total** | **32** |

**Bottom line:** The PRD's skeleton — invariants, glossary discipline, traceability, counter-metrics, assumption indexing — is genuinely above average, which makes the residual holes more dangerous, not less: downstream agents will trust this document. Do not release it to architecture/epics until C-1 through C-3 are resolved and the high-severity semantic gaps (completion, editing surface, SM-2 denominator, low-spec definition) have owners. None of the fixes requires new scope; nearly all are definitions, decisions, or open questions the stakeholder must be shown rather than shielded from.
