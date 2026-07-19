# Adversarial Review — Low-Spec Device Floor & Moodle-Embedded Reality

Reviewed: `DESIGN.md`, `EXPERIENCE.md` (spines of 2026-07-16), grounded against PRD §4.4, FR-18, FR-22/23/29, NFR-2, OQ-15/16.
Lens: a 2 GB Android 8 phone with an outdated WebView, on metered data, inside a Moodle page — and a teacher on a short-lived token. Everything below is a field scenario, not a taste note.

## Verdict

The spines are unusually honest about the floor — tap-to-load everywhere, poster-as-first-class, no webfonts/no shadows, feature-detection-not-UA — and that discipline is real and checkable. But the spines model the floor device as a *featureless* browser tab, and the field device is a *hostile* one: it kills the tab, drops the POST, reloads the page, and lies about its speech voices. Three whole classes of behavior the floor makes routine — page reload mid-lesson, quiz submission on a dying connection, and the Moodle mobile app as the client — are either unspecified or specified only by a narrative sentence in a flow. Until those are behavioral rules in Component/State Patterns, the "degraded states are designed states" promise holds only for the polite failures.

---

## Critical

### C1. The Moodle mobile app is nowhere in either spine — and it is how many students will open the course
**Location:** EXPERIENCE `§ Moodle Embedding Contract` (entire section), `§ Foundation` item 1 (`[ASSUMPTION: new browser tab]`), `§ Information Architecture` Student surfaces ("Moodle activity load (mod_edonlesson embed)"). PRD FR-22 says only "embedded in the Moodle page."

The embedding contract is written exclusively for a browser rendering the Moodle activity *page*: "mounts into the activity page's content region and inherits the page's scroll." The Moodle mobile app does not render activity pages that way — an activity module either ships an app-side handler or the app shows its own fallback ("open in browser" hand-off, or an app-managed WebView with different scroll, zoom, and lifecycle behavior). At colleges where the app is pushed precisely because it is cheaper on data, a large share of Students will hit mod_edonlesson through the app first. Today the spines specify nothing: not whether the app path is in scope, not what the hand-off state looks like, not whether the contract's scroll/height/one-instance rules survive an app-managed WebView (where pinch zoom — which the Diagram block explicitly leans on — is often disabled). The Teacher side has the same hole: `Foundation` assumes the launch "opens the Authoring UI in a new browser tab," which does not exist inside the app; Open Item 8 confirms tab-vs-same-tab but never asks "what if there is no tab?"

**Field scenario:** Student in the Moodle app taps the lesson activity. Best case: an ugly unstyled "open in browser" screen that violates the never-look-broken rule. Worst case: an app WebView where the Player half-works and no one designed the half.

**Fix:** Add a "Client contexts" row set to the Moodle Embedding Contract naming the three clients (desktop browser, mobile browser, Moodle app) and the required behavior in each. Minimum viable: a designed, content-styled hand-off state for the app ("This lesson opens in your browser" with one button), written in Voice-and-Tone copy, plus an explicit scope statement (app-native support yes/no) escalated as an Open Item with stakeholder sign-off. Do the same for the Teacher launch (`no-tab` context).

### C2. Quiz submission on flaky connectivity: no double-submit protection, no durability rule — and the copy makes a promise nothing guarantees
**Location:** EXPERIENCE `§ Component Patterns → Quiz block`; `§ State Patterns → "Quiz submitted, score syncing"`; PRD A-13, OQ-15 (attempt limits, highest attempt).

The spine specifies "Saving your score…" → "Score recorded: n/N" and, on persistent failure, "We'll keep saving your score — you can continue." Three things it does not specify:

