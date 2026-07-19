# Accessibility Review — e-DON Lesson Studio UX Spines (Adversarial)

**Reviewed:** `DESIGN.md`, `EXPERIENCE.md` (2026-07-16) against `prd.md` (2026-07-07). Reviewer lens: WCAG 2.1 AA (the spines' own recommendation for OQ-7), screen reader, keyboard/switch, low-vision/zoom, cognitive, vestibular — on Android 8-era student hardware.

## Verdict

The pragmatic floor is better than most MVP floors — transcripts as real text, poster fallbacks with full text alternatives, glyph+text paired with color, no autoplay, no hover-only affordances, reorder buttons beside drag. The contrast arithmetic in `DESIGN.md § Colors` was independently recomputed and **every listed pair genuinely passes AA** (details in F-15). But the floor is not AA-adequate as written, and its weakest points are exactly where the product's identity lives: **there is no text-alternative contract anywhere for the AI-generated visual content that is the product's point** — a gap baked into a schema advertised as playable forever (I-3) — and the floor's two boldest claims (simulation keyboard access "enforced via pre-publish checks", diagram "labels legible at phone width") are assertions with no mechanism behind them. The color system's own rule ("gold never carries meaning on light surfaces") is violated twice by the design's own components. Adopting WCAG 2.1 AA at OQ-7 will not close these; they need explicit spec changes, and one needs a schema field before v1.0 freezes.

**Counts:** 1 critical · 5 high · 7 medium · 4 low.

## Findings

### [critical] F-1 — No text-alternative contract for AI-generated visual content; the omission is schema-shaped and permanent

**Location:** `DESIGN.md § Components` (Diagram block, Poster fallback card, Model3D viewer, Diagram chat message); `EXPERIENCE.md § Accessibility Floor`; PRD FR-1/FR-20, `project-context.md §4` allowlist.
The floor requires text alternatives for *simulation poster fallbacks* only. Nothing anywhere requires:
- **alt text / accessible name for lesson Diagram SVGs** — the Diagram block spec covers frame, radius, caption typography; never a text alternative. A caption is not an alternative for a labelled technical diagram.
- **alt text for posters** (Model3D and Simulation full-tier state, where the annotations panel is behind a tap).
- **survival of SVG accessibility markup through Sanitisation.** Sanitisation is allowlist-based: anything not allowlisted is stripped. If `<title>`, `<desc>`, `role`, `aria-label`, `aria-labelledby` are not explicitly on the allowlist, the sanitiser itself will strip whatever accessibility the LLM happened to emit. No document mentions them.

Blind and low-vision students get unlabeled graphics in the one channel that *bypasses the Review Gate* (chat diagrams, FR-28) and in reviewed lesson diagrams alike. Worse: Lesson Script Schema v1.0 is the keystone contract, immutable and "playable forever" (I-3, FR-2). Shipping v1.0 without alternative-text fields means every early Published Version is inaccessible *forever*, and adding the field later is a schema version event.
**Fix:** (1) Add required `altText`/`longDescription` fields to Diagram, Model3D (poster), and Simulation (poster) Block schemas before v1.0 freezes; (2) generation contract must produce them from the same Grounding Chunks; (3) expose them as editable text in the Block editor (extend the A-28 editability map — they are text, not SVG); (4) explicitly allowlist `<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby` in Sanitisation; (5) chat diagram accessible name = FR-28 label + the student's request text + generated description (the floor's "label is part of the accessible name" covers only the label — the label describes provenance, not content).

### [high] F-2 — Quiz instant feedback is silent to screen readers, and the correct-answer reveal is color/border-only

