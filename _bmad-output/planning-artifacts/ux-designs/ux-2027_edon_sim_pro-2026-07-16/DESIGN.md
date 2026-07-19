---
name: e-DON Lesson Studio
description: Curriculum-grounded lesson authoring and playback for Nigerian Colleges of Education — calm institutional authority, AI-provenance made visible, low-bandwidth respect as an aesthetic.
status: final
sources:
  - _bmad-output/planning-artifacts/prds/prd-2027_edon_sim_pro-2026-07-07/prd.md
  - _bmad-output/planning-artifacts/prds/prd-2027_edon_sim_pro-2026-07-07/addendum.md
  - _bmad-output/planning-artifacts/edon-lesson-studio-product-brief.md
  - _bmad-output/project-context.md
updated: 2026-07-18
colors:
  primary: '#006847'
  primary-deep: '#004D34'
  primary-wash: '#E7F2ED'
  on-primary: '#FFFFFF'
  accent: '#FFB81C'
  accent-ink: '#402D00'
  accent-wash: '#FFF3D6'
  ink: '#191C1A'
  ink-secondary: '#565E5A'
  ink-disabled: '#9AA5A0'
  surface: '#FFFFFF'
  surface-subtle: '#F4F7F5'
  border: '#DCE5E0'
  border-strong: '#7E8C85'
  error: '#BA1A1A'
  error-wash: '#FBEDEB'
typography:
  display:
    fontFamily: 'Plus Jakarta Sans'
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
  display-sm:
    fontFamily: 'Plus Jakarta Sans'
    fontSize: 22px
    fontWeight: '600'
    lineHeight: '1.25'
  title:
    fontFamily: 'Plus Jakarta Sans'
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.3'
  body:
    fontFamily: 'Inter'
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: 'Inter'
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.45'
  label:
    fontFamily: 'Inter'
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
  caption:
    fontFamily: 'Inter'
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
  player-ui:
    note: 'The CORE Player bundle ships NO webfonts (strict bundle budget); Player text renders in the system stack for first paint: system-ui, -apple-system, Roboto, "Segoe UI", sans-serif — sizes/weights mirror the Inter ramp above. A lazy chunk loads Inter + Plus Jakarta Sans after first content paint as STANDARD on all capable devices (re-amended by stakeholder, 2026-07-18 — webfonts are no longer Showcase-only) — never render-blocking, never counted against the core budget. The system stack remains the fallback at every moment. Inter and Plus Jakarta Sans always load in the Authoring UI.'
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  '7': 48px
  gutter: 24px
components:
  button-primary:
    background: '{colors.primary}'
    foreground: '{colors.on-primary}'
    radius: '{rounded.md}'
  button-secondary:
    background: '{colors.surface}'
    foreground: '{colors.primary}'
    border: '1px solid {colors.border-strong}'
    radius: '{rounded.md}'
  button-quiet:
    background: 'transparent'
    foreground: '{colors.primary}'
    radius: '{rounded.md}'
  button-destructive:
    background: '{colors.surface}'
    foreground: '{colors.error}'
    border: '1px solid {colors.error}'
    radius: '{rounded.md}'
  regenerate-control:
    background: '{colors.accent-wash}'
    foreground: '{colors.accent-ink}'
    border: '1px solid {colors.accent}'
    radius: '{rounded.md}'
  ai-content-label:
    background: '{colors.accent-wash}'
    foreground: '{colors.accent-ink}'
    radius: '{rounded.sm}'
    typography: '{typography.body-sm}'
  status-chip:
    radius: '{rounded.full}'
    typography: '{typography.label}'
  block-rail-item-selected:
    background: '{colors.primary-wash}'
    indicator: '3px solid {colors.primary}'
  citation-card:
    background: '{colors.surface-subtle}'
    border: '1px solid {colors.border}'
    radius: '{rounded.md}'
    typography: '{typography.caption}'
  poster-fallback-card:
    background: '{colors.surface-subtle}'
    border: '1px solid {colors.border}'
    radius: '{rounded.lg}'
  quiz-option-correct:
    background: '{colors.primary-wash}'
    foreground: '{colors.primary-deep}'
  quiz-option-incorrect:
    background: '{colors.error-wash}'
    foreground: '{colors.error}'
  progress-header:
    track: '{colors.border}'
    fill: '{colors.primary}'
  notice-banner-info:
    background: '{colors.primary-wash}'
    foreground: '{colors.primary-deep}'
  notice-banner-warning:
    background: '{colors.accent-wash}'
    foreground: '{colors.accent-ink}'
  notice-banner-error:
    background: '{colors.error-wash}'
    foreground: '{colors.error}'