1. **Double-submit.** Student taps Submit on a 2G-grade connection; nothing visibly happens for four seconds; they tap again (the universal Nigerian-network reflex). Are two attempts consumed? With Teacher-configured attempt limits (OQ-15), a double-tap that burns an attempt is a grade-affecting harm, and the spine says nothing about disabling the control, deduplicating the submission, or what "an attempt" costs when the first request may or may not have landed.
2. **Close-during-sync.** Student sees "Saving your score…", assumes done (the copy reads reassuring, by design), and closes the page. If the submission is client-held pending retry, it is gone — the student re-does the quiz, which directly violates A-13 ("retriable without Student rework"). The spine never states *where* the pending submission lives.
3. **The copy lies unless durability is a rule.** "We'll keep saving your score — you can continue" is only true if the submission has been durably accepted somewhere that survives the page. The spine offers the sentence but not the guarantee.

**Fix:** Add three behavioral rules to the Quiz block pattern: (a) Submit is single-fire — the control disables on tap and a re-tap can never create a second attempt (idempotent submission is an experience requirement; mechanism architecture-owned); (b) "Saving your score…" may only be shown *after* the submission is durably accepted (server-acknowledged or durably queued in a way that survives page close — if neither is possible, the state must say "Don't close this page yet"); (c) an attempt is consumed at most once per Submit regardless of retries. Escalate (b) to architecture alongside Open Item 11.

### C3. Page reload is the floor device's default behavior, and the spine has no resume state at all — worse, version pinning makes reload silently swap the lesson
**Location:** EXPERIENCE `§ State Patterns → "Mid-lesson connectivity loss"` (covers assets only), `→ "Version pinning"` ("In-flight sessions keep the Published Version they started (A-4); new attempts load the latest — silently"); Open Item 11 (attempt unit undefined); PRD FR-23 ("Resume-after-disconnect behavior remains an architecture decision").

On a 1.5–2 GB phone, Android kills the backgrounded tab/WebView constantly: WhatsApp notification, camera, twenty minutes idle — return, full page reload. This is not an edge; it is the modal session shape on the floor. The spine's only connectivity state covers "assets for the next Block didn't load." There is no state for "the Player reloaded mid-lesson": Does the student land on Block 1 with viewed-marks gone? Are submitted quiz scores still shown? PRD defers resume *mechanism* to architecture, but the spine defers the entire student-visible *experience* along with it — and then builds on the undefined boundary: "in-flight sessions keep the Published Version they started; new attempts load the latest, silently." If a reload ends the "in-flight session," the student who was on Block 7 of v1 reloads into v2 — different blocks, different quiz — with the spine explicitly specifying *no version chrome* to explain it, and possibly an attempt consumed. The word "silently" is a designed-in confusion on exactly the devices that reload the most.

**Field scenario:** Chinedu is on Block 7 of 9, score pending on quiz 1. Battery saver kills the tab. He reopens: Block 1 of 10 (the lecturer published v2 an hour ago), his quiz shows unanswered. He has no idea whether his 8/10 exists, whether this is the same lesson, or whether he just spent an attempt.

**Fix:** Add a State Patterns row "Player reloaded mid-lesson" specifying the experience floor regardless of mechanism: viewed-marks and submitted-quiz states visibly restored (or, if architecture cannot restore them, an honest designed state — never a silent restart); define that a reload does *not* end the pinned session or consume an attempt (tie to Open Item 11 and force its resolution); and delete "silently" — when a returning student gets a different Published Version than last time, one line of content-styled copy ("Your lecturer updated this lesson") costs nothing and prevents the support ticket.

---

## High

### H1. "Work persisted" through token expiry is a narrative claim in Flow 1, not a rule anywhere
**Location:** EXPERIENCE `§ Key Flows → Flow 1` failure paths ("Token expires over lunch → Relaunch notice, one sentence, work persisted"); `§ Interaction Primitives → Authoring UI` ("save is automatic on valid input"); `§ State Patterns → "Expired/invalid Launch Token"` and `→ "Draft validation error after edit"` ("Draft not saved until conforming").