**Location:** `EXPERIENCE.md § Accessibility Floor` (aria-live list) + `§ Component Patterns → Quiz block`; `DESIGN.md § Components → Quiz block`.
The floor's `aria-live` list names generation progress, score sync, and regeneration — **not per-question quiz feedback**, the single most frequent state change a Student experiences and the pedagogical payload of FR-15. A screen-reader user selects an option and hears nothing. Additionally, after an incorrect answer "the correct answer [is] then outlined in `{colors.primary}`" — an outline is color/border only, no glyph, no text: a direct WCAG 1.4.1 failure inside the one component the design otherwise got right (✓/✗ glyphs on the *chosen* option).
**Fix:** Add per-question feedback to the aria-live inventory (or `role="status"` on the feedback text, `aria-describedby` from the option); give the revealed correct answer a glyph + "Correct answer" text prefix, not just an outline; specify that feedback text is programmatically associated with the question group.

### [high] F-3 — Block navigation swaps content in place with no focus management or announcement spec

**Location:** `EXPERIENCE.md § Component Patterns → Player shell`; `§ Moodle Embedding Contract` ("block navigation changes content in place").
One Block on screen at a time; Next/Back replace the content region. Nothing specifies where focus goes or what is announced. A screen-reader user presses Next and perceives nothing — the page didn't navigate, the live regions listed in the floor don't cover it, and focus is still parked on the Next button next to content they don't know has changed. This makes linear playback — the Player's whole job (FR-13) — effectively unusable non-visually.
**Fix:** Specify in the Player shell pattern: on block change, move focus to the new block's heading (`tabindex="-1"`) or announce "Block n of N — {block title}" via the existing live region; give the progress header a programmatic reading ("Block 3 of 9", not just visual fill); make the block heading a real heading element so SR users can navigate within the block.

### [high] F-4 — Simulation keyboard accessibility is "enforced" by checks that don't check it

**Location:** `EXPERIENCE.md § Accessibility Floor` (bullet 1) vs PRD FR-17/A-35.
The floor claims keyboard adjustability of simulation parameters is "a requirement on the generation prompt contract **enforced via the FR-17/A-35 pre-publish checks**". A-35's minimum check list is: loads without error, honors postMessage, exposes authored parameters, respects resource budget. **No keyboard check exists.** A prompt-contract line with no verification is a hope, not a floor — and LLM-generated code is precisely the code that will violate it (custom-painted sliders, div-buttons). Simulations are also the highest-variance MVP feature per PRD §11. Inside the sandbox, focus visibility and control contrast are equally ungoverned.
**Fix:** A-35 says "extend, do not narrow" — extend it: automated check that every declared parameter maps to a native form control (or has keyboard handlers + focusable role), asserted via the postMessage protocol or static DOM inspection inside the check harness; require native `<input type="range">`/`<input>`/`<button>` in the generation contract (cheap to check, cheap for old WebViews); add "operate the simulation by keyboard" to the Teacher preview guidance. The poster path's parameter-description text remains the last-resort equivalent — say so explicitly.

### [high] F-5 — "Labels legible at phone width" and "pinch zoom native" are outcomes with no mechanism; the embedding contract can forbid the only recourse

**Location:** `EXPERIENCE.md § Component Patterns → Diagram block`, `§ Key Flows → Flow 3 step 2`, `§ Moodle Embedding Contract`; `DESIGN.md § Components → Diagram block`.
An SVG technical diagram authored at unknown intrinsic size scales to a ~328px content column on a phone. Label legibility at that width is asserted in Flow 3 as if it were a property of the system; no requirement produces it — no minimum label font-size in the diagram generation contract, no legibility check, nothing at the Review Gate (Teachers preview at Phone 360, but chat diagrams never pass a Teacher). The claimed recourse, "pinch/browser zoom native", is **host-controlled**: the viewport meta tag belongs to the Moodle theme, and the Player is contractually barred from overriding page styles or opening overlays that escape its container. If an institution's theme sets `user-scalable=no`, low-vision students have a diagram they cannot read and cannot zoom — WCAG 1.4.4 failure with no owner.
**Fix:** (1) Minimum rendered label size rule in the diagram generation/validation contract (e.g., labels ≥ 12px at 360px container width — testable at sanitisation time from font-size/viewBox math); (2) an in-container enlarge affordance (diagram expands to full container width / rotates, or opens the raw sanitised SVG in a new tab — a link, not an overlay, so the embedding contract survives); (3) mod_edonlesson must guarantee `user-scalable=yes` on pages it controls, stated as an integration requirement.

