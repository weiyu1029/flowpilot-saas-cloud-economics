#!/usr/bin/env bash
set -euo pipefail
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_URL="${1:-https://github.com/weiyu1029/flowpilot-saas-cloud-economics.git}"
TARGET_DIR="${2:-$HOME/Documents/GitHub/flowpilot-saas-cloud-economics}"
mkdir -p "$(dirname "$TARGET_DIR")"
if [ ! -d "$TARGET_DIR/.git" ]; then git clone "$REPO_URL" "$TARGET_DIR"; else git -C "$TARGET_DIR" pull --rebase origin main; fi
rsync -av --delete --exclude='.git/' --exclude='.venv/' "$SOURCE_DIR/" "$TARGET_DIR/"
cd "$TARGET_DIR"
git add -A
git diff --cached --check
if ! git diff --cached --quiet; then git commit -m "Add complete FlowPilot SaaS cloud economics portfolio"; fi
git pull --rebase origin main
git push -u origin main