Follow the chain for a 90-minute review of a long draft: autosave fires on valid input, and autosave requires a live token. The token is "short-lived" (FR-29) with no stated lifetime and no stated expiry experience. So: token dies at minute 40; the teacher keeps editing for 50 more minutes; every autosave since minute 40 has been failing — the spine defines no state for a failing autosave (the "Saved" text state has no counterpart "Couldn't save"), no pre-expiry warning, and no rule that unsynced field content survives the Relaunch notice. Meanwhile "Draft not saved until conforming" means a half-finished accepted-answers list is *by design* unsaved when the wall hits. Flow 1's "work persisted" is asserted by the story and guaranteed by nothing in Component Patterns or State Patterns — exactly the kind of claim that dies in implementation.

**Fix:** Promote it to a behavioral rule in Component Patterns (Block editor): "No acknowledged edit is ever lost to token expiry; a failed autosave surfaces immediately as a visible state (not silent), and content in the editor at expiry is preserved locally and restored on relaunch into the same Draft." Add a State Patterns row for "Autosave failing / session ending" distinct from the terminal Relaunch notice. Specify where relaunch lands (back into the Draft, not Course home). Name the token-lifetime question an Open Item — 90-minute reviews are the normal case for an 11-block draft, not the exception.

### H2. Sequential heavy blocks: no unload policy, no return-state rule — memory pressure is the one floor constraint the ladder ignores
**Location:** EXPERIENCE `§ Capability Tiers & Degradation Ladder` (tiers cover *load*, never *unload*); `§ Component Patterns → Player shell` ("block navigation changes content in place"), `→ Model3D viewer`, `→ Simulation frame`.