### [high] F-6 — The diagram chat message is a third surface the accessibility floor forgot; its governance control is a 12px text button

**Location:** `EXPERIENCE.md § Accessibility Floor` ("both surfaces"), `§ Foundation` (three surfaces); `DESIGN.md § Components → Diagram chat message` ("Report this diagram" quiet-destructive text button, `{typography.caption}` = 12px).
The floor's keyboard rule covers "both surfaces" and its target-size rule names Player (≥48px) and authoring (≥44px). The Foundation section counts **three** user-facing surfaces. The diagram chat message — the only surface where AI content reaches Students unreviewed — inherits no keyboard rule, no target-size rule, and its safety valve, the FR-28 report control, is specified as 12px caption-sized text in a caption row. On the phones this product targets, that is an unhittable target for anyone with a motor impairment and invisible to anyone with low vision. The governance loop (label → report → review) only works if reporting is operable.
**Fix:** Extend the floor's scope line to name all three surfaces; give the report control a ≥44px hit area and ≥14px label; specify keyboard focus order and the accessible name for the diagram card within the chat message; state that the "generating"/quota/failure chat replies are announced by the chat's existing live region (or add one).

### [medium] F-7 — The design violates its own "gold never carries meaning on light surfaces" rule twice

**Location:** `DESIGN.md § Colors` (gold rule) vs `§ Components → Regenerate control`; `EXPERIENCE.md § Component Patterns → Block rail` (unseen gold dot).
Computed: gold `#FFB81C` is 1.73:1 on white, 1.61:1 on surface-subtle, 1.57:1 on its own gold-wash. The design correctly bans it as meaning-carrying text/hairline — then ships: (a) the **Regenerate control's 1px gold border** (1.57:1 against its wash fill), whose *working state* is "gold border animates to a sweep" — a state change carried by a sub-2:1 element (label swap to "Regenerating…" is the real signal; the spec should say so and not pretend the sweep communicates); (b) the **session-local "unseen" gold dot** on rail items — a meaning-carrying gold mark at 1.73:1 on white, failing WCAG 1.4.11's 3:1, with **no screen-reader equivalent specified at all**. UJ-1 step 4 leans on these dots for review completeness — the Review Gate's integrity cue is invisible to low-vision Teachers and nonexistent for blind ones.
**Fix:** Give the dot an `{colors.accent-ink}` or ink outline (or use accent-ink as the dot color) and an accessible state ("not yet opened this session") on the rail item; demote the sweep to decorative in the spec and name the label swap as the accessible state signal; either thicken the regenerate border with accent-ink or accept the wash+ink text as the control's identity and say so.

### [medium] F-8 — Secondary/quiet button boundaries fail non-text contrast

**Location:** `DESIGN.md § Components → Button set`; `border-strong` token.
Computed: `#AFBDB6` on white = **1.95:1** — the secondary button's only boundary is well under the 3:1 of WCAG 1.4.11. The green label (6.84:1) identifies the control's presence, but the boundary defines its hit area, and quiet buttons have neither border nor fill. In an authoring UI for moderate-digital-literacy users, "what is clickable" should not depend on inference.
**Fix:** Darken `border-strong` to ≥3:1 vs white (≈ `#7E8C85` territory) for control boundaries, or accept text-identifies-control explicitly and require it (min 44px padding preserved); do not use `border-strong` as the sole boundary of anything interactive.

### [medium] F-9 — Preview overlay: no focus trap, initial focus, or restore spec

