#!/usr/bin/env bash
# No-TypeScript gate ([HARD] project-context §2, CI-enforced per §9).
# Any .ts/.tsx file tracked under the fenced directories fails the build.
set -euo pipefail

matches=$(git ls-files -- \
  'player/**/*.ts' 'player/**/*.tsx' \
  'authoring/**/*.ts' 'authoring/**/*.tsx' \
  'schema/js/**/*.ts' 'schema/js/**/*.tsx')

if [ -n "$matches" ]; then
  echo "no-TypeScript gate FAILED — .ts/.tsx files are forbidden in player/, authoring/, schema/js ([HARD] rule):"
  echo "$matches"
  exit 1
fi
echo "no-TypeScript gate passed"