---

## Brand & Style

e-DON Lesson Studio serves lecturers and pre-service teachers at ~60 Nigerian Colleges of Education. The brand posture is **calm institutional authority**: this is a tool a college trusts with its curriculum and its gradebook, not a consumer AI toy. The palette is national — Nigerian green carries the institution's voice; gold carries the AI's.

That split is the system's one big idea: **green means settled, gold means judge this**. Everything the institution or the Teacher has approved renders in the green/neutral family. Everything the AI produced that still awaits human judgment — unreviewed Blocks, regeneration affordances, the "AI-generated" label on chat diagrams — renders in the gold family. A Teacher scanning a review screen can see at a glance what still needs their eyes; a Student can see at a glance which content carries an AI caveat. The Review Gate is the heart of the product (PRD I-2, FR-9–FR-12), and the color system exists to make that gate legible.

The third brand value is **adaptive performance as an aesthetic** (amended by stakeholder, 2026-07-17; posture inverted 2026-07-18 — Amendment F). e-DON reads as a flagship tech-startup experience, and **the polished, delightful expression is now the canonical default**: purposeful motion, a hero entrance for 3D content, brand typography, celebratory micro-interactions, generation rendered as a visible showpiece — modern smartphones with reliable connectivity are the assumed audience. Under data-saver signals or on genuinely constrained hardware the same product degrades gracefully to its restrained expression: flat surfaces, system fonts, static states, poster images styled as first-class content — a retained best-effort fallback rather than a launch-gating target. Both remain the brand. Motion is a polish voice, never a governance voice: it must never compete with, imitate, or animate the gold review-gate signals, and every animation respects `prefers-reduced-motion`.

## Colors