**Location:** `EXPERIENCE.md § Component Patterns → Preview overlay`, `§ Interaction Primitives`; `DESIGN.md § Components → Preview overlay`.
The full-screen overlay hosts the real Player, a device-width toggle, Low-spec toggle, and Close. `Esc` closing is specified; focus trapping, initial focus target, and focus restore to the invoking "Preview" button are not. Untrapped, Tab walks into the obscured workspace behind the scrim — disorienting for SR and keyboard users alike. Same gap applies to the Publish dialog.
**Fix:** One overlay rule in Interaction Primitives: overlays trap Tab, focus moves to the overlay title on open, returns to the invoker on close. Three sentences; costs nothing.

### [medium] F-10 — Three-pane workspace has no landmark or skip structure; the rail is a keyboard slog

**Location:** `EXPERIENCE.md § Responsive & Platform`, `§ Accessibility Floor` ("Tab order = reading order"); `DESIGN.md § Layout & Spacing`.
"Tab order = reading order" in a rail/editor/citations layout means a keyboard user tabs through every rail item — each with select + up + down controls (11 blocks ≈ 33 stops) — before reaching the editor, on every trip. No landmarks, no skip link, no roving-tabindex/listbox pattern for the rail is specified.
**Fix:** Name the panes as landmarks (`navigation` / `main` / `complementary`); make the rail one tab stop with arrow-key traversal and documented reorder keys (e.g., Ctrl+Arrow) — the "up/down buttons on focused item" already implies focus management, so specify it; add a skip-to-editor link.

### [medium] F-11 — Model3D: orbit has no non-drag equivalent and annotation markers are sub-target-size

**Location:** `EXPERIENCE.md § Interaction Primitives` ("everything the canvas does is also available as buttons (zoom ±, reset view)"), `§ Component Patterns → Model3D viewer`; `DESIGN.md § Components → Model3D viewer` (24px markers).
The claim "everything the canvas does is also available as buttons" is contradicted by its own parenthetical: zoom and reset get buttons; **orbit — the point of a 3D model — is drag-only**. Keyboard and switch users cannot rotate. And the numbered annotation markers are 24px dots in a Player whose own floor mandates ≥48px touch targets.
**Fix:** Rotate left/right/up/down buttons (or arrow keys on the focused canvas — canvas must be focusable with a role and name); 48px hit areas on markers (visual dot can stay 24px); guarantee the annotation text panel is toggleable from the button row, not only via markers. The Constrained-tier annotations-as-text-list already exists — offer it on Full tier too.

### [medium] F-12 — No reduced-motion consideration anywhere

**Location:** `DESIGN.md` (whole document), `EXPERIENCE.md § Interaction Primitives` (banned list omits it).
The system animates: the regenerate border sweep (indeterminate, persists for the duration of a regeneration), progress fills, skeleton loaders, generation progress bar. Not one line honors `prefers-reduced-motion`. The banned-everywhere list was the natural home and it isn't there.
**Fix:** One global rule: under `prefers-reduced-motion: reduce`, replace sweeps/shimmers with static state changes and progress animation with stepped updates. Note the old-WebView bonus: less animation is also cheaper on the device floor.

### [medium] F-13 — 12px caption is load-bearing, against the design's own 14px minimum

**Location:** `DESIGN.md § Typography` ("Minimum rendered body size anywhere: 14px") vs `§ Components`: AI content label (caption), poster caption one-line explanation (caption), block counter (caption), diagram caption (caption), citation excerpts (caption).
The 14px floor is evaded by classifying meaning-bearing text as "caption". The FR-28 AI-provenance label — governance-critical, "never truncated" — renders at 12px system font on a phone. The poster explanation that must let the poster "stand alone pedagogically" is 12px. These are content, not metadata.
**Fix:** Re-tier: AI content label, poster explanations, and quiz feedback ≥14px; keep 12px only for genuine metadata (dates, chunk IDs, version counts).

### [medium] F-14 — Cognitive traps for moderate-digital-literacy Teachers: three overlapping review-state signals, two "Regenerate" verbs, and an unannounced reroute

