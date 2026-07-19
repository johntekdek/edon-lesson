# ADR-015: CI Provider — GitHub Actions

**Status:** Accepted (stakeholder decision, 2026-07-19 — Story 1.2)
**Reserved by:** spine § Deferred ("CI provider — first epic"); AR-26.

## Context

The spine deferred the CI provider as a repo-host operational choice: budgets, tests, and gate scripts are CI-agnostic files, so the provider does not shape the architecture. Story 1.1 shipped its minimal workflow on GitHub Actions as the spine's working assumption; the implementation-readiness sign-off (2026-07-18) confirmed that assumption; the stakeholder ratified it with the Story 1.2 decisions (2026-07-19) alongside the move of the repo to a private GitHub remote.

## Decision

**GitHub Actions**, on the private GitHub repo that hosts the monorepo. Two workflows: `ci.yml` (correctness gates) and `security.yml` (dependency audits + secret scan, also on a weekly schedule). Dependabot provides update automation for `npm`, `uv`, and `github-actions` ecosystems.

## Consequences

- Repo hosting, CI, Dependabot, and branch protection live in one place with one auth domain.
- Every workflow carries a top-level least-privilege `permissions: contents: read` block; any job needing more escalates explicitly at job level (threat model S9).
- CI holds **no VPS or production credentials** — deploys are operator-initiated (ADR-016); a GitHub/Actions compromise cannot reach production.
- All gate logic stays in repo-local scripts (`tools/`), so a future provider move is workflow-file translation only.
- Branch protection (require CI green on `main`) is applied by the stakeholder post-merge via the documented `gh` command (deploy runbook §7) — sessions hold no repo-admin rights.
