# External Interface: mod_edonlesson ↔ Platform API (v1)

**Status:** draft — pending stakeholder sign-off of the architecture run 2026-07-17
**System:** `mod_edonlesson` — thin companion Moodle activity module (separate repo, GPLv3). All proprietary logic stays platform-side; the module is a client of the endpoints below plus Moodle's own grade/completion/task APIs.
**Posture:** this is the **LMS-agnostic platform API** (V3 seam f). Nothing in it is Moodle-specific; Moodle specifics (gradelib, completion API, scheduled tasks, activity settings) live only in the plugin. LTI 1.3 later means a new consumer of these same endpoints, not new platform core.

## 1. Authentication

- Server-to-server only, over TLS: per-Tenant API key (`Authorization: Bearer <key>`), stored in the plugin's Moodle admin settings, matching the existing block_edon_ai / edon-rag pattern (FR-24).
- Keys are hashed at rest platform-side; **two keys may be valid per Tenant concurrently** so rotation is issue-new → switch plugin setting → revoke-old, with no downtime (NFR-3).
- The Student/Teacher browser never holds a tenant key. Browser-facing credentials are only the short-lived tokens minted by these endpoints.
- Per-tenant CORS: the platform allows the tenant's Moodle origin (from tenant config) for the browser-facing Player/Authoring calls that follow session minting. No wildcard (project-context §4 [HARD]).

## 2. Endpoints consumed by mod_edonlesson

### 2.1 Lesson picker — `GET /api/v1/lessons?course_ref={ref}&published=1`
Lists the Tenant's Published Versions for the activity-settings picker (latest version per Lesson): `[{lesson_id, title, curriculum_ref, latest_version, published_at, has_quiz, quiz_max_points}]`. `curriculum_ref` is the flat string value (the Teacher override wins when `source: "teacher"` — AD-2's `curriculumRef` object never crosses this API). `course_ref` optional — omitted, returns Tenant-wide list (College-library parity, OQ-13). Teacher attempt limits and completion options are **Moodle activity settings**, configured in the picker form and kept plugin-side; they reach the platform per playback session (2.3).

### 2.2 Authoring launch — plugin-minted Launch Token (no platform call)
The plugin mints the FR-29 Launch Token **itself**, signing JWT HS256 with the per-Tenant signing secret from its admin settings (distinct from the API key; also dual-valid for rotation):

- Header: `{alg: "HS256", kid: "<key id>"}`
- Claims: `iss` (platform tenant id), `sub` (Moodle user id), `role` (`teacher` | `tenant_admin`), `course_ref`, optional `draft_hint`, `iat`, `exp = iat + 120s`, `jti` (UUID).
- Launch URL: `https://<platform>/authoring/launch#token=<jwt>` opened in a **new tab** (UX-confirmed). Fragment, not query, so the token never lands in server logs.
- The platform exchanges the token exactly once (`jti` replay-protected) for an Authoring Session cookie: 8 h absolute lifetime; expiry lands on the Relaunch notice; relaunch returns the Teacher to their last-active Draft.

### 2.3 Playback session — `POST /api/v1/playback-sessions`
Called by the plugin **server-side** when a Student opens the activity:

```json
{
  "lesson_id": "…",
  "lms_user_id": "moodle user id",
  "lms_user_role": "student",
  "course_ref": "…",
  "activity_ref": "opaque plugin instance id",
  "attempt_limit": 3,
  "completion_required": true
}
```

Response: `{player_bundle_url, script_url, playback_token, display: {attempts_used, attempt_limit, completion_state}}`.

- **The session response is for the plugin's own display only** (activity page furniture). It is never re-serialized into the page for the Player: the Player's first act after mount is `GET /api/v1/playback/bootstrap` (playback-token-authed), which is the single carrier of the pinned script URL, attempt identifiers, `resume` state (position as Block id, viewed Blocks, per-Block submission state, attempts), `feature_flags`, `governance_state`, `observer`, and `tier_hints` (AD-22).
- `playback_token` is a short-lived bearer (24 h) scoping all Player→platform calls (bootstrap, view marks, quiz submissions) to `(tenant, user pseudonym, lesson, activity_ref)`. Attempts, limits, and completion are scoped to `(lesson_id, activity_ref)` — the same Lesson in two activities never cross-blocks (AD-15).
- Non-student launches mint `observer: true` sessions: the Player runs read-only (no-op sink); no attempts or outbox rows are created.
- Version pinning: an open attempt pins its Published Version (A-4/OQ-15); a fresh run gets the latest. The bootstrap's script URL reflects that rule — the plugin does not implement it.
- The plugin embeds the Player: `<div id="edon-lesson"></div>` + `<script src={player_bundle_url}>` + `EdonPlayer.mount(el, {scriptUrl, token, locale})` — the canonical, complete mount call. Same-page embed, self-managed height (Moodle Embedding Contract).

### 2.4 Delivery outbox — grades and completion (pull + ack)
The platform is the system of record for attempts (server-authoritative scores, FR-15). Delivery to the LMS is an **outbox** the plugin drains from a Moodle scheduled task (default every 5 min; retries are simply the next run — A-13, SM-3's 24 h window):

- `GET /api/v1/outbox?kinds=grade,completion&limit=100` → `[{delivery_id, kind, activity_ref, lms_user_id, payload}]`
  - `grade` payload: `{lesson_id, attempt_no, score_fraction, best_fraction}` — plugin writes `best_fraction × grademax` via Moodle's Gradebook API (highest attempt, OQ-15).
  - `completion` payload: `{lesson_id, completed_at}` — plugin marks completion via the completion API.
- `POST /api/v1/outbox/ack` `{results: [{delivery_id, status: "applied" | "failed", error_code?}]}` — idempotent. `applied` completes the delivery; `failed` emits the platform `writeback_failure` event and leaves the row for redelivery (which emits `writeback_retry`); unacked rows are simply redelivered next run. Plugin-side writes are idempotent per `(activity_ref, lms_user_id, kind, attempt_no)`.

Rationale: outbound-only HTTP from Moodle (no inbound firewall holes into institutional Moodle hosting), LMS-agnostic platform, and native Moodle retry semantics via the Task API.

## 3. Error semantics
`401/403` invalid or revoked key → plugin surfaces its standard "service unavailable" string and logs; `404` unknown lesson (unpublished/deleted) → the activity shows the FR-12 "not available" state; `429` → task backs off to next run; `5xx` → retriable. The plugin never renders raw platform errors to users.

## 4. Work items (plugin-side, registered — not platform gaps)
- **WI-MOD-1**: plugin scaffolding — activity module with picker (2.1), settings (API key, signing secret, platform URL), capability checks mapping Moodle roles → `teacher`/`tenant_admin`/`student`.
- **WI-MOD-2**: scheduled task draining the outbox (2.4) + gradebook/completion writes + ack.
- **WI-MOD-3**: launch-token minting for the teacher entry point (2.2), new-tab launch, Moodle-mobile-app browser hand-off screen (UX ruling 14).