**Location:** `EXPERIENCE.md § Component Patterns → Status chip / Block rail / Generate form`; `§ State Patterns → Identical request while Draft exists`.
(a) A Block can simultaneously show a "Needs review" chip, a session-local gold unseen dot, and later "Edited" — with no stated rule for when "Needs review" clears (on open? on edit? ever?). Ambiguity here feeds exactly the rubber-stamp risk SM-C1 watches for. (b) "Regenerate" on a Block and "Regenerate lesson" on the same screen differ by one word and by total blast radius. (c) The FR-7 idempotency reroute silently lands the Teacher on an existing Draft with only a dismissible banner — visually surprising, and for SR users the route change is unannounced (the floor's live-region list doesn't include it).
**Fix:** Define the "Needs review" chip lifecycle in the Status chip row; rename whole-lesson action "Regenerate entire lesson…" with a confirm that names the Block count being replaced; add the idempotency banner to the aria-live inventory and move focus to it on reroute.

### [low] F-15 — Contrast claims verified; one rounds generously

**Location:** `DESIGN.md § Colors`.
Recomputed: primary/white **6.84:1** (claimed 6.9 — overstated by rounding; still comfortably AA), accent-ink/gold **7.61:1** ✓, accent-ink/gold-wash **11.95:1** ✓, ink-secondary/white **6.68:1** ✓, primary-deep/green-wash **8.68:1** ✓, error/white **6.46:1** ✓, error/error-wash **5.67:1** ✓, gold/white **1.73:1** (correctly banned). Progress fill vs track 5.32:1 ✓ (>3:1). All listed text pairs pass AA both as stated and in adjacent wash combinations checked. **Fix:** State 6.8:1; a document that stakes its credibility on computed ratios shouldn't round up.

### [low] F-16 — Unknown-Block omission (FR-2): visual and announced counts are consistent, but two edges are unspecified

**Location:** `EXPERIENCE.md § State Patterns → Unknown Block type`, `§ Component Patterns → Player shell`.
Verified: omitting unknown Blocks from both the sequence *and* the "Block n of N" count means no visual-vs-announced mismatch — good design. Remaining gaps: (a) the progress header "marks viewed Blocks and Blocks still needing action" — those marks have no specified text/AT equivalent; (b) the all-Blocks-unknown edge ("Block 0 of 0") is undefined — should render the major-version-mismatch can't-play state, not an empty player; (c) server-authoritative completion must count the *same renderable set as the Student's Player version*, or a Student on an older Player can view everything renderable and never complete — cross-reference to architecture.
**Fix:** Give header marks an accessible list equivalent ("Viewed 4 of 9; Quiz in Block 6 not yet submitted" — the completion summary already has this pattern; reuse it); define the zero-renderable edge; flag (c) to architecture.

### [low] F-17 — Language attributes unspecified despite NFR-8 doing the hard part

**Location:** `EXPERIENCE.md § Voice and Tone`; PRD NFR-8 (Lesson Script text fields carry a language tag).
The schema carries language tags; nothing says the Player or chat diagram card sets `lang` on rendered content regions. Free win for screen-reader pronunciation, and future-proof for the localisation roadmap.
**Fix:** One line: Player content regions and diagram cards set `lang` from the script's language tag.

### [low] F-18 — Small ARIA-state and live-region hygiene gaps

**Location:** `EXPERIENCE.md § Component Patterns` (Narration control, Generation progress card, Budget pause).
(a) "Show text" and Low-spec toggles need stated pressed/expanded state semantics. (b) The generation progress card's *elapsed time* must be excluded from its live region or it announces every tick. (c) During a budget pause the Generate form is disabled — disabled controls are skipped by AT; the persistent banner must precede the form in DOM order or be referenced from it so the *reason* is discoverable. (d) SpeechSynthesis narration will speak over a running screen reader — no fix required (never autoplays, transcript is equivalent), but the spec should acknowledge the interaction so support staff aren't surprised.
**Fix:** One hygiene paragraph in the Accessibility Floor covering toggle states, live-region exclusions, and disabled-with-reason association.
