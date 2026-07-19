# Block Types — Renderer Specification

This document specifies every field a renderer needs, per block type, sufficiently to
implement rendering **against this package alone** (FR-3). Field casing is camelCase
throughout. All examples are drawn from `fixtures/valid/full-six-block-lesson.json`.

## Lesson envelope

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `schema` | string `"MAJOR.MINOR"` | yes | Contract version. See [versioning.md](versioning.md) for mismatch behaviour. |
| `lessonId` | string | yes | Stable lesson identity (UUID). |
| `tenantId` | string | yes | Owning tenant. Never rendered; drives isolation. |
| `courseRef` | string | yes | Opaque LMS-agnostic course reference. |
| `curriculumRef` | object `{value, source}` | yes | Curriculum line shown on Lesson cards. `source` is `"pipeline"` (derived) or `"teacher"` (corrected in review — a Teacher edit flips it). |
| `version` | integer ≥ 0 | yes | `0` = Draft (pre-publish); publish stamps `n ≥ 1`, immutable thereafter. |
| `title` | string | yes | Lesson title (Player top bar, Lesson card). |
| `language` | string (loose BCP-47) | yes | One lesson-level tag. Renderers set `lang` on content regions from it; narration voice preference follows it. |
| `blocks` | array | yes | **Ordered** — playback order is the array order (FR-13). |

## Base block envelope (every block, including unknown future types)

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `id` | string | yes | Stable slot id minted at plan stage (AD-23). View marks, submissions, citations, progress rows all key on it. Never regenerate or reindex. |
| `type` | string | yes | Renderer selector (BlockRegistry key). Unknown values: omit the block from sequence and counts — no gap card, no error. |
| `title` | string | yes | Block heading. Rendered as a real heading element (focus target on navigation); used in the rail, "Block n of N — {title}" announcements, and the completion tick list. |
| `citations` | array of citation | yes (may be empty) | Per-block provenance. Teachers see them per block; Students see only the lesson-level aggregated "Sources" list. |

### Citation object

| Field | Required | Semantics |
| --- | --- | --- |
| `sourceChunkId` | yes | Grounding Chunk id at generation time. Display metadata only — never dereference back to the retrieval service for rendering. |
| `documentTitle` | yes | Source document title (citation card heading). |
| `excerpt` | yes | The grounded text excerpt. With `documentTitle`, this is the integrity anchor inside immutable Published Versions. |
| `locator` | no (nullable) | Human position string, e.g. `"Page 6"`. Render only when present and non-null. |
| `documentId`, `tags` | no | Optional source metadata. |

### assetRef object (every heavy-asset reference)

| Field | Required | Semantics |
| --- | --- | --- |
| `ref` | yes | `asset://{asset_id}` stable id, resolved to a URL at delivery (Draft live paths or the frozen publish manifest). Renderers never construct URLs themselves. |
| `transferSize` | yes | Compressed transfer size in **bytes**. The only field tap-to-load labels ("Load 3D model (4.2 MB)") and tier ceilings read. |

### poster object (Model3D and Simulation)

| Field | Required | Semantics |
| --- | --- | --- |
| `image` | yes (assetRef) | Poster image. The instant first paint while the heavy asset arrives, the degraded-tier render, and the flag-off render. A block in poster state **counts as viewed**. |
| `altText` | yes | Short text alternative (text-alternative contract; Teacher-editable). |
| `longDescription` | no | Extended description for labelled technical content. |
| `caption` | yes | One-line explanation naming what the full asset shows — the poster must stand alone pedagogically. |

## `slide`

| Field | Required | Semantics |
| --- | --- | --- |
| `body` | yes | Markdown-subset string. Renders instantly; text is never behind a loader. |

**Markdown subset (exact):** paragraphs, headings (`##`, `###`), `**bold**`, `*italic*`,
ordered and unordered lists. **Forbidden:** images, raw HTML, links. Renderers **strip or
ignore disallowed constructs — never error, never render them raw.**

## `narration`

| Field | Required | Semantics |
| --- | --- | --- |
| `text` | yes | The transcript — always available, the primary modality. Rendered as real selectable text. |
| `audioRef` | no (assetRef) | Publish-time TTS audio. When present, pre-generated audio is the primary playback source; when absent, SpeechSynthesis fallback; when neither is usable, transcript shows by default and the play control is hidden. Never autoplay. |

## `quiz`

| Field | Required | Semantics |
| --- | --- | --- |
| `questions` | yes, min 1 | Ordered question list. |

Per question: `id` (required), `type` (`"multipleChoice"` | `"shortAnswer"`), `prompt`
(required), `feedback` (required — shown after the question is answered, announced via
`role="status"`, programmatically associated with its question group).

- **multipleChoice:** `options` (min 2, each `{id, text}`, rendered as a radio group) and
  `correctOptionId` (must reference an option id — the validators enforce this). After
  answering, mark the correct option with a check glyph and the text prefix "Correct answer".
- **shortAnswer:** `acceptedAnswers` (min 1, non-empty strings). Matching is normalised
  (case/whitespace/punctuation) in Player and server code — the list here is the
  Teacher-approved source of truth.

Scoring: **1 point per question**; scores are `earned/possible` fractions. Answers
necessarily ship with the Published Version for instant client feedback (accepted
formative-stakes trade-off); the server re-score is authoritative.

## `diagram`

| Field | Required | Semantics |
| --- | --- | --- |
| `svg` | yes | Sanitised SVG markup, stored **inline** (byte-exact review-gate integrity — ratified 2026-07-18). Scale to container width; provide an in-container "View larger" affordance. Sanitisation preserved `<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby`. Lesson diagrams passed the Review Gate — no AI label. |
| `altText` | yes | Short text alternative. |
| `longDescription` | no | Extended description for labelled technical diagrams. |
| `caption` | no | Caption line under the diagram. |

## `model3d`

| Field | Required | Semantics |
| --- | --- | --- |
| `modelRef` | yes (assetRef) | Curated-library glTF asset. Render in an orbit/zoom viewer with full button equivalents and a focusable canvas. The attribution/licence line renders from **asset metadata** (library registry / publish manifest) — deliberately not duplicated in the script. |
| `poster` | yes (poster) | First paint + degraded/no-WebGL path. |
| `annotations` | yes (may be empty) | Numbered markers: `{number ≥ 1, text, anchor {x,y,z} optional}`. Render markers on the canvas when anchored; always render the annotation text panel (every tier — Constrained/Floor show poster + annotations as a text list). |

## `simulation`

| Field | Required | Semantics |
| --- | --- | --- |
| `mode` | yes | `"template"` (launch default) or `"freecode"` (tenant-flag-gated). Identical sandbox + protocol for both. |
| `templateId` | required iff `mode: "template"` | Template-library entry to instantiate. |
| `bundleRef` | required iff `mode: "freecode"` (assetRef) | Generated simulation bundle. |
| `name` | yes | Shown in the frame's thin header strip; the iframe's accessible title. |
| `params` | yes (may be empty) | AD-12 descriptor array: `{id, label, type, min, max, step, default}` (`id`, `label`, `type` required). The postMessage protocol relays these; every param must map to a keyboard-operable native control (checked pre-publish). |
| `paramsDescription` | yes | Prose description of the parameters — the Floor-tier text alternative beside the poster. |
| `poster` | yes (poster) | First paint, bounded-wait fallback, flag-off render. |

Sandbox law (renderer side): `iframe sandbox="allow-scripts"`, CSP `default-src 'none'`,
communication only via the postMessage protocol (protocol document ships separately in
`/schema` — Story 10.1; it, not this file, pins the message set).
