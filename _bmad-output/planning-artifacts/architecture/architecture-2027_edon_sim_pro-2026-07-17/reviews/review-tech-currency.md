# Reviewer Lens — Tech Currency & Reality-Check

**Artifact:** `ARCHITECTURE-SPINE.md` (Stack table + AD rules) and `docs/adr/*` (ADR-001, ADR-002, ADR-003, ADR-012)
**Charge:** verify committed decisions were web-researched / reality-checked rather than asserted from training data.
**Review date:** 2026-07-17 (all web checks performed today).

## Verdict summary

The spine's currency discipline is genuinely good — most "verified 2026-07-17" claims held up against today's web, including the entire Anthropic/OpenAI/Google model-and-pricing matrix in ADR-002 and the Procrastinate transactional-enqueue property that AD-4 depends on. Two findings matter: the **@gltf-transform CLI licensing fact is stale** (the pinned v4.4.x CLI is MIT, not Prosperity-PPL — a design constraint in ADR-012/the Stack table rests on a now-false fact), and the **React 19.2-on-Chrome-61 device floor is asserted without evidence** and is not exercised by the CI profile as designed.

Counts: **1 critical, 1 high, 3 medium, 5 low.** Plus a verified-clean ledger at the end.

---

## CRITICAL

### C-1 — @gltf-transform/cli v4.4.x is MIT, not Prosperity-PPL; the exclusion rationale is stale

- **Claim (Stack table + ADR-012):** "the v4 CLI is Prosperity-PPL dual-licensed and excluded per §5"; "The `@gltf-transform/cli` v4 binary is excluded: it is Prosperity-PPL/commercial dual-licensed, which violates §5; only the MIT SDK packages enter the dependency tree." The Stack table stamps this "verified current 2026-07-17".
- **What I verified (2026-07-17):**
  - Repo root `LICENSE.md` at `main`: **MIT** (copyright Don McCurdy) — https://github.com/donmccurdy/glTF-Transform/blob/main/LICENSE.md
  - `packages/cli/package.json` at `main`: `@gltf-transform/cli` **4.4.1, license: MIT** — https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/cli/package.json
  - npm registry latest: `@gltf-transform/cli@4.4.1`, **license MIT** — https://registry.npmjs.org/@gltf-transform/cli/latest
  - `packages/core/package.json`: `@gltf-transform/core` 4.4.1, MIT (the SDK-is-MIT half of the claim is correct) — https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/core/package.json
  - gltf-transform.dev search snippets describe the project as "maintained as independent open source under MIT License", with "glTF Transform Pro" existing as a sponsorship/commercial-support offering, not a license gate.
- **Assessment:** The early-v4 CLI (2024) did carry a Prosperity-PPL/commercial dual license — that is the training-data fact the ADR encodes — but at the version the spine actually pins (**4.4.x**) the CLI has returned to MIT. Web searches surfaced **no evidence** that any current 4.4.x package is Prosperity-licensed. The "verified 2026-07-17" stamp on this row is therefore not true: this specific fact was recalled, not re-checked. This is Critical under this lens's rubric because a recorded design decision (build our own ingest script; CLI banned from the dependency tree per §5) rests on the false/stale fact.
- **Blast radius:** benign direction — the chosen architecture (programmatic ingest via the MIT SDK) is safe either way; nothing built on it breaks. But the §5-violation rationale is wrong, the fence is unnecessary, and the team may be planning to re-implement CLI functionality it could legally just use.
- **Correction:** Reword ADR-012 and the Stack table row: the SDK **and** the CLI are MIT at 4.4.x; the historical v4.0-era Prosperity dual-licensing no longer applies at the pinned version. Keep the programmatic-SDK ingest decision if desired (it is still the better architecture for a pipeline step), but drop "violates §5" as the rationale, or re-justify the CLI exclusion on operational grounds. Optionally add a lockfile-time license check (e.g. `license-checker`) so future upstream license changes are caught mechanically rather than by memory.

---

## HIGH

### H-1 — React 19.2 on Chrome 61-era browsers: asserted, not evidenced, and not actually tested by the CI floor as designed

