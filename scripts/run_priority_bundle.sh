#!/usr/bin/env bash
set -euo pipefail
TOOLS="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PDF="${1:-}"
ID="${2:-}"
if [[ -z "$PDF" ]]; then read -r -p "Private original PDF path: " PDF; fi
if [[ -z "$ID" ]]; then read -r -p "Archive parent external ID: " ID; fi
PDF="$(realpath -- "$PDF")"
umask 077
mkdir -p "$HOME/209-private"
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng ghostscript
python3 -m venv "$HOME/209-private/pdf-venv"
PY="$HOME/209-private/pdf-venv/bin/python"
"$PY" -m pip install 'pypdf>=6,<7' ocrmypdf
"$PY" "$TOOLS/run_priority_bundle.py" --input "$PDF" --parent-external-id "$ID"
