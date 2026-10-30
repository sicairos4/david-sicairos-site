#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(git rev-parse --show-toplevel)"
private_root="${HOME:?HOME is required}/209-private"
mkdir -p "$private_root/source" "$private_root/sql" "$private_root/metrics" "$private_root/android-delivery"
chmod 700 "$private_root" "$private_root/source" "$private_root/sql" "$private_root/metrics" "$private_root/android-delivery"
if ! command -v psql >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends postgresql-client
fi
exclude="$(git rev-parse --git-path info/exclude)"
mkdir -p "$(dirname "$exclude")"
touch "$exclude"
if ! grep -qF '# 209 private Codespaces exclusions' "$exclude"; then
  cat >> "$exclude" <<'EOF'

# 209 private Codespaces exclusions
/private/
**/attachment-index-dataset-*.json
**/scheduler_export*.json
**/creator_engine_metrics.db*
**/creator_engine_benchmark*.json
**/creator_engine_benchmark*.csv
**/archive-import-*.sql
**/archive-import-*.sql.receipt.json
*.keystore
*.jks
.env
.env.*
!.env.example
EOF
fi
printf '%s\n' 'Codespaces tooling installed. No tests, import, metrics collection, publishing or signing-key changes were run.' 'Put genuine source files in $HOME/209-private/source. Configure secrets through Codespaces settings.'
