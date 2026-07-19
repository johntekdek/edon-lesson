---
name: e-DON Lesson Studio
status: final
sources:
  - _bmad-output/planning-artifacts/prds/prd-2027_edon_sim_pro-2026-07-07/prd.md
  - _bmad-output/planning-artifacts/prds/prd-2027_edon_sim_pro-2026-07-07/addendum.md
  - _bmad-output/planning-artifacts/edon-lesson-studio-product-brief.md
  - _bmad-output/project-context.md
updated: 2026-07-18
---

# e-DON Lesson Studio — Experience Spine

> Paired with `DESIGN.md` (visual identity; token references `{path.to.token}` resolve there). Spines win on conflict with any mock or import. Vocabulary follows the PRD Glossary (§3) verbatim throughout.

## Foundation

Three user-facing surfaces, one visual identity, sharply different constraints:

1. **Authoring UI** — a Teacher-facing React (JSX, no TypeScript — `project-context.md` §2 [HARD]) web application. Reached **only** via Moodle-initiated launch: mod_edonlesson mints a signed, short-lived Launch Token carrying Tenant, user ID, role, and course reference (FR-29). There is no login screen, no course picker, and no standalone URL worth bookmarking. Desktop-first workspace; functional down to phone width. The launch opens the Authoring UI in a new browser tab, keeping the Moodle course tab intact (confirmed by stakeholder, 2026-07-17).
2. **Player** — a self-contained embeddable JavaScript bundle (script + mount API, no host framework) rendering Published Versions inside Moodle activity pages and Drafts inside the Authoring UI's Preview overlay (FR-9: same Player, same script). Governed by a strict bundle budget with lazy-chunk discipline. Device posture (stakeholder realignment, 2026-07-18 — Amendment F, § Rulings & Open Items): **modern smartphones with reliable connectivity are the canonical audience; Showcase/Full is the default experience.** Brand fonts and motion ship as lazy chunks loaded post-first-paint as **standard** (never render-blocking, never counted against the core budget); the Floor tier survives as thin best-effort fallback.
3. **Diagram chat message** — a message-level component riding the existing block_edon_ai chat (OQ-12). The chat's own chrome is untouched; this spine specifies only the diagram message and its states.

No UI component library is mandated — that is an architecture decision (ADR territory); this spine and `DESIGN.md` are library-agnostic. The Operator surface is explicitly out of UX scope: minimal internal tooling, form owned by architecture (PRD A-2) — this consciously includes per-Tenant budget/quota configuration and the OQ-1 $2 soft-alert, which are Operator-side concerns with no Teacher/Student surface. Likewise deliberately excluded: Teachers monitor Student results in the Moodle gradebook they already use; MVP adds no in-product results surface (no-dashboard fence, PRD §8).

## Information Architecture

**Authoring UI** (all surfaces carry the launch Course Context; a chip in the header names the course at all times):

| Surface | Reached from | Purpose |
|---|---|---|
| Course home | Moodle launch (Launch Token) | Lessons for the launch course: the Teacher's own Drafts + the Tenant's Published Versions; start generation. A secondary **College library** tab lists the Tenant's Published Versions across courses, each with "Duplicate as my draft" — this realizes OQ-13's Tenant-wide visibility and is how a colleague finds a lesson from another course (confirmed by stakeholder, 2026-07-17). |
| Generate form | Course home "New lesson" | Topic + optional guidance → Generation Job (FR-4) |
| Review Workspace | Lesson card / "Draft ready" | Block-level review, edit, reorder, delete, regenerate; per-Block Citations (FR-6, FR-10) |
| Preview overlay | Review Workspace "Preview" | Faithful Student view via the real Player, incl. device-width and Low-spec view toggles (FR-9, A-27) |
| Publish dialog | Review Workspace "Publish" | Pre-publish checks + explicit immutable publication (FR-11, FR-17) |
| Diagram review queue | Course home header nav | Tenant-scoped triage of Student-reported chat diagrams (FR-28) |
| Relaunch notice | Any surface, expired/invalid Launch Token | Dead end with one instruction: relaunch from Moodle (FR-29) |

**Student surfaces** (inside the Moodle course; the Player never navigates away from the activity page):

| Surface | Reached from | Purpose |
|---|---|---|
| Player — block sequence | Moodle activity load (mod_edonlesson embed) | Linear playback of the Published Version's ordered Blocks (FR-13) |
| Player — Sources | Lesson end | Lesson-level Citations list (OQ-10 — no per-Block display for Students) |
| Player — completion summary | After last Block | Completion state, server-authoritative score status, attempts (FR-15, FR-23) |
| Diagram message | block_edon_ai chat | The Diagram Request surface: request and receive a governed, labelled SVG diagram (FR-19, FR-28) |

