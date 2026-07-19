#!/usr/bin/env bash
# Operator-initiated deploy (ADR-016). Run from an operator machine with SSH access.
# AI/dev sessions never hold these credentials (stakeholder policy, 2026-07-19) and
# CI holds no VPS secrets — GitHub compromise must not equal VPS compromise.
#
# Usage: EDON_DEPLOY_HOST=user@host [EDON_DEPLOY_PATH=/opt/edon/app] deploy/deploy.sh
set -euo pipefail

HOST="${EDON_DEPLOY_HOST:?set EDON_DEPLOY_HOST=user@host}"
APP_PATH="${EDON_DEPLOY_PATH:-/opt/edon/app}"

echo "==> Sync working tree (git-tracked files only) to ${HOST}:${APP_PATH}"
git ls-files -z | rsync -az --delete --files-from=- --from0 . "${HOST}:${APP_PATH}/"

echo "==> Sync Python environment on the VPS (uv, from the committed lockfile)"
ssh "$HOST" "cd ${APP_PATH} && uv sync --frozen --no-dev --all-packages --python /opt/edon/venv/bin/python"

echo "==> Restart services"
ssh "$HOST" "sudo systemctl restart edon-api.service"
# Worker units are enabled from Epic 2 onward; restart them once they exist:
# ssh "$HOST" "sudo systemctl restart 'edon-worker-*'"

echo "==> Health check"
ssh "$HOST" "curl -fsS http://127.0.0.1:8100/api/v1/health"
echo
echo "deploy OK"