- **Nigerian Green (`{colors.primary}` #006847)** — the brand and action color. Primary buttons, links, active navigation, selection states, progress fills, and confirmed/success moments (publish confirmation, correct-answer feedback). There is no separate success token: green already means "settled and safe," and a second green would dilute it. Celebration also belongs to the green family — the Showcase quiz-success micro-interaction is green, never gold. Contrast on `{colors.surface}`: 6.8:1 (AA normal text, both directions — white-on-green and green-on-white).
- **Deep Green (`{colors.primary-deep}` #004D34)** — hover/pressed states of primary elements and high-emphasis green text on washes.
- **Green Wash (`{colors.primary-wash}` #E7F2ED)** — selected rail items, correct-answer fills, info banners. Always paired with `{colors.primary-deep}` (8.7:1) or `{colors.ink}` text.
- **Gold (`{colors.accent}` #FFB81C)** — the AI-provenance accent. Reserved exclusively for "AI output awaiting your judgment": regenerate controls, unreviewed-AI status chips, the AI-content label on chat diagrams, warning banners about AI/budget states. Gold is **never** used decoratively, never for celebration, and — critically — **never as text or a meaning-carrying hairline on light surfaces** (1.7:1 against white — fails every contrast threshold). Gold appears as a fill with `{colors.accent-ink}` text (7.6:1, AA) or as `{colors.accent-wash}` with `{colors.accent-ink}` text.
- **Gold Ink (`{colors.accent-ink}` #402D00)** — the only text color permitted on gold and gold-wash surfaces.
- **Ink (`{colors.ink}` #191C1A / `{colors.ink-secondary}` #565E5A / `{colors.ink-disabled}` #9AA5A0)** — text ramp on light surfaces. `ink-secondary` holds 6.7:1 on `{colors.surface}` (AA); `ink-disabled` is for disabled affordances only, never running text.
- **Surfaces (`{colors.surface}` #FFFFFF, `{colors.surface-subtle}` #F4F7F5)** — white canvas; the subtle green-grey tint distinguishes secondary panels (citations, posters, rails) without borders doing all the work.
- **Borders (`{colors.border}` #DCE5E0, `{colors.border-strong}` #7E8C85)** — hairline structure and control boundaries respectively. `border-strong` holds 3.5:1 on `{colors.surface}`, meeting the 3:1 non-text minimum, so it may be the *sole* boundary of an interactive control; `border` may not.
- **Error (`{colors.error}` #BA1A1A on `{colors.error-wash}` #FBEDEB)** — failed jobs, failed pre-publish checks, incorrect-answer feedback, destructive confirmation. 6.5:1 on white, 5.7:1 on its wash. Error red is never used for AI-attention states — that is gold's job; red means "something went wrong," gold means "someone must look."

Light mode only for MVP (confirmed by stakeholder, 2026-07-17): the Player must sit naturally on institutional Moodle themes (light), and a dark variant would double the contrast-testing surface on a constrained budget. No dark tokens are defined; adding them later is additive.

## Typography

Two families, two jobs (both SIL OFL; licence metadata recorded when the dependency lands, OFL acceptability confirmed in architecture per `project-context.md` §5):

- **Plus Jakarta Sans** (`{typography.display}`, `{typography.display-sm}`, `{typography.title}`) is the wayfinding voice of the **Authoring UI**: page titles, lesson titles, block headers, dialog titles. Its geometric warmth reads modern without reading playful.
- **Inter** (`{typography.body}`, `{typography.body-sm}`, `{typography.label}`, `{typography.caption}`) is the working voice: body copy, form fields, table rows, citations, chips.

The **Player's core rule stands**: per `{typography.player-ui}`, the core Player bundle ships no webfonts — text renders in the system stack for first paint at the same size/weight ramp (core bundle budget, plus Moodle-native feel). A lazy chunk loads Inter + Plus Jakarta Sans after first content paint as **standard on all capable devices** (re-amended by stakeholder, 2026-07-18); it is never render-blocking, never counted against the core budget, and the system stack remains the fallback at every moment. Lesson *content* is text, SVG, and assets; it never bakes text into images (NFR-8 localisation-readiness).

Type discipline: `display` appears at most once per screen. No all-caps except `{typography.label}` chips where case is set by content, not CSS. Minimum rendered body size anywhere: 14px — and *meaning-bearing text is body, not caption*: the AI content label, poster explanations, and quiz feedback render at ≥14px (`{typography.body-sm}`); `{typography.caption}` (12px) is reserved for genuine metadata (dates, chunk refs, version counts).

## Layout & Spacing

8px scale (`{spacing.1}`–`{spacing.7}`), `{spacing.gutter}` 24px page gutters.

- **Authoring UI** is a desktop-first workspace. The Review Workspace at ≥1024px is a three-pane layout: block rail (fixed ~280px, left), block editor (fluid center), citations/detail panel (~320px, right, collapsible). Below 1024px the Citations panel becomes a slide-in sheet; below 768px the rail becomes a horizontal block strip above the editor. Content forms (Generate form) cap at 640px width — authoring inputs are short, and a narrow column signals "this is simple."
- **Player** never owns the viewport. It renders inside the Moodle activity content region, fills its container width (max 100%, no fixed pixel widths), and manages its own height. Internal padding `{spacing.4}` on phones, `{spacing.5}` at ≥600px container width. One Block on screen at a time; Block content caps at ~720px reading width inside wider containers.
- **Diagram chat message** inherits the block_edon_ai chat column; the diagram card fills the message width.

## Elevation & Depth

Near-flat. Hierarchy comes from tone (`{colors.surface}` vs `{colors.surface-subtle}`) and hairline borders, not shadow. Two sanctioned shadows: dialogs/overlays (`0 8px 24px rgba(25,28,26,0.16)`) and the sticky publish bar (`0 -1px 0 {colors.border}` plus a faint `0 -4px 12px rgba(25,28,26,0.06)`). The Player uses **no box-shadows at all** — flat rendering is cheaper to paint on old GPUs and sits more quietly inside Moodle's page.

## Shapes

`{rounded.sm}` 4px for chips-in-text, labels, and small controls; `{rounded.md}` 8px for buttons, inputs, and cards; `{rounded.lg}` 12px for posters, dialogs, and the preview overlay; `{rounded.full}` for status chips only. The geometry reads "institutional tool with warmth" — softer than a government form, firmer than a consumer app. Imagery (posters, diagram cards) follows its container radius exactly.

## Components

Visual specs only — behavior lives in `EXPERIENCE.md § Component Patterns` under the same names.

| Component | Visual spec |
|---|---|
| Button set | Primary `{components.button-primary}`; secondary `{components.button-secondary}`; quiet `{components.button-quiet}`; destructive `{components.button-destructive}`. Height 44px (40px in dense authoring toolbars), padding `{spacing.4}` horizontal, `{typography.label}` at 15px. Focus: 2px `{colors.primary}` ring, 2px offset. Disabled: `{colors.ink-disabled}` text on `{colors.surface-subtle}`. |
| Regenerate control | `{components.regenerate-control}` — gold-wash button with a regenerate glyph; the only gold *control* in the system (the wash + `{colors.accent-ink}` text are its identity; the 1px gold border is decorative, not information). While regenerating: label swaps to "Regenerating…" — that swap is the state signal; the optional border sweep is decorative and disappears under `prefers-reduced-motion`. |
| Status chip | `{components.status-chip}`. Variants: Draft (`{colors.surface-subtle}` + `{colors.ink-secondary}`), Published (`{colors.primary-wash}` + `{colors.primary-deep}`), Edited (`{colors.surface}` + border + `{colors.ink-secondary}`), Needs review (`{colors.accent-wash}` + `{colors.accent-ink}`), Check failed (`{colors.error-wash}` + `{colors.error}`). |
| Lesson card | `{colors.surface}` card, `{rounded.md}`, hairline border. Lesson title `{typography.title}`, course + curriculum reference `{typography.caption}` in `{colors.ink-secondary}`, status chips right-aligned, version history line `{typography.caption}` ("v2 current · v1 archived"). |
| Generate form | 640px column. Topic: single-line input, `{typography.body}`. Guidance: 3-row textarea labeled "Guidance (optional)". Course Context rendered as a read-only chip above the fields (`{colors.primary-wash}`, lock glyph) — visibly *given*, never editable; the same chip treatment persists in the Authoring header on every surface. |
| Generation progress card | The showpiece form (stakeholder amendment, 2026-07-17): generation renders as visible block-by-block assembly — an outline column where each Block materializes as the pipeline completes it (type glyph + title skeleton in `{colors.surface-subtle}` → filled row), header stage label `{typography.title}`, elapsed time `{typography.caption}`, `{components.progress-header}`-style bar beneath. When per-Block progress events are unavailable, degrades to the plain card (stage label + bar). Failed state swaps fill to `{colors.error}` and shows the reason in `{typography.body-sm}`. |
| Block rail | Vertical list; each item = index number, Block-type glyph, first words of the Block, status chip (mini). Selected item per `{components.block-rail-item-selected}`. Unseen dot (session-local): 8px `{colors.accent}` fill inside a 1.5px `{colors.accent-ink}` ring — the ring supplies the ≥3:1 boundary that bare gold cannot. Drag handle appears on hover/focus; keyboard reorder buttons always visible when item focused. |
| Block editor | Center pane. Block-type header (`{typography.title}` + glyph), editable fields per type in `{typography.body}`, field labels `{typography.label}`. Non-editable payloads (Diagram SVG, Simulation) render read-only inside a `{colors.surface-subtle}` inset with the Regenerate control adjacent. |
| Citations panel | Stack of `{components.citation-card}` — source title `{typography.body-sm}` semibold, excerpt `{typography.caption}`, chunk metadata `{typography.caption}` in `{colors.ink-secondary}`. |
| Preview overlay | Full-screen overlay, `{colors.ink}` at 60% scrim, white sheet `{rounded.lg}`. Top bar: lesson title, device-width toggle (Phone 360 / Tablet 768 / Full), "Low-spec view" toggle (standard selected treatment, `{colors.primary-wash}` when on — this is a device-simulation control, not AI provenance, so gold is wrong here) with helper text "Shows *what* these devices see — not how fast they see it", Close. Player renders 1:1 inside. |
| Publish dialog | Modal, `{rounded.lg}`. Pre-publish check list: rows with pass (`{colors.primary}` check) / fail (`{colors.error}` cross + reason). Confirm button `{components.button-primary}`; blocked state disables it and keeps failures visible. |
| Notice banner | Full-width banner per `{components.notice-banner-info}` / `-warning` / `-error`; icon left, `{typography.body-sm}`, single action right. Warning (gold) is for budget-pause and AI-attention notices; error for failures; info for confirmations. |
| Player shell | Container-native chrome: top progress header per `{components.progress-header}` (4px track, Block counter `{typography.caption}` — system font in the core bundle, brand font once the lazy fonts chunk lands: standard on all capable devices, not Showcase-gated, per `{typography.player-ui}` re-amendment 2026-07-18), bottom nav bar with Back (quiet) / Next (`{components.button-primary}`, min 48px tall). No shadows; core bundle webfont-free per `{typography.player-ui}`; palette only. **Tiered motion budget** (amended 2026-07-17): on Full/Constrained/Floor, no continuous animation — skeletons are static `{colors.surface-subtle}` blocks (no shimmer), the progress fill steps rather than tweens, no Block-transition effects. On **Showcase**, the motion language applies: purposeful ≤300ms Block transitions, animated (shimmer) skeletons, stepped-to-smooth progress — all delivered in the lazy enhancement chunk, all suppressed by `prefers-reduced-motion`, and none of it ever touching gold governance elements. |
| Slide block | Reading column ≤720px, system-font ramp mirroring `{typography.body}` at 17px on phones. Headings in semibold system font, `{colors.ink}`. |
| Narration control | Compact bar under the slide heading: play/pause (48px target per the Player floor — corrected 2026-07-18), elapsed dots, "Show text" toggle. Uses `{colors.primary}` glyphs on `{colors.surface}`; active state `{colors.primary-wash}`. Transcript renders as normal body text below. |
| Quiz block | Question `{typography.body}` semibold; options as full-width tappable rows (min 48px, `{rounded.md}`, hairline border). Selected: `{colors.primary-wash}` + `{colors.primary-deep}` border. Correct feedback `{components.quiz-option-correct}` + check glyph; incorrect `{components.quiz-option-incorrect}` + cross glyph, and the correct answer is then marked with a check glyph and the text prefix "Correct answer" — never outline alone. Feedback text `{typography.body-sm}`. Showcase only: a brief green-family celebratory micro-interaction on a correct submission (check-draw + subtle `{colors.primary-wash}` pulse, ≤600ms, once per question) — never gold, never copy hype, suppressed by `prefers-reduced-motion`. |
| Diagram block | Sanitised SVG on `{colors.surface}`, `{rounded.md}` hairline frame, caption `{typography.caption}`. (Lesson diagrams passed the Review Gate — no AI label here.) |
| Model3D viewer | Viewer canvas inside `{rounded.lg}` frame; orbit/zoom hint chip bottom-left (`{colors.ink}` 70% on white pill); annotation markers: 24px `{colors.primary}` dots with white numerals inside ≥48px hit areas; control row beneath the canvas — rotate ◀ ▶ ▲ ▼, zoom ±, reset, annotations toggle — as 48px secondary buttons (Player floor — corrected 2026-07-18); annotation text in a `{colors.surface-subtle}` panel below the canvas. Showcase hero entrance: the model fades in and performs a slow ~2s auto-orbit before settling to rest — entirely inside the reserved media box, suppressed by `prefers-reduced-motion`. |
| Simulation frame | Sandboxed iframe inside `{rounded.lg}` frame on `{colors.surface-subtle}`; parameter controls (sliders/inputs) rendered by the simulation; a thin header strip names the simulation `{typography.caption}`. |
| Poster fallback card | `{components.poster-fallback-card}` — poster image top (container radius), caption bar below: block title `{typography.body-sm}` semibold + one-line explanation `{typography.body-sm}` + optional "Load 3D model (4.2 MB)" secondary button. Styled exactly like content, never like an error (no red, no warning icons). |
| Sources section | Collapsed section at lesson end: "Sources" `{typography.title}`-equivalent in system font, list of `{components.citation-card}` at lesson level. |
| AI content label | `{components.ai-content-label}` pinned to the top-left of chat diagram cards: "AI-generated — verify against your course materials". Never removable, never truncated. |
| Diagram chat message | Chat bubble containing: AI content label, sanitised SVG (white card, `{rounded.md}`), caption row with "Report this diagram" quiet-destructive text button — `{typography.body-sm}` label on a ≥48px hit area per the Player/chat target floor (corrected at readiness sign-off 2026-07-18; it is the FR-28 governance control, not metadata). |
| Diagram review queue row | Table row: thumbnail (40px), request text `{typography.body-sm}`, report count chip, date `{typography.caption}`, two actions: "Mark reviewed" secondary button + "Mark invalid" destructive button (`{components.button-destructive}`, confirm required). Queue entry in the header nav carries a count badge (`{colors.primary}` pill, white numeral) when non-empty. |
| Empty state | One branded pattern for every empty surface: `{typography.display-sm}` headline (system-font equivalent in the Player), one-sentence body `{typography.body}`, single primary action, and a subtle brand accent — an inline SVG geometric motif in `{colors.primary-wash}`/`{colors.border}` (no raster, no mascots, byte-cheap). Never a blank region, never gold. |
| Completion summary | Card at lesson end: "Lesson complete" heading (system font semibold), tick list of Blocks with `{colors.primary}` check glyphs, score status line `{typography.body}`, attempts line `{typography.body-sm}` in `{colors.ink-secondary}`, jump-back links as quiet buttons. Missing items render in the same list with hollow markers + jump links — never error styling. |

## Do's and Don'ts

| Do | Don't |
|---|---|
| Reserve gold for AI-awaiting-judgment states (regenerate, unreviewed, AI labels, budget warnings) | Use gold decoratively, for celebration, or as text/hairlines on white (1.7:1 — fails) |
| Pair every gold or gold-wash fill with `{colors.accent-ink}` text | Put white or green text on gold |
| Use green for actions, selection, progress, and settled/confirmed states | Introduce a second success color or color-code block types |
| Style poster fallbacks as first-class content cards | Style fallbacks as errors (red, warning triangles, "failed to load") |
| Keep the *core* Player bundle flat and lean: system fonts, no shadows, no webfonts, no imagery beyond lesson assets | Load Inter/Plus Jakarta Sans, icon fonts, motion libraries, or CSS frameworks inside the core Player bundle — Showcase polish ships only as lazy enhancement chunks |
| Scope all showcase motion to the Showcase tier, keep celebration in the green family, and suppress every animation under `prefers-reduced-motion` | Let motion touch, imitate, or compete with gold governance signals — or animate anything on Full/Constrained/Floor tiers |
| Let the Player inherit the Moodle page's scroll and width | Fix-position Player chrome to the viewport or override Moodle page styles |
| Keep authoring forms narrow (≤640px) and plain-labeled | Expose prompt-engineering affordances (temperature, model pickers, token counts) |
| Meet AA contrast on every text/fill pair listed in § Colors | Use `{colors.ink-disabled}` for running text or captions |
