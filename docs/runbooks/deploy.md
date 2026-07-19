# Runbook: Deploy (staging/prod VPS) — draft (Story 1.2)

**Transport:** operator-initiated rsync over SSH (ADR-016). **Policy (standing, 2026-07-19):** AI/dev sessions never hold VPS credentials; every step here is operator-run. CI verifies; it never deploys.

## 1. One-time VPS provision

```bash
# as root on the VPS (Ubuntu LTS assumed)
adduser --system --group --home /opt/edon edon
mkdir -p /opt/edon/app /var/lib/edon /etc/edon
chown -R edon:edon /opt/edon /var/lib/edon
apt install -y nginx certbot python3-certbot-nginx rsync curl
curl -LsSf https://astral.sh/uv/install.sh | sh   # uv for the edon user's env
sudo -u edon uv venv --python 3.12 /opt/edon/venv
```

## 2. Environment file

```bash
cp .env.example /etc/edon/edon.env   # then edit: EDON_ENV=staging, real values
chown root:edon /etc/edon/edon.env && chmod 640 /etc/edon/edon.env
```

Real secrets exist only here — never in the repo, never in CI (project-context §4).

## 3. systemd units

```bash
cp deploy/systemd/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now edon-api.service
# Worker units ship inert until Epic 2 (Procrastinate) — install but do NOT enable:
#   edon-worker-generation@.service, edon-worker-delivery.service, edon-worker-maintenance.service
systemd-analyze verify /etc/systemd/system/edon-api.service
```

## 4. nginx

```bash
cp deploy/nginx/edon.conf /etc/nginx/sites-available/edon.conf
# edit server_name (replace staging.edon.example)
ln -s /etc/nginx/sites-available/edon.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## 5. TLS (Let's Encrypt)

```bash
certbot --nginx -d <hostname>   # installs cert paths matching deploy/nginx/edon.conf
```

## 6. Deploy (and rollback)

```bash
# from the operator machine, repo root, on the commit CI verified:
EDON_DEPLOY_HOST=<user>@<host> deploy/deploy.sh
# rollback: git checkout <previous-tag> && EDON_DEPLOY_HOST=… deploy/deploy.sh
```

Verify: `curl https://<hostname>/api/v1/health` → `{"status":"ok"}`.

## 7. Branch protection (operator-run, once, after Story 1.2 merges)

Requires repo admin (`gh auth login` as john). Requires CI green on `main` before merge and blocks direct pushes ("no direct pushes to main once CI exists", project-context §8):

```bash
cat > /tmp/protection.json <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["js", "py", "licence-audit", "budgets", "e2e", "npm-audit", "pip-audit", "gitleaks"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
gh api -X PUT "repos/{owner}/{repo}/branches/main/protection" --input /tmp/protection.json
```

## Open items (tracked)

- Backup timer (`edon-backup.timer`: pg_dump + asset rsync off-VPS) — Story 11.5 with the ops runbooks.
- Zero-downtime reload posture — pre-launch hardening (ADR-016 consequences).
- SSE proxy buffering on the progress endpoint — revisit at Story 2.5.