- **Claim (AD-11 + Stack table):** Player floor is ES2017 / `build.target: 'chrome61'`, with React 19.2.x as the Player framework — i.e., an implicit claim that React 19.2 runs on Chrome-61-class (2017) engines/WebViews.
- **What I verified (2026-07-17):**
  - React publishes **no minimum-browser matrix for React 19**. Current docs say only "React supports all modern browsers" + "older browsers need polyfills"; the concrete environment-requirements page is React-18-era legacy documentation (https://legacy.reactjs.org/docs/javascript-environment-requirements.html, https://react.dev/blog/2024/12/05/react-19). No source found that states React 19.x is supported or tested on Chrome 61.
  - Transpilation covers **syntax only**. Vite's `build.target` explicitly performs no polyfilling — missing *built-ins* on Chrome 61 remain missing: `globalThis` (Chrome 71 — https://mathiasbynens.be/notes/globalthis), `queueMicrotask` (71), `Promise.finally` (63), `Object.fromEntries` (73), `Array.prototype.flat` (69), `reportError` (95, used by React 19's default `createRoot` error handling — guarded, but a fallback path that has never been exercised in this design). Any one of these appearing unguarded in React 19.2, a transitive dep, or app code is a hard runtime crash on the floor device.
  - The AD-11 CI low-spec profile (Playwright + CDP CPU 6× + network shaping + memory cap) runs **current headless Chromium** — throttling a 2026 engine never exercises a 2017 engine's missing built-ins. The floor as specified can pass CI and still crash on the actual floor device.
