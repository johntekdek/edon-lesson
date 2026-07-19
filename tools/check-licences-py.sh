#!/usr/bin/env bash
# Licence-audit gate, uv lockfile (AR-25; project-context §5 [HARD]).
# tools/licence-allowlist.txt is the human contract; this maps it to pip-licenses'
# classifier vocabulary (classifier names differ from SPDX ids — both spellings listed).
# Runs against the uv-synced environment; own-code distributions excluded.
set -euo pipefail
cd "$(dirname "$0")/.."

uv run --with pip-licenses pip-licenses \
  --from=mixed \
  --allow-only="MIT;MIT License;BSD-2-Clause;BSD-3-Clause;BSD License;Apache-2.0;Apache Software License;Apache License 2.0;Apache-2.0 OR BSD-2-Clause;ISC;ISC License (ISCL);0BSD;BSD Zero Clause License;PSF-2.0;Python Software Foundation License;Python-2.0;Unlicense;The Unlicense (Unlicense);CC0-1.0;CC0 1.0 Universal (CC0 1.0) Public Domain Dedication;BlueOak-1.0.0;Blue Oak Model License (BlueOak-1.0.0);OFL-1.1;SIL Open Font License 1.1 (OFL-1.1);MPL-2.0;Mozilla Public License 2.0 (MPL 2.0)" \
  --ignore-packages edon-backend edon-lesson-schema

echo "licence-audit (uv) passed"
