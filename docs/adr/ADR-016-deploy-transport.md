# ADR-016: Deploy Transport — Operator-Initiated rsync over SSH

**Status:** Accepted (stakeholder decision, 2026-07-19 — Story 1.2)
**Reserved by:** spine § Deferred ("Deploy mechanics — first epic, with the CI provider"); AR-26.

## Context

The single-VPS systemd topology is fixed (spine § Deployment); only the transport was open: rsync, registry-based images, or a CI runner pushing to the VPS. Two constraints decide it: (1) stakeholder policy (2026-07-19, standing): AI/dev sessions never hold production credentials, and (2) the threat model's least-privilege principle — a GitHub or Actions compromise must not become a VPS compromise.

## Decision

**Operator-initiated rsync over SSH** via `deploy/deploy.sh`: the operator (john) runs the script from a machine holding SSH access; it rsyncs the git-tracked tree, syncs the Python environment from the committed `uv.lock` (`uv sync --frozen`), restarts units, and health-checks. CI's role ends at verification — it produces a green commit, never a deployment.

## Consequences

- No deploy secrets in GitHub: nothing for a compromised workflow or action to exfiltrate (threat model S9/T9.3).
- Deploys are deliberate operator actions with a human in the loop — consistent with the review-gate culture of the product itself.
- Downtime posture: `systemctl restart` implies seconds-level interruption; acceptable for staging and the ≤ 5-college pilot. Zero-downtime reloads (socket activation / dual-instance) are a pre-launch hardening decision, not taken now.
- Frontend build artifacts (player/authoring bundles, from Epic 2+/4+) ride the same rsync: built by the operator via the repo's build scripts before deploy; if that proves clumsy, a CI artifact-download step (still operator-pulled, still credential-free toward the VPS) is the revisit path.
- Rollback = `git checkout <previous tag>` + re-run the script (runbook §6).