- **Assessment:** Not proven false, but this is a committed device-floor budget resting on an unverifiable assertion — exactly what this lens is chartered to flag. The recorded Preact-swap option is a real mitigation but is itself unevaluated against the same floor.
- **Correction:** (a) add a targeted polyfill layer for the floor (core-js entries for the built-ins above, or `vite-plugin-legacy`'s modern-polyfills mode) and/or a static gate (`eslint-plugin-compat` / browserslist `chrome >= 61`) in CI; (b) add at least one real old-engine smoke (BrowserStack/LambdaTest Chrome 61 or an Android 8-era WebView) to the pre-launch checklist so the ES2017 floor is evidenced once by an actual run, not only by throttled modern Chromium.

---

## MEDIUM

### M-1 — Vite 8 lib-mode IIFE + targets: real and supported, with one Rolldown-migration caveat to encode

- **Claim (AD-11 + Stack):** Player ships as Vite 8 lib-mode IIFE with `build.target`/`cssTarget: 'chrome61'`.
- **What I verified (2026-07-17):** Vite 8 (Rolldown/Oxc-based) still supports lib mode with `iife` format (`name` required for iife/umd); `build.cssTarget: 'chrome61'` is a documented, current example in the Vite build-options docs (the Android WeChat WebView case), and browser-version strings remain valid `build.target` values. Sources: https://vite.dev/config/build-options, https://vite.dev/guide/migration, https://github.com/vitejs/vite/blob/main/docs/config/build-options.md.
- **Gap:** the Vite 7→8 migration notes state **`import.meta.url` is no longer polyfilled in UMD/IIFE output** (replaced with `undefined`). For a self-contained IIFE Player that lazy-loads chunks/assets, any `import.meta.url`-relative asset resolution silently breaks. Not flagged anywhere in the spine.
- **Correction:** verified — keep the decision; add a Player-build rule: no `import.meta.url`-based asset resolution in the IIFE bundle (asset URLs must come from the mount `opts`/manifest), and check this at CI.

### M-2 — Self-hosted migration-path row (Qwen3.6-35B-A3B, vLLM ≥ 0.19, xgrammar/guidance) not verified

- **Claim (ADR-002 exclusions):** "Qwen3.6-35B-A3B (Apache 2.0, ~17.5 GB at INT4, vLLM ≥ 0.19 with guided decoding via xgrammar/guidance…)" as the §3 migration-path exemplar.
- **What I checked:** I performed no successful web confirmation of this model name, its quantized size, or the vLLM 0.19 guided-decoding claim in this review; nothing in the artifact cites a source for it either, and the model/version naming is post-training-data for any reviewer — it must be sourced, not recalled.
- **Assessment:** Explicitly *not* launch-blocking (ADR-002 says it is benchmarked only at the migration trigger), so Medium, not High. But it is a named-tech row with no currency evidence.
- **Correction:** mark the row "class exemplar — re-verify at migration trigger" (partially done) **and** add the vendor/model-card URL when the ADR is next touched, or strip the specific INT4-size/vLLM-version numerals, which create false precision.

### M-3 — Mini-tier candidate rows partially unverified (gpt-5.4-mini, gemini-3.1-flash-lite)

- **Claim (ADR-002 mini table):** `gemini-3.1-flash-lite` $0.25/$1.50; `gpt-5.4-mini` $0.75/$4.50 (alongside `claude-haiku-4-5` $1/$5 and `gpt-5.6-luna` $1/$6).
- **What I verified:** `claude-haiku-4-5` $1/$5 confirmed (current Anthropic pricing reference); `gpt-5.6-luna` $1/$6 confirmed (https://openai.com/index/gpt-5-6/, https://www.aipricing.guru/openai-pricing/). The **gpt-5.4-mini and gemini-3.1-flash-lite rows were not confirmed** by my spot-checks (the current OpenAI lineup is presented as the 5.6 Sol/Terra/Luna family; older 5.4-generation mini pricing and the 3.1-flash-lite price were not surfaced).
- **Assessment:** Half the mini table is evidenced, half is not. Since the benchmark's cost-first selection depends on these prices being real GA prices, unverified rows can skew the plan.
- **Correction:** before the benchmark runs (it is a pre-launch work item, so there is time), re-confirm both rows against vendor pricing pages and note whether `gpt-5.4-mini` is still a served/GA model in July 2026 or superseded by `gpt-5.6-luna`.

---

## LOW

### L-1 — Stack-table pins not individually spot-checked (plausible, self-correcting)

Pydantic 2.13.x, SQLAlchemy 2.0.51/Alembic 1.18.x, uvicorn 0.51.x, jsonschema 4.26.x, openai SDK 2.46.x, Playwright 1.61.x, Three.js 0.185, DOMPurify 3.4.x, ajv 8.20.x, httpx 0.28.x ("release-frozen upstream" — consistent with httpx's known post-0.28 release freeze, but not re-confirmed today). All are `.x`-ranged seeds with the stated rule "the code owns exact pins once lockfiles exist", which is the correct discipline — wrong minors self-correct at cold-start. No action beyond normal lockfile creation. (FastAPI and Procrastinate rows *were* verified — see ledger.)

### L-2 — nginx `X-Accel-Redirect` authz-then-stream: long-stable, low-risk

Decades-old documented nginx mechanism (nginx docs/wiki "X-Accel"; `internal` location + app-set header). No sign of deprecation; the pattern in AD-9/ADR-012 is standard. Not re-fetched today; risk of staleness ≈ nil. Verified-by-stability.

### L-3 — PostgreSQL 18 RLS + per-request session GUC: still the standard pattern

`CREATE POLICY … USING (tenant_id = current_setting('app.tenant_id')::…)` with `SET LOCAL` per transaction remains the canonical Postgres multi-tenant defense-in-depth pattern; nothing in PG 18 release material changes RLS/GUC semantics. AD-6 stands. (uuidv7 side of PG18 fully verified — see ledger.)

### L-4 — Claude 5-tier sampling-param claim: one nuance

ADR-002 fact #2 says 5-tier Claude models "reject temperature/top_p/top_k". Verified with one nuance: Sonnet 5 rejects **non-default** values (defaults/omission accepted); Fable 5/Opus 4.8/4.7 reject the parameters outright. The ADR's operative rule ("pipeline configs stay sampling-param-free by default") is correct either way. Optional one-word fix ("non-default").

### L-5 — Two dated assertions accepted as-is

(a) "WebView-shell browsers lack Web Speech entirely — verified" (AD-10): consistent with Android WebView's known lack of `speechSynthesis`; not re-tested here — the bounded-start watchdog makes the design safe even if wrong. (b) "Moodle 5.3 ships 2026-10" (Deferred table): not verified; already correctly parked as a deferred re-validation item at plugin-epic start. No action.

---

## Verified-clean ledger (claims checked today that held)

| Claim (where) | Result | Source |
| --- | --- | --- |
| Procrastinate 3.9.x exists & active (AD-4/ADR-003) | ✅ 3.9.0 released 2026-06-20; steady 2026 cadence | https://procrastinate.readthedocs.io/en/stable/changelog.html , https://pypi.org/project/procrastinate/ |
| Transactional enqueue in caller's own transaction (AD-4/ADR-003) | ✅ v3.8.0 (2026-03-28) added external-connection support for **atomic job deferral** — defer in the same DB transaction as the domain write; docs carry a "Using an external database connection" production how-to. Note: this landed in 3.8 — the ≥3.9 pin is load-bearing for AD-4; don't let a resolver downgrade below 3.8. | changelog above; https://procrastinate.readthedocs.io/ (production → external connection) |
| PostgreSQL 18 native `uuidv7()` (Stack "IDs UUIDv7" + PG 18.x) | ✅ PG18 ships `uuidv7()` (+`uuidv4()` alias, `uuid_extract_timestamp` v7 support), monotonic per backend | https://www.thenile.dev/blog/uuidv7 , https://neon.com/postgresql/18/uuidv7-support |
| Anthropic OpenAI-compat endpoint is test-grade; drops structured outputs & prompt caching (AD-3/ADR-002 fact #1) | ✅ official docs: intended to test/compare; `strict` ignored (no schema guarantee); prompt caching unsupported → the two-driver design (openai-compatible + anthropic-native) is correctly motivated | https://docs.anthropic.com/en/api/openai-sdk |
| `claude-sonnet-5` $3/$15, intro $2/$10 **through 2026-08-31**; 1M ctx; structured outputs (ADR-002) | ✅ exact match, including the intro-expiry date the ADR flags for decision | Anthropic current pricing/model reference (checked via claude-api reference, cached 2026-06-24, consistent with vendor page) |
| `claude-opus-4-8` $5/$25; `claude-haiku-4-5` $1/$5 (ADR-002) | ✅ | same |
| `gpt-5.6-terra` $2.50/$15; `gpt-5.6-sol` $5/$30; `gpt-5.6-luna` $1/$6; family GA 2026-07-09 (ADR-002) | ✅ all three tiers + prices + GA status confirmed | https://openai.com/index/gpt-5-6/ , https://simonwillison.net/2026/Jul/9/gpt-5-6/ , https://www.aipricing.guru/openai-pricing/ |
| `gemini-3.5-flash` GA + $1.50/$9 (ADR-002) | ✅ GA 2026-05-19, $1.50/$9, cached input $0.15 (≈0.1×) | https://simonwillison.net/2026/May/19/gemini-35-flash/ , https://devtk.ai/en/models/gemini-3-5-flash/ |
| `gemini-3.1-pro` excluded as Preview-not-GA (ADR-002) | ✅ still Pre-GA/Preview terms as of July 2026 | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-pro |
| Prompt caching GA all three vendors, ~0.1× cached input (ADR-002 fact #4) | ✅ Anthropic 0.1× reads; OpenAI 90% cached-read discount (GPT-5.6 explicit breakpoints); Gemini $0.15 vs $1.50 | sources above |
| FastAPI 0.139.x current (ADR-001, Stack) | ✅ 0.139.0 → 2026-07-01; 0.139.2 → 2026-07-16 (ADR-001's exact "0.139.2 verified 2026-07-17" checks out) | https://github.com/fastapi/fastapi/releases , https://pypi.org/project/fastapi/ |
| Playwright + CDP `Emulation.setCPUThrottlingRate` (AD-11 CI profile) | ✅ standard supported pattern via `context.newCDPSession(page)`; rate 4–6× is common CI practice | https://charpeni.com/blog/how-to-easily-reproduce-a-flaky-test-in-playwright , https://github.com/microsoft/playwright/issues/29155 |
| Vite 8 lib-mode IIFE + `cssTarget: 'chrome61'` (AD-11) | ✅ real, documented (see M-1 for the one caveat) | https://vite.dev/config/build-options |
| @gltf-transform SDK packages (core/extensions/functions) MIT (Stack/ADR-012) | ✅ the SDK half of the claim is correct (see C-1 for the CLI half) | https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/core/package.json |

## Required actions (for the gate)

1. **C-1:** correct the @gltf-transform licensing statement in ADR-012 and the Stack table; re-decide (or re-justify) the CLI exclusion on true grounds. *(Must-fix before spine leaves draft — it carries a false "verified" stamp.)*
2. **H-1:** add a floor-polyfill/compat-lint decision and one real old-engine smoke to make the Chrome-61 floor evidenced rather than asserted.
3. **M-1..M-3:** encode the `import.meta.url` IIFE rule; source or soften the Qwen/vLLM row; re-verify the two unconfirmed mini-tier price rows before the benchmark runs.
