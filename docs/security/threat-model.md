# Threat Model — e-DON Lesson Studio

**Status:** living document — seed. Extend as new surfaces are built; every critical-tier story's review checks its code against the relevant scenarios below.

## Primary adversary

The primary adversary is an **authenticated student**: legitimate credentials, inside the system, motivated (grades), patient (a full term), and willing to inspect network traffic, read client code, replay requests, and hand-edit anything the client touches. Secondary adversaries — a malicious teacher within a tenant, a compromised tenant credential, an external unauthenticated attacker — are in scope but lower-likelihood. Design for the student first; the rest largely follows.

**Governing assumption:** anything delivered to the client (scores, answer keys, tokens, lesson JSON, simulation code) is fully visible and modifiable by the student. Client-side checks are UX, never security. Every security decision is enforced server-side.

## Attack scenarios by surface

### S1 — Grades and quiz scoring
- **T1.1** Forge a high score by crafting/replaying the submission request directly.
- **T1.2** Resubmit or double-submit to overwrite a lower attempt or exceed attempt limits.
- **T1.3** Tamper with the answer payload to have client-side "correct" mismatch server truth.
- **T1.4** Race two concurrent submissions to corrupt attempt state or gradebook writeback.
- **Controls:** server-authoritative rescoring against the published script; idempotent single-fire submit, first-ack-wins; attempt pinned to published version; transactional submit + rescore + outbox in one commit. *Accepted by design (A-21):* formative quizzes expose answers client-side — reading one's own key is not a breach; forging the recorded grade is what's blocked.

### S2 — Tenant and course isolation
- **T2.1** Access another course's lessons, drafts, or assets by changing an id in a request.
- **T2.2** Reach another tenant's data (the 60-college cross-bleed — highest-severity outcome).
- **T2.3** Read teacher-only material (unpublished drafts, answer keys, citations) as a student.
- **Controls:** PostgreSQL row-level security so cross-tenant access is impossible by construction, not by application-layer checks; course scope derived from the (server-verified) launch token, never from client-supplied ids; draft visibility owner/role-scoped.

### S3 — Launch tokens and sessions
- **T3.1** Replay a captured launch token to mint a session later.
- **T3.2** Forge or alter token claims (tenant, course, role, user) to escalate or impersonate.
- **T3.3** Extend or reuse an authoring session beyond its lifetime.
- **Controls:** single-use, 120-second, signed tokens; server-side signature + claim verification; bounded authoring session; relaunch re-mints rather than reusing.

### S4 — AI-generated content as an XSS/injection vector
- **T4.1** Student-requested diagram returns SVG carrying script/event-handler/foreignObject that executes in another user's browser.
- **T4.2** A stored lesson field renders unsanitised and executes.
- **T4.3** Prompt-shaped input to the diagram channel coaxes the model into emitting hostile markup.
- **Controls:** allowlist-based SVG sanitisation (strip script, event handlers, foreignObject, external refs) before persist; sanitise-then-freeze so the immutable published copy is the reviewed copy (no swappable asset); the student diagram channel is the ONE review-gate bypass — it carries mandatory grounding, sanitisation, quotas, rate limits, the AI-generated label, and the report→review→cache-evict loop.

### S5 — Simulation sandbox escape
- **T5.1** Generated (or, behind the flag, free-coded) simulation code breaks out of its frame to read the parent page, tokens, or other lessons.
- **T5.2** Simulation makes network calls to exfiltrate data or attack internal services.
- **T5.3** Simulation abuses postMessage to forge results or completion.
- **Controls:** sandboxed iframe, no network, strict CSP, no storage APIs; a defined postMessage protocol with server-side validation of anything it reports; headless pre-publish check harness gating what code may ship; template-first (free-code only behind a tenant flag after the ≥70% gate).

### S6 — Cost / denial-of-wallet
- **T6.1** A student spams the diagram channel to burn tenant LLM budget.
- **T6.2** Automated request floods to exhaust generation capacity.
- **Controls:** per-student diagram quotas and rate limits; per-tenant budget ceilings enforced at the adapter layer (a [HARD] rule), with cache-only degradation and no silent failure on exhaustion; generation concurrency bound.

### S7 — Credentials and secrets
- **T7.1** Extract a tenant edon-rag key or platform secret from client, logs, or error output.
- **T7.2** Use a stale/revoked key after rotation.
- **Controls:** platform secrets env-only; per-tenant credentials as hashed/KEK-encrypted rows; key rotation (issue/revoke without downtime) from day one; no secrets in logs or error bodies; tenant-scoped error logging, never raw to users.

### S8 — Privacy / data protection (NDPA)
- **T8.1** Student PII leaks to an external LLM provider via a prompt.
- **T8.2** Identifiable data lands in telemetry or logs.
- **Controls:** structural identity-stripping before any LLM/adapter call (no student identity crosses that boundary); pseudonymised ids in telemetry; defined log retention; maintained processor record.

### S9 — Supply chain and CI (added Story 1.2, stakeholder opt-in 2026-07-19)
- **T9.1** Malicious or vulnerable dependency version enters via either ecosystem (typosquat, dependency confusion, compromised upstream).
- **T9.2** A compromised third-party GitHub Action tampers with builds or exfiltrates repository tokens.
- **T9.3** An over-scoped CI token turns a workflow compromise into repo tampering or infrastructure access.
- **T9.4** A secret committed to history is harvested later (by anyone with repo read — including a future contributor's leaked clone).
- **T9.5** Lockfile drift — floating or unpinned dependencies make builds non-reproducible and un-auditable.
- **Controls:** committed lockfiles (`package-lock.json`, `uv.lock`) are the only install paths; `npm audit` (high/critical) + `pip-audit` (any known vuln) blocking in CI, plus a weekly scheduled run so new advisories surface without commits; Dependabot update automation (npm, uv, github-actions); gitleaks full-history secret scan, blocking; every workflow defaults to `permissions: contents: read` with explicit job-level escalation only; CI holds **no** VPS/production credentials — deploys are operator-initiated (ADR-016), so GitHub compromise ≠ infrastructure compromise; the licence-audit gate doubles as a provenance tripwire (an unexpected licence flags an unexpected package).

## Cross-cutting principles

1. **Server is the only authority.** Client output is never trusted for a security decision.
2. **Isolation by construction, not by check** — RLS and sandboxing over application-layer guards where possible.
3. **The review gate is the safety spine.** Its one sanctioned bypass (student diagrams) is the most heavily controlled surface in the system.
4. **Fail loud, fail closed.** Budget exhaustion, writeback failure, and sanitisation failure surface as visible, safe states — never silent pass-through.
5. **Assurance ladder:** critical-tier stories built on the strongest model; adversarial red-team review sessions at the M2/M3/M4 gates; one professional human penetration test before the pilot admits real students.
