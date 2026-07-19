# ADR-002: Launch Model Selection — Benchmark Plan per Workload

**Status:** Accepted (stakeholder sign-off, 2026-07-18). This ADR fixes the *plan*; the *winners* are recorded as a dated addendum to this ADR when the benchmark runs (a pre-launch work item), and land in configuration only — never code.
**Reserved by:** project-context.md §3; PRD addendum §1. Constraint: benchmark the leading frontier tier on the actual pipeline; do not default to GPT-4o out of habit.

## Workload keys under benchmark

| Workload | What runs | Selection posture |
| --- | --- | --- |
| `lesson_generation` | Full pipeline: plan → per-Block content → validation | Quality-first, then cost |
| `simulation_generation` | Simulation code/params stage + sandbox checks | Quality-first (highest-variance feature); also decides the OQ-5 mode default |
| `diagram_generation` | Structured SVG/Mermaid diagram emission | Cost-first among models clearing the quality bars |
| `tts` (added 2026-07-18, stakeholder amendment) | Publish-time narration audio via the adapter's OpenAI-compatible speech surface | Selected at M2 via a small voice-quality/cost bench (naturalness for Nigerian-English listeners as a rubric criterion; cost per published lesson); full Cost Telemetry like every workload |
| `embeddings` | — | **Not benchmarked.** Fixed: existing Ollama `nomic-embed-text` inside edon-rag, unchanged (project-context §3). |

## Candidate matrix (GA API models, verified against vendor pages 2026-07-17)

Frontier (`lesson_generation`, `simulation_generation`):

| Vendor | Model | $/1M in / out | Notes |
| --- | --- | --- | --- |
| Anthropic | `claude-sonnet-5` | $3 / $15 (intro $2/$10 to 2026-08-31 — **decide on list price**) | 1M ctx; native structured outputs |
| Anthropic | `claude-opus-4-8` | $5 / $25 | quality ceiling row |
| OpenAI | `gpt-5.6-terra` | $2.50 / $15 | value row |
| OpenAI | `gpt-5.6-sol` | $5 / $30 | quality ceiling row |
| Google | `gemini-3.5-flash` | $1.50 / $9 | Google's current GA flagship |

Mini (`diagram_generation`):

| Vendor | Model | $/1M in / out |
| --- | --- | --- |
| Google | `gemini-3.1-flash-lite` | $0.25 / $1.50 † |
| OpenAI | `gpt-5.4-mini` | $0.75 / $4.50 † |
| Anthropic | `claude-haiku-4-5` | $1 / $5 |
| OpenAI | `gpt-5.6-luna` | $1 / $6 |

† Verified once from vendor pricing pages 2026-07-17 but not re-confirmed by the reviewer-gate spot-check — **re-verify these two rows (price + structured-output support) as step zero of the benchmark run.**

Exclusions: `gemini-3.1-pro` (Preview, not GA — GA-only rule for launch config; add when GA). Self-hosted open-weight reference for the §3 migration path: **Qwen3.6-35B-A3B** (Apache 2.0, ~17.5 GB at INT4, vLLM ≥ 0.19 with guided decoding via `xgrammar`/`guidance` on the OpenAI-compatible server; source: the Hugging Face model card `Qwen/Qwen3.6-35B-A3B` + vLLM structured-outputs docs, checked 2026-07-17) — superseding the brief's "Qwen3-32B-class" as the current class exemplar; not benchmarked at launch, re-sourced and benchmarked at the migration trigger.

## Harness

- Runs the **actual pipeline** through the production adapter with zero code changes per candidate — the run itself is the proof of the [HARD] config-only-switch rule. A candidate that cannot be swapped by config alone fails the adapter, not the benchmark.
- Fixture set: ≥ 12 topics across ≥ 4 NCE subject areas with frozen retrieval fixtures (recorded Grounding Chunks) so runs are reproducible and isolate model variance from retrieval variance. **Stakeholder-owned action items (block this benchmark's execution, not epic creation):** (1) supply the fixture corpus material; (2) name the two human rubric reviewers. (Ratified 2026-07-18.)
- 3 runs per topic per candidate (variance visibility). Batch APIs (50% off, all vendors) are used for benchmark economics only — never for interactive generation (SM-1).
- Cost accounting comes from the platform's own Cost Telemetry (FR-27) — the benchmark doubles as telemetry verification. Record intro vs list pricing separately.

## Metrics and bars

`lesson_generation`: schema-validity rate first-pass and after one repair loop (bar: ≥ 98% post-repair); citation coverage — % content Blocks whose citations resolve to supplied chunks (bar: 100% per A-5); interactive-Block richness (SM-C2 proxy, ≥ 60% lessons with Quiz+one of Model3D/Simulation); human publishability rubric 1–5 by two reviewers on anonymised outputs (bar: median ≥ 4, proxy for SM-2's 70%); wall-clock median/p90 against SM-1 (< 5 min median, p90 ≤ 2×); fully-loaded cost per lesson vs the $2 soft alert (SM-4).

`simulation_generation`: automated pre-publish check pass rate (loads clean, ready-signal in time, declared params present and keyboard-operable, resource budget); parameter-manifest correctness; reviewer rubric; cost/latency. **OQ-5 stakeholder posture (2026-07-18): the template library is the launch default regardless of this benchmark's outcome** — the ≥ 70% bar gates only whether free-code *activates* behind the tenant flag.

`diagram_generation`: structured-output parse rate (Mermaid/SVG), sanitiser survival rate, label-legibility check pass rate at 360 px, grounding-accuracy rubric on a 30-diagram sample, cost per request, latency p90 (chat-tolerable ≤ 30 s).

Selection rule: for quality-first workloads, the cheapest candidate within 5% of the best rubric score that clears every bar; for `diagram_generation`, the cheapest clearing all bars. Ties break toward the provider already serving another workload (fewer keys/quotas to operate).

## Adapter-critical facts the plan must respect (verified 2026-07-17)

1. **Anthropic's OpenAI-compat endpoint is test-grade**: it ignores `response_format`/`strict` (structured outputs require the native Messages API `output_config.format`) and drops prompt caching. The adapter therefore has **provider drivers behind its OpenAI-compatible consumer interface**: `openai-compatible` driver (OpenAI, Gemini compat endpoint, vLLM, OpenRouter) and a `anthropic-native` translating driver. Consumers still see one OpenAI-compatible interface; the [HARD] §3 rule holds at the consumer boundary.
2. Claude 5-tier models reject non-default `temperature`/`top_p`/`top_k` (Fable 5/Opus 4.8 reject the parameters outright; Sonnet 5 rejects non-default values) — pipeline configs stay sampling-param-free by default; per-workload params live in config and may be provider-conditional inside the adapter.
3. Gemini's OpenAI-compat endpoint (beta) passes structured outputs, streaming, function calling.
4. Prompt caching is GA at all three vendors (~0.1× cached input); the pipeline orders prompts stable-prefix-first (system + Grounding Chunks before per-Block instructions) so per-Block stages hit the cache within a Generation Job.

## Re-run cadence

Re-benchmark on any of: (a) the project-context §3 diagram-spend migration trigger; (b) SM-2 falling below target for a month with generation implicated; (c) a new GA frontier/mini model from an existing provider; (d) every 6 months regardless. Each re-run appends a dated result addendum here; switches ship as config + an evaluation pass (project-context §3).