**Moodle-native surfaces** (thin, unbranded — they follow the institution's Moodle theme, not `DESIGN.md`):

| Surface | Reached from | Purpose |
|---|---|---|
| Lesson picker | Moodle "Add an activity" → mod_edonlesson settings | Pick a Published Version for this course; set completion options and quiz attempt limits — configured here, as Moodle teachers expect from other activity modules (FR-23/OQ-15; confirmed by stakeholder, 2026-07-17) |
| Authoring entry point | mod_edonlesson teacher view | "Open Lesson Studio" — mints the Launch Token (FR-29) |

Surface closure: every PRD user journey lands on these surfaces (UJ-1, UJ-5 → Authoring set; UJ-2 → Player set; UJ-3 → Diagram message; UJ-4 → Operator tooling, out of UX scope by A-2).

→ Composition references: `mockups/key-review-workspace.html` (Review Workspace + blocked Publish dialog), `mockups/key-player-mobile.html` (Player canonical + Floor-tier states inside Moodle chrome), `mockups/key-diagram-chat.html` (Diagram message + Quota state).

## Capability Tiers & Degradation Ladder

**Amended posture (stakeholder realignment 2026-07-18 — Amendment F; supersedes the OQ-16-derived posture):** Students are assumed on modern smartphones with reliable connectivity, and **Showcase/Full is the canonical, default experience** — the ladder below is inverted from a floor-first to a fallback ladder. The Floor and Constrained rungs are retained as **thin best-effort fallback** (they also serve feature-flag-off states and future offline export) but no longer gate launch, and the low-spec CI profile is advisory. Degraded states remain **designed states, not error states** — the poster path keeps its design quality; it is simply no longer the routine path.

| Tier | Detection (feature-based, never user-agent) | Model3D | Simulation | Narration |
|---|---|---|---|---|
| Showcase | Capable device + fast connection, auto-detected; any data-saver signal, metered hint, or detection uncertainty demotes — when unsure, demote (stakeholder amendment, 2026-07-17) | Auto-loads with the hero entrance (slow ~2s auto-orbit, settles; inside the reserved media box; skipped under `prefers-reduced-motion`) | Auto-loads to its ready state — sound and narration still start only on explicit action | Same as Full (brand webfonts are standard on all capable devices via the lazy fonts chunk, not Showcase-gated — re-amended 2026-07-18; `{typography.player-ui}`) |
| Full | WebGL available + asset within its per-Block budget | Auto-loads to the interactive viewer (poster is first paint); data-saver → "Load 3D model (size)" | Auto-loads to ready (poster first paint); data-saver → "Run simulation (size)" | Audio play control — pre-generated narration audio, SpeechSynthesis fallback — + "Show text" |
| Constrained | WebGL available; asset too heavy for the detected device class (definition architecture-owned) or load fails | Poster fallback card + annotations as text list | Poster first; run attempted; runtime failure → Poster fallback card | Same as Full |
| Floor | No WebGL / sandbox unable to run | Poster fallback card + annotations as text list | Poster fallback card + parameter description text | No usable voices → transcript shown by default, play control hidden |

Ladder rules:

- **Auto-load is the default everywhere** (re-amended by stakeholder, 2026-07-18 — reverses the earlier B6 ruling). Heavy assets (Model3D, Simulation) auto-load on every tier; the poster remains the instant first paint while the asset arrives, and any load failure lands on the normal Constrained behavior. **Tap-to-load (with the transfer-size label) applies only under explicit data-saver signals** (`saveData`, `prefers-reduced-data`, metered hints) — respect for constrained data survives as an opt-in state, not the default.
- **Showcase polish is standard, still never a dependency** (2026-07-18). Webfonts and motion ship as lazy chunks after first content paint on all capable devices — standard, never counted against the core bundle budget and never render-blocking; the system stack remains the fallback at every moment. Demotion is graceful mid-session: if the connection degrades, the next heavy Block simply behaves like Full. Motion never touches gold governance signals, and every animation respects `prefers-reduced-motion`. The Floor tier, poster paths, and durability rules are unchanged by this tier and remain first-class.
- **Completion is tier-independent.** A Block in its poster state counts as viewed; every Quiz Block works on every tier; the Floor tier can reach 100% completion (FR-18).
- **At most one heavy Block is live at a time.** Leaving a heavy Block releases it; it returns to its poster state (memory pressure on 1.5–2 GB devices makes two live heavy Blocks a tab crash). Returning and re-loading must not re-charge the Student's data for an asset already downloaded this session — cached re-load, no size re-prompt; if re-download is genuinely possible, the size label reappears honestly.
- **Posters are budgeted and lazy.** They auto-load (they *are* the universal path), so they carry their own per-image budget (value architecture-owned, CI-enforced with the other budgets) and load lazily as their Block approaches — never the whole lesson's posters up front. All size labels state *transfer* (compressed) size — that is what metered data charges.
- **Narration has a runtime-failure rung too.** If speech does not audibly start within a bounded time of tap, the control converts to the Floor state (transcript shown, control hidden) — quiet, never an error. "Usable voice" means an English-family voice that begins speaking when asked; voice preference follows the Lesson Script language tag (en-NG → en-GB → any English). "Show text" stays one tap away so a poor voice is never a trap.
- **The Teacher sees what the Floor sees.** The Preview overlay's Low-spec view toggle renders exactly the Floor-tier states (A-27), so degraded states pass through the Review Gate like everything else.
- **Posters derive from the content itself.** They are static images — pre-rendered views of the curated glTF asset, captures of the simulation, or SVG — selected/produced during generation and reviewed at the Review Gate. They are never AI-generated illustrative raster imagery (that fence stands, PRD §8); the production mechanism is architecture-owned. The caption names what the full asset shows so the poster stands alone pedagogically.

## Moodle Embedding Contract

What "feels native to Moodle" means, behaviorally (FR-22, A-12):

- The Player mounts into the activity page's content region and **inherits the page's scroll** — it never fixes chrome to the viewport, never traps scroll, never opens overlays that escape its container.
- Fluid single-column layout driven by container width, not viewport width; no CSS features beyond the Android 8-era WebView floor (feature-detect WebGL, SpeechSynthesis, and modern APIs; render the Floor tier when detection fails).
- The Player styles only its own container: no global CSS resets, no `!important` wars with the institution's Moodle theme, class names namespaced.
- Height is self-managed; the page never shows nested scrollbars.
- One Player instance per page; Block navigation (Back/Next) changes content in place — the browser back button stays Moodle's, untouched.
- All Player chrome uses `DESIGN.md` colors; the core bundle renders in the system font stack for first paint, and the standard lazy fonts chunk upgrades Player text to the brand fonts per `{typography.player-ui}` (2026-07-18: webfonts are standard on all capable devices, post-first-paint, never render-blocking). The Player root carries its own opaque background and hairline border, so it reads as a deliberate card on light institutional themes (light-only confirmed — item 4 in § Rulings & Open Items; a dark-theme audit is post-MVP).
- **No layout shift.** On Block navigation the Player brings its own top edge into view — the Student is never left staring mid-page after content swapped. Media containers reserve their space: a poster and its replacement (viewer/iframe) occupy the same reserved box, so tap-to-load never shifts text already on screen.
- **Client contexts.** The rules above are written for desktop and mobile *browsers* rendering the activity page. The **Moodle mobile app** is a distinct client: MVP does not attempt app-native rendering; the activity presents a designed, content-styled hand-off — "This lesson opens in your browser." with one button — never an unstyled fallback. The Teacher entry point behaves the same in the app (opens the system browser). (Confirmed by stakeholder, 2026-07-17: app-native support is out of MVP scope; the hand-off is the designed path.)
- **Native structurally, unmistakably e-DON visually.** The contract governs structure (scroll, height, width, no shift); within it the Player's visual voice is polished and delightful per `DESIGN.md` — a flagship product card, not an anonymous embed (stakeholder amendment, 2026-07-17).

## Voice and Tone

Microcopy rules; brand posture lives in `DESIGN.md § Brand & Style`. Every user-facing string is externalised with a language key (NFR-8) — English at launch, plain and warm, written for moderate digital literacy. Money and AI limits are stated honestly, in institutional terms, never as blame.

| Do | Don't |
|---|---|
| "Your draft is ready to review." | "🎉 Your AI lesson has been generated!" |
| "Usually ready in a few minutes. You can close this — we'll keep working." | "Please wait. Do not close this window." (also: don't promise "under 5 minutes" — SM-1 is a median; p90 is 2× it, A-34) |
| "Generation failed: we couldn't find enough course material on this topic. Try a more specific topic." | "Error 422: ungrounded generation" |
| "You've used today's 20 diagram requests. More available tomorrow." | "Rate limit exceeded." |
| "New diagrams are paused for your college this month. Diagrams already drawn are still available." | "Tenant budget exhausted." |
| "AI-generated — verify against your course materials" (verbatim, FR-28) | Softening or rewording the AI label |
| "This simulation can't run on this device. The picture below shows what it demonstrates." | "WebGL not supported" / "Loading failed" |
| "Score recorded: 8/10." | "Your submission has been successfully processed." |
| Address Teachers as professional peers; Students plainly and encouragingly | Exclamation marks, hype, or scolding on limits and failures |

Every number and period in limit copy (quota figures, retry windows, budget periods) is **interpolated from Tenant configuration** — the exemplars above show platform defaults (OQ-2), never hardcoded values; the NFR-8 externalised-strings rule makes this templating free.

## Component Patterns

Behavioral rules; visual specs live in `DESIGN.md § Components` under identical names.

| Component | Use | Behavioral rules |
|---|---|---|
| Button set | Both surfaces | Every action is a labeled button — no icon-only primary actions (moderate digital literacy). Destructive actions always confirm; nothing else does. |
| Regenerate control | Review Workspace: Diagram, Model3D, Simulation Blocks only (FR-10/OQ-3) | One click + confirm re-runs generation for this Block only; the rest of the Draft stays editable while it runs. Never offered on Slide/Quiz/Narration (manual edit there). (Stakeholder ruling 2026-07-17: ships PRD-minimal as specified; the optional "What should change?" steering field is recorded as a named fast-follow candidate, not an MVP requirement.) |
| Status chip | Lesson card, Block rail | States: Draft / Published / Edited / Needs review / Check failed. Lifecycle of "Needs review": appears on a Diagram/Model3D/Simulation Block whose content just arrived from generation or Regeneration, clears when the Teacher opens that Block; it is session-scoped, and the rail's unseen dot is the same state in miniature — one signal in two sizes, never two meanings (no review state is persisted — scope fence). Chips are informational, never clickable. |
| Lesson card | Course home | Shows own Drafts (private, OQ-13) and Tenant Published Versions. Card opens Review Workspace (own Draft) or a read view with "Duplicate as my draft" (others' Published Versions). The version count opens the version history line. |
| Generate form | Course home | Two fields only: Topic (required) and Guidance (optional). Course Context is a read-only chip — supplied by the Launch Token, never typed or picked (FR-4, FR-29). Submitting an identical request lands on the existing Draft with an info Notice banner (FR-7 idempotency), not a new job. Submitting without a topic is rejected inline with a clear message (FR-4). The same form serves **whole-Lesson Regeneration** (FR-7, UJ-1 edge): a "Regenerate entire lesson…" action on the Review Workspace and the Lesson card reopens it prefilled with the Lesson's topic and guidance, both editable; the confirm names how many Blocks will be replaced; submitting explicitly re-runs the pipeline, bypassing the idempotency cache. |
| Generation progress card | Course home / post-submit | The showpiece moment (stakeholder amendment, 2026-07-17): generation renders as **visible block-by-block assembly** — the lesson outline materializes as the pipeline reports each Block (glyph + title skeleton → filled row), never a bare spinner. Requires per-Block progress events from the pipeline (upgrades A-8's "desirable, not committed" — carried in the Architect handoff); when events are absent, degrades to the plain card with coarse states queued → generating → complete/failed. Elapsed time visible; the Teacher can leave — the Lesson card carries the state. Failure shows the Teacher-readable reason (FR-8) and an explicit "Try again" (regeneration is never implicit). |
| Block rail | Review Workspace | Ordered Block list: index, type glyph, excerpt, mini status chip. Click selects; drag or focused up/down buttons reorder (FR-10). The rail is one tab stop: arrow keys traverse items, a documented modifier+arrow performs the same reorder as the visible buttons. Session-local "unseen" dot (visual spec in `DESIGN.md`) on Blocks not yet opened this session — a navigation aid only, never persisted; the rail item exposes the state programmatically ("not yet opened since generation"). |
| Block editor | Review Workspace | Per-type editing per the A-28 editability map: text fields for Slide, Narration, Quiz (questions, answers, accepted-answer lists, feedback), Model3D annotations; Diagram SVG and Simulation code render read-only with the Regenerate control adjacent. Every edit revalidates the Draft; validation errors pin inline to the offending field. Durability rule: **no acknowledged edit is ever lost to Authoring Session expiry** — a failed autosave surfaces immediately as a visible state (never silent), and content in the editor at expiry is preserved locally and restored on relaunch into the same Draft (mechanism architecture-owned). |
| Citations panel | Review Workspace | Per-Block Citations (FR-6/OQ-10), collapsible. Each card links excerpt → Grounding Chunk metadata. Deleting a Block visibly drops its Citations. |
| Preview overlay | Review Workspace | Renders the actual Player against the current Draft — no separate preview renderer (FR-9). Device-width toggle (Phone 360 / Tablet 768 / Full) and Low-spec view toggle (Floor-tier states, A-27) with the honesty line in its helper text: "Shows *what* these devices see — not how fast they see it" (real floor hardware is slow, not just featureless). Simulation Blocks are interactive in preview. Esc or Close returns without losing editor state. |
| Publish dialog | Review Workspace | Runs pre-publish checks visibly (schema validation; Simulation automated checks, FR-17/A-35). Any failure blocks publishing with a per-Block readable reason; the Teacher's exits are Regenerate or delete that Block (A-11). On success: explicit confirm → immutable Published Version with version number; copy explains adding/updating the Moodle activity. |
| Notice banner | Both surfaces | Info: confirmations, idempotency notices, and the persistent Tenant-Admin-on-another-Teacher's-lesson banner (informational, not an AI-attention state — gold reserved per DESIGN.md; ratified at readiness sign-off 2026-07-18). Warning (gold): Budget Ceiling pause — generation disabled with honest copy, replay unaffected (OQ-9/FR-26). Error: failed jobs, writeback problems. Banners are dismissible except the budget pause, which persists while true; the disabled Generate form is programmatically associated with the budget banner so the *reason* is discoverable by assistive tech. |
| Player shell | Player | Progress header: "Block n of N" + fill; marks viewed Blocks and Blocks still needing action (unsubmitted Quiz), with a programmatic text equivalent ("Viewed 4 of 9; Quiz in Block 6 not yet submitted"). Back/Next buttons are the only sequence navigation (no swipe) and are **always available** — a Student may read ahead without submitting; completion, not navigation, is what requires every Quiz Block submitted (OQ-15). On Block change, focus moves to the new Block's heading (a real heading element, `tabindex="-1"`) and the live region announces "Block n of N — {Block title}". Completion = all renderable Blocks viewed + all Quiz Blocks submitted; unknown Block types are excluded from both counts (FR-2). A script with zero renderable Blocks renders the major-version can't-play state, never an empty Player. |
| Slide block | Player | Static rich text; renders instantly (text is never behind a loader). Marks viewed on render. |
| Narration control | Player | Explicit play/pause; never autoplays. **Primary source is the pre-generated narration audio** shipped with the Published Version (`audioRef` — stakeholder amendment 2026-07-18); SpeechSynthesis is the fallback when audio is absent; text is always the primary modality and is never framed as a lesser mode. "Show text" toggles the transcript and exposes its pressed/expanded state to AT; when no audio source is usable, transcript shows by default and the play control is hidden (A-9). If playback does not audibly start within a bounded time of tap, the control converts to that same state — quiet, never an error. Narration state resets per Block. |
| Quiz block | Player | Multiple-choice and short-answer (FR-15). Instant client-side feedback per question — no server round-trip; feedback is announced (`role="status"`) and programmatically associated with its question group. On submit, the server re-scores and is authoritative. Durability rules: **Submit is single-fire** — the control disables on tap, a re-tap can never create a second submission, and an attempt is consumed at most once per Submit regardless of network retries (idempotent submission is an experience requirement; mechanism architecture-owned). "Saving your score…" may only show once the submission is durably accepted (server-acknowledged, or durably queued so it survives page close — Open Item 17); until then the state reads "Don't close this page yet — still saving." Writeback failure after acceptance shows a calm retrying notice and never blocks progress (A-13). Retakes per attempt limits; highest attempt recorded; attempts remaining always visible (OQ-15). On Showcase, a correct submission earns the brief green-family celebratory micro-interaction (visual spec in `DESIGN.md`; never gold, suppressed by `prefers-reduced-motion`; copy stays plain — celebration is motion's job, not copy's). (Answers and accepted-answer lists necessarily ship with the Published Version for client feedback — an accepted formative-stakes trade-off, A-21; the server score is what reaches the gradebook.) |
| Diagram block | Player | Displays the reviewed, sanitised SVG scaled to container width, with an in-container "View larger" affordance (expands to full container width, or opens the raw sanitised SVG in a new tab — a link, not an overlay, so the embedding contract survives; pinch zoom is host-controlled and cannot be the only recourse). Every Diagram Block carries a text alternative (see Accessibility Floor). Label legibility is a generation/validation requirement: minimum rendered label size at 360px container width, checkable at Sanitisation time from font-size/viewBox math (mechanism architecture-owned). No AI label — this content passed the Review Gate. |
| Model3D viewer | Player | Auto-loads by default with the hero entrance on Showcase (poster is the instant first paint; the intro plays inside the reserved media box, no layout shift, skipped under `prefers-reduced-motion`); poster-first tap-to-load only under data-saver signals (Amendment F). Loaded: orbit (drag inside canvas, or arrow keys — the canvas is focusable with a role and name) + zoom; the control row (rotate, zoom ±, reset, annotations toggle) duplicates every gesture, so nothing is drag-only. Gestures capture only after the asset is interactive, so page scroll is never hijacked. Annotation markers and the control-row toggle both open the annotation text panel — on every tier. Attribution/licence line rendered from asset metadata (FR-16). |
| Simulation frame | Player | Auto-loads by default (Amendment F): the poster is the instant first paint while the sandboxed iframe starts and reaches ready; tap-to-load "Run simulation (size)" applies only under data-saver signals (FR-17). Parameters (sliders/inputs) are the simulation's own; the frame relays lifecycle via the postMessage protocol. A simulation that fails to load, crashes, or does not signal readiness within a bounded time renders the Poster fallback card (detection mechanism architecture-owned — a hard-crashed sandbox emits nothing, so the experience requirement is the bounded wait, not an error signal) — quiet on the page, honest in the caption. |
| Poster fallback card | Player, Preview overlay | The designed degraded state (FR-18): poster image + caption naming what the full asset shows + annotations/parameters as text. Counts as viewed. Never styled as an error. |
| Sources section | Player | Collapsed by default at lesson end: "Sources" with lesson-level Citations list (OQ-10). |
| Empty state | Both surfaces | One branded pattern for every empty surface (visual spec in `DESIGN.md`): headline + one-sentence body + single primary action. Empty is a designed state, never a blank region; copy follows Voice and Tone. |
| Completion summary | Player | Renders after the last Block: tick list of Blocks, score status, attempts line, jump-back links for anything missing. Cross-version rule (a retake landed on a newer Published Version): show *this attempt's* score plus one line "Your best score so far: X" (X = whatever the gradebook rule yields); attempt counts are per-Lesson, not per-version (definition folded into Open Item 11). The attempts counter falls back to its last-known value or "—" on flaky loads — never a spinner. |
| AI content label | Diagram message | The verbatim FR-28 label on every chat diagram. Always visible, never dismissible. |
| Diagram chat message | block_edon_ai chat | Request → generating state → sanitised SVG card with AI content label + "Report this diagram" control (≥48px hit area per the Player/chat target floor — corrected at readiness sign-off 2026-07-18; it is the FR-28 governance valve). The diagram card's accessible name = the FR-28 label + the Student's request text + the generated description. Cache hits render instantly and don't count against the Rate Limit (OQ-2). All limit/quota/failure states render as chat replies in Voice-and-Tone copy, announced via the chat's live region — the chat never errors technically. |
| Diagram review queue row | Diagram review queue | Shows diagram thumbnail, original request text, report count, date. Two actions (stakeholder rulings, 2026-07-17): **"Mark reviewed"** (the diagram is fine) clears it from the queue; **"Mark invalid"** (confirm required) clears it *and evicts its Tenant cache entry* so it can never be served again — the next equivalent Diagram Request regenerates fresh. This completes the OQ-17 governance loop: label → report → review → removal. Both actions emit Structured Events (FR-27 taxonomy extension approved; PM/Architect add "diagram review completed" and "diagram invalidated" to the FR-27 list). |

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| Cold load | Course home / Review Workspace / Player | Skeletons matching final layout — static below Showcase, animated on Showcase only, per the tiered motion budget in `DESIGN.md`. Player shows lesson title + first Slide text as early as possible — text before assets, always, on every tier. |
| Expired/invalid Launch Token | Relaunch notice | Full-screen, one sentence: "Your session has ended. Open Lesson Studio again from your Moodle course to continue." No login form, no retry button (FR-29). |
| Empty course home | Course home | Branded Empty state: "No lessons yet for this course." + New lesson button. |
| Generation queued / running | Course home | Generation progress card in its assembly form (block-by-block outline materializing; plain-card degradation when per-Block events are absent); copy sets a few-minutes expectation (SM-1 is a median — never promise a hard number) and says leaving is safe. |
| Generation failed | Course home | Error Notice banner + readable reason + "Try again" (explicit). No partial Draft exists (FR-5). |
| Identical request while Draft exists | Generate form | Routed to the existing Draft with info Notice banner: "This topic already has a draft — you're looking at it. Regenerate from here if you want a fresh one." (FR-7). The reroute is announced and focus moves to the banner — never a silent location change. |
| Budget Ceiling exhausted | Course home, Generate form | Persistent warning Notice banner (gold): generation paused for the college this month; in-flight jobs finish; replay and review unaffected (OQ-9). Generate form disabled with the same copy — never a silent failure. |
| Block regenerating | Review Workspace | The Block's rail item and editor pane show the working state; the rest of the Draft stays editable. On completion the new Block content replaces the old and gets the "unseen" dot. On failure: previous content retained + error notice on that Block only. |
| Draft validation error after edit | Block editor | Inline field-level error; Draft not saved until conforming (FR-3/FR-10). |
| Edit save failed / offline | Review Workspace | Persistent "Not saved — retrying" on the affected field plus a workspace banner; edits retained locally; recovery is never silent (the "Saved" state has this as its honest counterpart). |
| Session ending (Authoring Session near expiry) | Review Workspace | If the session lifetime is known, a warning banner precedes expiry ("Your session ends soon — recent changes are saved"); expiry itself lands on the Relaunch notice (relaunch mints a fresh Launch Token), and relaunch returns the Teacher into the same Draft, not Course home. Session lifetime and warning lead time: Open Item 16. (Naming corrected at readiness sign-off 2026-07-18: the 120 s single-use Launch Token is spent at launch; what expires mid-review is the 8 h Authoring Session.) |
| Simulation check failed | Review Workspace, Publish dialog | "Check failed" chip on the Block; Publish dialog lists the readable reason; publish blocked until Regenerate succeeds or the Block is deleted (A-11). |
| Publish succeeded | Publish dialog → Course home | Confirmation with the new version number; card flips to Published; copy points to placing/updating the Moodle activity (FR-22). |
| Discard Draft | Review Workspace | Destructive confirm; emits its Structured Event (FR-10). |
| Tenant Admin on another's lesson | Review Workspace | Persistent info banner naming the owner — visible, not blocking (OQ-13). |
| Lesson not available | Moodle activity (Student) | "This lesson isn't available yet. Ask your lecturer." — never Draft content, never a technical error (FR-12). |
| Unknown Block type (newer minor schema) | Player | The Block is omitted from the sequence and the "Block n of N" count entirely — no gap card, no error; completion counts renderable Blocks only, so a Student is never stranded (FR-2, `project-context.md` §6). |
| Major-version mismatch | Player | Defined can't-play state, calm and content-styled: "This lesson needs a newer version of the player and can't open yet. Ask your lecturer." Never partial render, never silent corruption (FR-2). |
| Simulation Blocks flagged off for Tenant | Player / generation | Generation produces no Simulation Blocks; an existing Published Version renders its Simulation Blocks as Poster fallback cards. `[ASSUMPTION: poster render for flagged-off Blocks; flag mechanics are architecture-owned (A-14)]` |
| Mid-lesson connectivity loss | Player | Current Block stays usable; moving to a Block whose *assets* haven't loaded shows an inline retry ("Couldn't load the next part — try again") without resetting position. (The published script arrives complete up front — only heavy assets load lazily; nothing here implies incremental script delivery, which is reserved for V3.) |
| Quiz submitted, score syncing | Quiz block / completion summary | "Saving your score…" → "Score recorded: n/N." On persistent failure: "We'll keep saving your score — you can continue." Student never re-does work (A-13). |
| Attempts exhausted | Quiz block | Attempts-used line; answers reviewable read-only; highest attempt stands (OQ-15). |
| Completion reached | Completion summary | All-Blocks-viewed + quizzes-submitted confirmation, score status, attempts remaining; completion reflects in Moodle course page tick (FR-23). If anything is still missing (unviewed Block, unsubmitted Quiz), the summary lists it with a jump-back link instead of a dead end. |
| Version pinning | Player | In-flight sessions keep the Published Version they started (A-4); new attempts load the latest. When a returning Student receives a different Published Version than last time, one line of content-styled copy explains it — "Your lecturer updated this lesson." — and that is the *only* version chrome Students ever see. |
| Player reloaded mid-lesson | Player | The most common session shape on floor devices (battery saver, tab kill, app switch). Experience floor regardless of mechanism (resume mechanics are architecture-owned, FR-23): viewed marks and submitted-quiz state are visibly restored — or an honest designed state says what was kept — never a silent restart at Block 1. A reload does not end the pinned session and never consumes an attempt (Open Item 11). |
| Player script-load failure | Player | The bundle or Published Version itself fails to fetch: calm can't-load state in the same voice as the major-version state — "This lesson couldn't load. Try again." with a retry — never a blank region in the Moodle page. |
| Diagram generating | Diagram message | "Drawing your diagram… this can take a moment." |
| Diagram cache hit | Diagram message | Instant render; visually identical to a fresh diagram (label included). |
| Rate Limit reached (temporal throttle) | Diagram message | Chat reply: "You're asking quickly — you can try again in {retry window}." Always states when retry is possible (FR-21); the window is interpolated from Tenant config. Distinct from the daily Quota below (PRD Glossary separates the two). |
| Daily diagram Quota reached | Diagram message | Chat reply: "You've used today's {n} diagram requests. More available tomorrow." ({n} from Tenant config; default 20, OQ-2). |
| Tenant diagram quota/budget cache-only | Diagram message | Chat reply: "New diagrams are paused for your college this month. Diagrams already drawn are still available." (OQ-9). |
| Sanitisation/generation failure | Diagram message | "Couldn't produce that diagram. Try describing it differently." — never partial or raw output (FR-20). |
| Diagram reported | Diagram message | Inline confirmation: "Thanks — your lecturer will review this diagram." Report control disabled after reporting. |
| Diagram feature flagged off | block_edon_ai chat | No diagram affordance appears; chat behaves as today (FR-26). |
| Empty diagram review queue | Diagram review queue | Branded Empty state: "No reported diagrams." |

## Interaction Primitives

**Player (touch-first, floor-device-first):**

- Tap is the only required gesture. Explicit Back/Next buttons — **no swipe navigation** (conflicts with page scroll inside Moodle and with old WebView gesture handling).
- Touch targets ≥ 48px. No hover-dependent affordances anywhere.
- 3D orbit/zoom gestures activate only once the asset is interactive (after auto-load, or after tap-to-load under data-saver signals), inside the canvas; everything the canvas does is also available as buttons (zoom ±, reset view).
- Narration and simulations *start* only on explicit user action — nothing makes sound unrequested. Showcase auto-load readies content and may animate its entrance; it never starts sound.

**Authoring UI (pointer-first, fully keyboard-operable):**

- Every drag interaction (Block reorder) has a button equivalent (up/down on the focused rail item).
- Inline edit: click into field, edit, blur/`Esc`; save is automatic on valid input with a visible "Saved" text state (and its "Not saved — retrying" counterpart), never a per-field save button.
- `Esc` closes the topmost overlay (Preview, dialogs); overlays never stack more than one deep. Overlays trap `Tab`; initial focus lands on the overlay title; focus returns to the invoking control on close.

**Banned everywhere:** swipe-to-navigate, hover-only affordances, autoplaying audio/video, icon-only primary actions, modal stacks >1, infinite scroll, unlabeled spinners as sole feedback (>2s states always carry text), continuous animation on Full/Constrained/Floor tiers (Showcase follows the tiered motion budget in `DESIGN.md § Components → Player shell`), any motion on gold governance elements, and any animation that ignores `prefers-reduced-motion` (both surfaces, every tier).

## Accessibility Floor

Visual contrast pairs live in `DESIGN.md § Colors`. **Target (adopted by stakeholder 2026-07-17, resolving PRD OQ-7): WCAG 2.1 AA**, scoped as follows — full AA conformance is required for every surface we control: the Authoring UI, Player chrome, all designed states, and the Moodle-native surfaces. AI-generated content (diagrams, generated visuals) is governed by the text-alternative contract below plus best-effort conformance; full AA over generated artifacts is not promised. The behavioral floor below is the enforced baseline on Floor-tier devices regardless.

- **Scope: all three surfaces** — Authoring UI, Player, *and* the diagram chat message (the one place AI content reaches Students unreviewed inherits every rule here, including target sizes).
- **Text-alternative contract for AI-generated visuals.** Every Diagram Block and every poster (Model3D, Simulation) carries a Student-facing text alternative — a short `altText` and, for labelled technical diagrams, a `longDescription` — produced by generation from the same Grounding Chunks, stored in the Lesson Script, and editable as plain text in the Block editor (extends the A-28 editability map: alternatives are text even where the SVG is not). Sanitisation's allowlist must explicitly *preserve* SVG accessibility markup (`<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby`) — otherwise the sanitiser strips whatever accessibility the model emitted. **Approved in full (stakeholder, 2026-07-17):** Schema v1.0 carries these fields; the generation pipeline populates `altText` at creation; Teachers edit them in review. Carried in the Architect handoff as a schema/PRD data-model addition — the schema is "playable forever" (I-3), which is exactly why it lands before freeze.
- Full keyboard operability on all surfaces: quiz options as radio groups, `Tab` order = reading order. The Review Workspace names its panes as landmarks (navigation / main / complementary), offers a skip-to-editor link, and the Block rail is a single tab stop with arrow-key traversal (see Component Patterns).
- For Simulation parameters (controls rendered *inside* the sandboxed iframe by generated code), keyboard adjustability is a generation-contract requirement — native form controls (`<input type="range">`, `<button>`) required — and the A-35 check set is **extended** (A-35: "extend, do not narrow") with an automated keyboard-operability check: every declared parameter maps to a native control or a focusable role with key handlers. The poster path's parameter descriptions remain the last-resort equivalent.
- Narration content always available as text (A-9); transcripts are real text, selectable and screen-reader readable.
- Every lesson completable without WebGL, without audio, and without color perception: correctness feedback pairs color with glyphs (✓/✗) and text (FR-18 ladder).
- Async state changes announced via `aria-live=polite`: generation progress, score sync, regeneration, per-question quiz feedback, Block changes, and the idempotency reroute. The AI content label is part of the chat diagram's accessible name.
- Simulation iframes carry accessible titles; their poster fallbacks carry full text alternatives (captions + parameter descriptions).
- Player content regions and diagram cards set `lang` from the Lesson Script's language tag (NFR-8 already carries it) — correct screen-reader pronunciation for free, localisation-proof.
- Visible focus indicators per `DESIGN.md` on every interactive element; touch targets ≥ 48px in the Player and chat message, ≥ 44px in authoring.
- All meaning-carrying color pairs meet AA per `DESIGN.md § Colors`; gold never carries meaning as text/hairline on light surfaces.
- Hygiene: toggle controls ("Show text", Low-spec view) expose pressed/expanded state; live regions exclude ticking values (elapsed time); a control disabled for a policy reason (budget pause) is programmatically associated with the banner that explains why. SpeechSynthesis narration can speak over a running screen reader — acceptable because it never autoplays and the transcript is equivalent, but stated here so it is a known interaction, not a surprise.

## Responsive & Platform

| Context | Behavior |
|---|---|
| Authoring ≥ 1024px | Three-pane Review Workspace (rail / editor / citations) per `DESIGN.md § Layout & Spacing`. |
| Authoring 768–1023px | Citations panel becomes a slide-in sheet; rail persists. |
| Authoring < 768px | Rail becomes a horizontal block strip above the editor; all functions remain available. (Confirmed by stakeholder, 2026-07-17: authoring is desktop-optimized but phone-functional — many lecturers are phone-primary; nothing is desktop-only.) |
| Player, any container | Fluid single column; behavior keyed to container width. Constraint, not technique: layout must work on Android 8-era WebViews that lack modern layout APIs (e.g., container queries) — how width is obtained is implementation's choice. Thresholds ~600px for padding/reading-width changes only. Never horizontal scroll. |
| WebView floor | Feature-detect WebGL, SpeechSynthesis, and every modern API; absent features route to the Capability Tier ladder, never to a broken screen. |
| Performance as UX | Text renders before assets; every >2s wait has a labeled state; heavy assets auto-load by default (poster is the instant first paint), with tap-to-load + transfer size only under data-saver signals (Amendment F). Measurable CI checks (2026-07-18 split): the **blocking** floor runs on a standard modern profile — lesson title + first Slide text within the architecture-set budget; the throttled low-spec profile still runs but is **advisory** (it informs the fallback experience, it does not gate). Skeletons appear only for waits >300ms and always resolve text-first. The core Player bundle budget keeps its hard CI fail; fonts/motion chunks load lazily after first content paint (standard) and never count against it. |

## Key Flows

Protagonists and journey names mirror PRD §2.3 verbatim. UJ-4 (Operator onboarding) has no UX surface in scope (A-2).

### Flow 1 — UJ-1: Dr. Amina generates, reviews, and publishes a lesson

1. In her Moodle course, Dr. Amina clicks **Open Lesson Studio** on the mod_edonlesson teacher view. A new tab opens on Course home; the header chip reads her course name — she never logged in, never picked a course (FR-29).
2. She clicks **New lesson**, types "Ohm's Law and simple circuits", adds one guidance line, submits. The Generation progress card appears: "Usually ready in a few minutes. You can close this — we'll keep working."
3. She marks two exam scripts while it runs; when she glances back, her lesson is visibly assembling — outline rows materializing Block by Block as the pipeline completes them — until the card reads **Draft ready to review**.
4. Review Workspace opens. The Block rail shows 11 Blocks, each with a gold unseen dot. She steps through: fixes a misleading quiz distractor inline (accepted answers editable, FR-10/OQ-4), deletes a redundant Slide, moves the Simulation before the Quiz with the reorder buttons.
5. The circuit Diagram mislabels a resistor. She clicks **Regenerate** on that Block and confirms. It alone shows the working state; she keeps reviewing others. The new diagram lands with a fresh unseen dot, its Citations updated.
6. **Preview** at Phone 360 width, then flips on **Low-spec view**: the 3D circuit becomes its poster card with annotations as text. It reads as content, not damage. She closes preview — her editor state is intact.
7. **Publish.** Checks run visibly: schema ✓, simulation checks ✓. She confirms.
8. **Climax:** the dialog settles green — "**Version 1 published.** Students will see this lesson once you add it to your Moodle course." Gold has left the screen; everything is settled green and neutral. Back in Moodle, she adds the activity via the Lesson picker in two minutes.

*Failure paths:* generation fails → readable reason + explicit Try again, no partial Draft (FR-8). The Draft is off-target → she discards it, reopens the prefilled Generate form, sharpens her guidance, and explicitly regenerates (UJ-1 edge; never implicit). Simulation check fails → publish blocked with the per-Block reason; her exits are Regenerate or delete that Block (A-11). Her Authoring Session expires over lunch → Relaunch notice, one sentence; every acknowledged edit is preserved and relaunch returns her to this Draft (the Block editor durability rule).

### Flow 2 — UJ-2: Chinedu completes a lesson on a budget Android phone

1. Chinedu taps the lesson activity in his Moodle course on a 2 GB Android 8 phone. The Player mounts in the page; the title and first Slide text render before anything heavy — Block 1 of 9.
2. His WebView has no usable voices, so the narration's transcript is already open below the heading and the play control is hidden. He reads instead (A-9).
3. His data saver is on, so heavy Blocks are tap-to-load with size labels (Amendment F — auto-load is the default otherwise). The Simulation Block shows its poster and **Run simulation (1.1 MB)**. He taps; sliders appear; dragging resistance changes the current live (FR-17).
4. The Model3D Block offers **Load 3D model (4.2 MB)**. Data is low; he doesn't tap. The poster and its numbered annotation text tell him what the model shows — the Block counts as viewed (FR-18).
5. The Quiz: he answers each question and gets instant feedback with the correct answer explained (FR-15). He submits.
6. "Saving your score…" becomes "**Score recorded: 8/10.**"
7. **Climax:** the completion summary shows every Block ticked and his score recorded; back on the course page, the activity carries Moodle's own completion tick, and the 8/10 is in the gradebook his lecturer already uses (FR-23).

*Failure paths:* score writeback fails → "We'll keep saving your score — you can continue," no rework (A-13). Connectivity drops mid-lesson → current Block stays; Next shows inline retry.

### Flow 3 — UJ-3: Ngozi requests a diagram in chat

1. Revising at night, Ngozi types into the AI chat she already uses: "labelled diagram of the human heart".
2. "Drawing your diagram… this can take a moment." The diagram card renders: sanitised SVG, labels legible at phone width, and the label she always sees — **AI-generated — verify against your course materials** (FR-28).
3. **Climax:** minutes later her classmate asks for the same diagram and it appears instantly — the cache, invisible, just feels like a fast product (FR-21). Ngozi cross-checks one label against her textbook, spots a doubtful one, taps **Report this diagram** → "Thanks — your lecturer will review this diagram."

*Failure paths:* 21st request today → "You've used today's 20 diagram requests. More available tomorrow." College budget exhausted → "New diagrams are paused for your college this month. Diagrams already drawn are still available." Sanitisation failure → "Couldn't produce that diagram. Try describing it differently."

### Flow 4 — UJ-5: Dr. Amina revises a published lesson

1. A term later, Dr. Amina relaunches Lesson Studio from her course. The Lesson card reads **Published · v1** with her Draft beneath it.
2. She opens the Draft, improves two Slides, previews, publishes.
3. **Climax:** "**Version 2 published.**" The card's version line now reads *v2 current · v1 archived, still playable* (FR-11/I-3). New Student sessions get v2; nobody mid-lesson is yanked forward (A-4). Her Moodle activity needs no touch — it serves the latest version.

*Alternate path:* a colleague wants her lesson for another course → they find it in the **College library** tab (Tenant-wide Published Versions, OQ-13) and duplicate it as their own Draft; Dr. Amina's original is untouched.

### Flow 5 — Reported diagram triage (FR-28)

1. Dr. Amina notices the **Diagram review queue** badge on Course home: 1 waiting.
2. The queue row shows Ngozi's heart diagram thumbnail, the original request text, and one report. She opens it, checks the flagged label against the syllabus — Ngozi is right; one label is wrong.
3. **Climax:** she clicks **Mark invalid** and confirms. The diagram leaves the queue and its Tenant cache entry is evicted — no Student will ever be served it again, and the next request for that diagram regenerates fresh. The governance loop — label, report, review, removal — closed inside the tools both users already had (OQ-17; stakeholder ruling 2026-07-17).

*Alternate path:* the diagram is actually fine → **Mark reviewed** clears it from the queue; the cache is untouched.

## Rulings & Open Items

All 17 items were ruled by the stakeholder on 2026-07-17 (full record in `.memlog.md`). Numbering is stable — in-text references to "Open Item n" resolve here.

> **Amendment F (stakeholder realignment, 2026-07-18, at architecture sign-off):** device posture inverted — modern smartphones with reliable connectivity are canonical; Showcase/Full is the default experience; the Floor tier is thin best-effort fallback and the low-spec CI profile is advisory. Item 5 (tap-to-load) re-amended: auto-load default everywhere, tap-to-load only under explicit data-saver signals. Item 3 re-amended: Player webfonts are standard (lazy, post-first-paint). New MVP capability: **pre-generated narration audio** (publish-time TTS; text remains primary) and **course-scoped Live Q&A** via the embedded block_edon_ai chat on the activity page. V2 reserved (do not design): dialogue Block types, AI Teacher persona, scripted classmates. These amendments supersede conflicting text elsewhere in this spine; the sections above have been updated in place.

1. **Accessibility target (PRD OQ-7) — RESOLVED:** WCAG 2.1 AA adopted, scoped: full AA on all controlled surfaces (Authoring UI, Player chrome, designed states, Moodle-native surfaces); AI-generated content is governed by the text-alternative contract plus best-effort conformance; the pragmatic floor remains the enforced Floor-tier baseline.
2. **Reported-diagram remediation — RESOLVED (yes):** "Mark invalid" evicts the diagram's Tenant cache entry so it is never served again — treated as completing OQ-17's governance loop, not new scope. Designed in § Component Patterns and Flow 5.
3. **Player webfonts — RESOLVED as amended:** the core bundle stays webfont-free and within budget; the Showcase tier lazily loads Inter + Plus Jakarta Sans as an enhancement chunk (amendment E, `.memlog.md`).
4. **Light mode only — CONFIRMED.**
5. **Tap-to-load — RESOLVED as amended, then re-amended by Amendment F (2026-07-18):** auto-load is now the default everywhere; tap-to-load applies only under explicit data-saver signals.
6. **Authoring posture — CONFIRMED:** desktop-optimized, phone-functional.
7. **Attempt limits in the Moodle Lesson picker — CONFIRMED.**
8. **New-tab launch — CONFIRMED.**
9. **Block-Regeneration steering field — RESOLVED (no):** MVP ships PRD-minimal plain re-run; "What should change?" is recorded as a **named fast-follow candidate**, not a requirement.
10. **Mark-reviewed Structured Event — RESOLVED (yes):** added to the FR-27 taxonomy (with "diagram invalidated" accompanying item 2).
11. **Attempt unit — ARCHITECT HANDOFF:** define whether an attempt is a full lesson run or per-Quiz-Block submission, including what "highest attempt" means across Published Versions with different quiz denominators (see the Completion summary rule) and the guarantee that a reload neither ends the pinned session nor consumes an attempt.
12. **Curriculum Reference provenance — ARCHITECT HANDOFF:** pipeline-derived; define whether and how a Teacher corrects it during review.
13. **College library tab — CONFIRMED.**
14. **Moodle mobile app scope — CONFIRMED:** designed browser hand-off for Student activity and Teacher entry point; app-native rendering out of MVP scope.
15. **Schema text-alternative fields — APPROVED IN FULL:** `altText`/`longDescription` in Schema v1.0 for Diagram Blocks and Model3D/Simulation posters; the Sanitisation allowlist preserves `<title>`, `<desc>`, and `aria-*` attributes; the pipeline populates `altText` at creation and Teachers edit it in review. Carried below as a schema/PRD data-model addition.
16. **Launch Token lifetime & expiry experience — ARCHITECT HANDOFF:** token lifetime policy, pre-expiry warning, autosave durability across expiry, relaunch-into-the-same-Draft (FR-29 ADR).
17. **Quiz submission durability — ARCHITECT HANDOFF:** durable-acceptance gating for "Saving your score…", single-fire idempotent Submit, an attempt consumed at most once per Submit.

### Architect handoff (explicit — the Architecture workflow must carry all of these)

- Items **11, 12, 16, 17** above, unabridged.
- **Schema/PRD data-model addition (item 15):** text-alternative fields in Schema v1.0 plus the Sanitisation-allowlist entries preserving SVG accessibility markup.
- **FR-27 taxonomy extensions (items 2 and 10):** "diagram review completed" and "diagram invalidated (cache evicted)" Structured Events.
- **Per-Block generation progress events (amendment E):** the block-by-block assembly showpiece upgrades A-8's "finer-grained progress desirable, not committed" to required for the Showcase authoring experience; the card degrades to stage labels where events are absent.
- **Showcase tier detection (amendment E):** capable-device + fast-connection heuristics with demote-when-unsure semantics, data-saver signals honored; enhancement chunks (webfonts, motion) load after first content paint, outside the core bundle budget.
