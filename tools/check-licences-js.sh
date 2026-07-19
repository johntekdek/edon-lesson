#!/usr/bin/env bash
# Licence-audit gate, npm lockfile (AR-25; project-context §5 [HARD]).
# tools/licence-allowlist.txt is the human contract; this maps it to
# license-checker's SPDX vocabulary. Transitive-inclusive, dev deps included.
# Own-code packages (private UNLICENSED workspaces + the root manifest) are excluded.
set -euo pipefail
cd "$(dirname "$0")/.."

ALLOW=$(grep -v '^#' tools/licence-allowlist.txt | grep -v '^$' | paste -sd';' -)

npx license-checker-rseidelsohn \
  --onlyAllow "$ALLOW" \
  --excludePackages "edon-lesson@0.0.0;@edon/lesson-schema@1.0.0;@edon/player@0.0.1;@edon/authoring@0.0.1" \
  --summary

echo "licence-audit (npm) passed"
