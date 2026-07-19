# External Interface: block_edon_ai ↔ Platform Diagram API (v1)

**Status:** final (stakeholder sign-off, 2026-07-18)
**System:** `block_edon_ai` — the existing production Moodle AI-chat plugin, a modifiable companion (stakeholder decision, OQ-12). Its enhancement is a registered third-repository work item with a **minimal surface**: call the endpoint below and render what comes back. Sanitisation, caching, Quotas, Rate Limits, grounding, and identity-stripping all stay platform-side.

## 1. Authentication
Same pattern as mod_edonlesson: per-Tenant API key in `Authorization: Bearer`, server-to-server from the plugin's PHP backend (the Student browser never calls the platform directly and never holds the key). Dual-valid keys for rotation.

## 2. Endpoints

### 2.1 `POST /api/v1/diagrams`
Synchronous request/response (the chat shows its "Drawing your diagram…" state while waiting; platform deadline 60 s).

Request:
```json
{
  "request_text": "labelled diagram of the human heart",
  "lms_user_id": "moodle user id",
  "course_ref": "required — retrieval is course-scoped (edon-rag contract v1.1)"
}
```

`lms_user_id` is used **only** for Rate Limits, Quotas, and pseudonymised telemetry — it is stripped before any retrieval or LLM call (NFR-9). The platform pseudonymises it per-tenant before storage.

Response `200` — one of `status` values, always with humane copy fields the plugin renders verbatim (Voice-and-Tone templating happens platform-side from tenant config):

```json
{
  "status": "served",           // served | rate_limited | quota_exhausted | budget_paused | failed
  "diagram_id": "…",
  "svg": "<svg …sanitised…>",
  "alt_text": "…",
  "long_description": "…",
  "label": "AI-generated — verify against your course materials",
  "cached": false,
  "message": null                // set on non-served statuses: user-facing chat reply text
}
```

- `served`: sanitised SVG (already passed the FR-20 allowlist gate; `<title>`/`<desc>`/`aria-*` preserved). The plugin renders it in the diagram card with the mandatory `label` and the Report control. Cache hits return instantly with `cached: true` and are never rate-limit-charged (OQ-2).
- `rate_limited` / `quota_exhausted` / `budget_paused` / `failed`: `message` carries the exact user-facing string (interpolated from Tenant config — e.g. quota `{n}`, retry window). The plugin posts it as a normal chat reply; the chat never errors technically.

### 2.2 `POST /api/v1/diagrams/{diagram_id}/report`
```json
{ "lms_user_id": "…", "note": "optional" }
```
`204`. Emits the FR-27 `diagram_reported` event and enqueues the diagram in the Teacher review queue (FR-28). Idempotent per (diagram, user): repeat reports return `204` without duplicate queue entries. The plugin then disables its Report control for that message.

## 3. Feature flag
If the Diagram feature is flagged off for the Tenant, `POST /api/v1/diagrams` returns `403 {status: "disabled"}`; the plugin hides the diagram affordance entirely (it may probe via tenant config endpoint `GET /api/v1/features` at page load, cached plugin-side for 5 min).

## 4. Live Q&A — course-scoped chat embed (stakeholder amendment, 2026-07-18)

The lesson activity page presents the **existing block_edon_ai chat**, scoped to the launch course, alongside the embedded Player — the MVP's Live Q&A surface. This rides the chat's existing edon-rag pipeline: **no new inference economics** (I-1 untouched), NFR-9 identity-stripping unchanged. The Player itself does not implement chat; the plugin/page composition places the chat surface with the activity (presentation details are a UX/plugin story concern within the Moodle Embedding Contract — the chat must not break the Player's style isolation).

## 5. Work items (plugin-side, registered)
- **WI-CHAT-1**: diagram request affordance + diagram card rendering (SVG, label, alt text, "View larger" link, Report control) per the UX Diagram chat message spec.
- **WI-CHAT-2**: status-message pass-through (chat replies for limit/quota/budget/failure states) + live-region announcement via the chat's existing mechanism.
- **WI-CHAT-3**: feature-flag probe + hide behavior.
- **WI-CHAT-4** (2026-07-18): course-scoped chat presence on the mod_edonlesson activity page (Live Q&A beside the Player), per §4. Lands in milestone M4 with diagrams.
