# ADR-012: Object Storage and Published-Asset Self-Containment

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
project-context §2: object storage for lesson assets with tenant-scoped path prefixes. V3 seam (e): published-lesson assets static and self-containable (offline/SCORM export a cheap fast-follow). Single-VPS launch; no AGPL runtime dependencies (§5 — which rules out MinIO as the default choice).

## Decision
- A minimal **StorageDriver port**: `put / get / stream / delete / exists / url_for(internal)`. Launch driver: **VPS filesystem** at `/var/lib/edon-lesson/assets/`, served by nginx via `X-Accel-Redirect` after platform authorization (tenant + session checks happen in the app; nginx only streams). An **S3-compatible driver** is the documented scale-out swap (any S3 API provider; SeaweedFS noted as a permissively-licensed self-hosted option). MinIO is deliberately not the default (AGPL).
- **Path law:** `tenants/{tenant_id}/…` is the first segment of every key, produced by one helper requiring `TenantContext` (ADR-008). Layout: `…/library/models/{asset_id}/`, `…/lessons/{lesson_id}/draft/{…}`, `…/lessons/{lesson_id}/v{n}/{…}`, `…/diagram-cache/{key}.svg`, `…/sim-templates/{template_id}/v{n}/`.
- **Publish freeze:** publishing copies (hardlink on the filesystem driver) every asset the Draft references into the immutable `…/lessons/{lesson_id}/v{n}/` prefix and writes `manifest.json` (paths, byte sizes, content hashes, licence/attribution records for Model3D). The Published Version references only frozen paths — deleting or re-ingesting library assets can never break a published lesson (I-3/NFR-4), and `v{n}/` + script + player bundle **is** the future SCORM/offline package.
- Curated Model Library ingest pipeline (operator CLI, ours): fetch → licence metadata capture (mandatory field, §5; the index also carries `curriculum_tags` — FR-16's curriculum mapping) → Draco optimization via **@gltf-transform 4.4.x** (MIT — verified at repo LICENSE and npm for the pinned version on 2026-07-18; the early-v4 Prosperity relicensing was reverted, and the CI licence-audit gate re-verifies on every upgrade) → poster render capture (deterministic viewer screenshots of the asset itself — never AI-generated imagery) → size-budget gate (`budgets.json`) → library index row.
- Backups: nightly `pg_dump` + filesystem asset rsync to off-VPS storage; both are one systemd timer each (ops runbook in `/docs`).

## Consequences
- No new stateful service to operate at launch; the storage swap is config + driver, invisible to domain code.
- Hardlink freeze makes republish storage-cheap (unchanged assets share inodes).
- Disk capacity is a monitored ops metric (events sized ~nothing; assets dominated by the Model Library and simulation bundles).