The ladder is entirely about whether a heavy asset *starts*. Nothing says what happens when the student moves on: Student loads the 4.2 MB glTF viewer (WebGL context #1), Next to the simulation, taps Run (sandboxed iframe, its own JS heap), Back to the 3D block. On 1.5–2 GB RAM with an Android 8 WebView (which caps live WebGL contexts and kills the renderer under pressure), two live heavy blocks is a tab crash — which lands you in C3 with everything lost. The spine also never answers the student-visible question: does Back to a previously-loaded 3D block show the live viewer or the poster again? If the poster, does re-tapping re-download 4.2 MB on metered data (a data-honesty question, not a mechanism question)?

**Fix:** Add a ladder rule, stated as experience not mechanism: "At most one heavy Block is live at a time; leaving a heavy Block releases it and it returns to its poster state. Returning and re-loading must not re-charge the student's data for an asset already downloaded this session (cached re-load, no size re-prompt — or, if re-download is possible, the size label reappears honestly)." This makes tab-crash avoidance a designed behavior and closes the repeat-download ambiguity.

### H3. Narration handles "no voices" but not "voices that lie" or "voices that are wrong" — and the tier table has no runtime-failure row for it
**Location:** EXPERIENCE `§ Capability Tiers` Narration column (Full/Constrained: "SpeechSynthesis play control"; Floor: "No usable voices → transcript by default"); `§ Component Patterns → Narration control` (A-9); `§ Interaction Primitives` ban on ">2s states without text".

Model3D and Simulation both have a runtime-failure path in the ladder ("load fails / crashes → poster"). Narration does not. On Android 8 WebViews, `speechSynthesis` routinely *reports* voices and then `speak()` silently does nothing (or the voice list is empty until an async event the spine's "feature-detect" framing doesn't capture). Result: the play control renders (detection passed), the student taps it, and nothing happens — zero feedback, which is worse than the spine's own banned unlabeled-spinner. "Usable voices" is doing all the work in the Floor row and is never defined. Second gap: "available but poor." The content is Nigerian English science text; the only voice on the device is en-US and mangles every local term and name. The spine treats narration as binary (works/absent) when the field reality is a quality spectrum — and NFR-8's language tag on Lesson Script text is never connected to voice selection.

**Fix:** (a) Add a narration runtime-failure rule mirroring the Simulation one: if speech does not audibly start within a bounded time of tap, the control converts to the Floor state (transcript shown, control hidden) — quiet, no error. (b) Define "usable" behaviorally: an English-family voice that begins speaking when asked. (c) Add a voice-preference experience rule: prefer the Lesson Script language tag (en-NG → en-GB → any en), and keep "Show text" permanently one tap away so a bad voice is never a trap (it is — good — but say *why* in the pattern so it survives redesign).

### H4. The Low-spec view simulates capability, not speed — the teacher's trust in the Review Gate is built on a fast laptop
**Location:** EXPERIENCE `§ Component Patterns → Preview overlay`, `§ Capability Tiers` ("The Teacher sees what the Floor sees", A-27); `§ Responsive & Platform → Performance as UX`; DESIGN `§ Components → Preview overlay`.

"The Teacher sees what the Floor sees" is only half-true, and the spine never admits the half. Low-spec view swaps in Floor *states* (posters, transcripts) rendered instantly on an i7. The real floor device shows the same states after 5–10 seconds of script parse and paint, with janky scroll in between. Dr. Amina signs off on a lesson that "reads as content, not damage" — and the damage on real hardware is temporal, not visual. Separately, the spine's perceived-performance rules are directional but unmeasurable: "text renders before assets," ">2s waits have a labeled state" — but no first-text target, no skeleton timing (minimum display to avoid flash, maximum before text must land), nothing bound to the CI low-spec profile the PRD already mandates (NFR-2), which is sitting right there as the measurement rig.

**Fix:** (a) One honesty line in the Preview overlay spec and its UI copy: "Low-spec view shows *what* these devices see, not how fast they see it." (b) Bind the experience to the existing CI profile with two measurable floors, e.g.: lesson title + first Slide text visible under the throttled CI low-spec profile within N seconds of mount; skeletons appear only for waits >300ms and always resolve to text-first. The numbers are architecture's to set; the spine's job is to demand that they exist and are CI-enforced like the bundle budget it already calls "a UX guarantee."

---

## Medium

### M1. Height self-management is asserted; layout shift is not addressed — the Next button is a moving target
**Location:** EXPERIENCE `§ Moodle Embedding Contract` ("Height is self-managed; the page never shows nested scrollbars"); `§ Component Patterns → Player shell` (bottom nav, in-flow because fixed chrome is banned).

The contract bans nested scrollbars and fixed chrome — good — but says nothing about the consequences: block heights vary wildly (a 3-line slide vs. a loaded 3D viewer + annotation panel), so on every Back/Next the in-flow bottom nav jumps vertically and the Moodle page's scroll offset points at nothing. Tap-to-load swaps a poster for a taller viewer mid-read, shoving the text the student was reading off-screen. On a slow device these shifts happen seconds after the tap, when the thumb is already resting where Next *used* to be.

**Fix:** Two contract rules: (a) on block navigation the Player brings its own top edge into view (never leaves the student stranded mid-page); (b) media containers reserve their space — poster and its replacement (viewer/iframe) occupy the same reserved box, so loading never shifts text already on screen. Both are experience requirements, cheap to state, expensive to retrofit.

### M2. Tap-to-load is the data-honesty headline, but posters auto-load with no size discipline anywhere
**Location:** EXPERIENCE `§ Capability Tiers` ladder rules ("Tap-to-load everywhere… respects metered data"); DESIGN `§ Components → Poster fallback card`; PRD FR-18 (budgets Model3D assets and the bundle — not posters).

Every heavy asset is size-labeled and consented — but every poster downloads automatically, on every tier, and neither spine nor PRD puts a byte budget or a loading rule on them. A 9-block lesson with posters on half its blocks silently spends megabytes of metered data before the student consents to anything. The poster path is, by the spine's own design, the *universal* rendering path — which makes its weight the single biggest uncontrolled data cost in the Player.

**Fix:** Add to the ladder rules: posters carry their own per-image budget (value architecture-owned, CI-enforced with the other budgets) and load lazily — only as their block approaches, never the whole lesson's posters up front. Text-before-assets already implies half of this; make it explicit for posters specifically.

### M3. Retake across Published Versions: "highest attempt" and "attempts remaining" have no student-visible story when the quiz changed
**Location:** EXPERIENCE `§ State Patterns → "Version pinning"`, `→ "Attempts exhausted"`; `§ Component Patterns → Quiz block` ("attempts remaining always visible"); PRD OQ-15 ("highest attempt", pinned to version taken).

Student scores 6/10 on v1. Retakes; new attempt loads v2, where the quiz is now 8 questions. They score 7/8. Which is "highest"? What does the completion summary show — 7/8 while the gradebook shows whatever the writeback rule computed across incomparable denominators? Do attempts carry across versions? The spine specifies the pinning rule and the always-visible attempts counter but never the cross-version display, and Students get *no version chrome* to even frame the difference. The jump-back links themselves are safe (within a pinned session) — the confusion is entirely at the retake boundary.

**Fix:** Specify the completion-summary display rule for cross-version attempts (recommend: show the score of *this* attempt plus one line "Your best score so far: X" using whatever the gradebook rule yields), and state that attempt counts are per-lesson, not per-version. Force the "highest across different denominators" question into Open Item 11's resolution — it is currently nobody's.

### M4. The Player has no motion policy — and the spine's own skeletons are the likeliest paint-cost violation
**Location:** EXPERIENCE `§ State Patterns → Cold load` (skeleton block); `§ Interaction Primitives` (bans list — no animation entry); DESIGN `§ Components → Player shell`, `progress-header`; DESIGN's only specified animation (regenerate sweep) is authoring-side.

DESIGN's discipline (no webfonts, no shadows, flat paint) is explicit, but neither spine bans or bounds *motion* in the Player. Every implementer will reach for the defaults: shimmer-animated skeletons (continuous compositing on a Mali-400-class GPU), width-transitioned progress fills, cross-fade block transitions. Each is a per-frame paint cost on exactly the hardware the brand promises to respect, and nothing in the spines makes it a violation. `prefers-reduced-motion` is also never mentioned.

**Fix:** Add one line to the Player shell pattern (or Interaction Primitives): "Player motion budget: no continuous animations (no shimmer — skeletons are static), no block-transition effects; the progress fill may step, not tween; respect `prefers-reduced-motion`." Cheap sentence, saves a frame budget.

---

## Low

### L1. "Sits comfortably on any institutional theme" vs. light-mode-only tokens
**Location:** DESIGN `§ Brand & Style` light-mode `[ASSUMPTION]`; EXPERIENCE `§ Moodle Embedding Contract` ("a branded card sitting comfortably on any institutional theme"). Some of the ~60 colleges will run dark or heavily-customized Moodle themes; a hard-white `{colors.surface}` card on a dark theme is a flashlight, and the contract sentence overpromises what the light-only assumption delivers. Fix: soften the contract claim to match the assumption, or add a minimal rule (Player root carries its own opaque background and a hairline border so it reads as a deliberate card, never as a theme bug) and note dark-theme audit as a post-MVP item on the existing assumption.

### L2. Size labels and offline counters: two small honesty holes
**Location:** EXPERIENCE `§ Capability Tiers` ("load control showing the download size"); `§ Component Patterns → Quiz block` ("attempts remaining always visible"). (a) "Size" is undefined — it must be *transfer* (compressed download) size, since that is what metered data charges; say so, or the label under-reports by the compression ratio. (b) "Attempts remaining always visible" requires server state; on a flaky load the spine should name the fallback (last-known value or "—", never a spinner in a counter).

---

*Reviewer note: findings C2, C3, H1, H2 share a root cause — the spines specify what surfaces look like in each state but are silent about state **survival** (across taps, retries, reloads, expiries). One pass adding durability rules to Component Patterns would close most of this review.*
