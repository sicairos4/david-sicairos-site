#!/usr/bin/env bash
set -euo pipefail
umask 077
if [[ "$(id -u)" != 0 ]]; then echo 'Run as a host administrator.' >&2; exit 1; fi
if [[ $# != 1 ]]; then echo 'Usage: bash install-host.sh /absolute/path/to/04_Automation' >&2; exit 1; fi
SOURCE=$(realpath -- "$1")
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
for f in browser_worker.py requirements.txt schema.sql accounts.example.json; do
  [[ -f "$SOURCE/$f" ]] || { echo "Required source file absent: $f" >&2; exit 1; }
done
command -v apt-get >/dev/null || { echo 'This installer targets Debian/Ubuntu Linux.' >&2; exit 1; }
command -v systemctl >/dev/null || { echo 'A systemd host is required.' >&2; exit 1; }
apt-get update
apt-get install -y python3 python3-venv python3-pip
if ! id browser209 >/dev/null 2>&1; then useradd --system --create-home --home-dir /var/lib/209-browser --shell /usr/sbin/nologin browser209; fi
install -d -m 0755 /opt/209-browser /opt/209-browser/worker
install -d -m 0700 /etc/209-browser
install -d -o browser209 -g browser209 -m 0700 /var/lib/209-browser
for f in browser_worker.py requirements.txt schema.sql; do install -m 0644 "$SOURCE/$f" "/opt/209-browser/worker/$f"; done
if [[ ! -f /etc/209-browser/accounts.json ]]; then install -o browser209 -g browser209 -m 0600 "$SOURCE/accounts.example.json" /etc/209-browser/accounts.json; fi
chown root:browser209 /etc/209-browser
chmod 0750 /etc/209-browser
python3 -m venv /opt/209-browser/venv
/opt/209-browser/venv/bin/python -m pip install -r /opt/209-browser/worker/requirements.txt
export PLAYWRIGHT_BROWSERS_PATH=/opt/209-browser/browsers
/opt/209-browser/venv/bin/python -m playwright install --with-deps chromium
if [[ ! -f /etc/209-browser/worker.env ]]; then
  install -m 0600 /dev/null /etc/209-browser/worker.env
  cat > /etc/209-browser/worker.env <<'ENV'
BROWSER_WORKER_ROLE=standby
BROWSER_DATABASE_URL=
BROWSER_ACCOUNTS_FILE=/etc/209-browser/accounts.json
BROWSER_STATE_DIR=/var/lib/209-browser
PLAYWRIGHT_BROWSERS_PATH=/opt/209-browser/browsers
ENV
fi
install -m 0755 "$HERE/run-once.sh" /opt/209-browser/run-once.sh
install -m 0644 "$HERE/209-browser.service" /etc/systemd/system/209-browser.service
install -m 0644 "$HERE/209-browser.timer" /etc/systemd/system/209-browser.timer
systemctl daemon-reload
printf '%s\n' 'Host files installed. No worker or timer started. Configure private runtime access and account login before activation.'
