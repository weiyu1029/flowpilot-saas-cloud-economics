#!/bin/bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_NAME="flowpilot-saas-cloud-economics"
REPO_URL="https://github.com/weiyu1029/${REPO_NAME}.git"
TARGET_ROOT="$HOME/Documents/GitHub"
TARGET_DIR="$TARGET_ROOT/$REPO_NAME"

printf '\nFlowPilot safe publisher\n'
printf 'Source: %s\nTarget: %s\nRemote: %s\n\n' "$SOURCE_DIR" "$TARGET_DIR" "$REPO_URL"

command -v git >/dev/null 2>&1 || { echo "Git is not installed. Run: xcode-select --install"; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo "rsync is required."; exit 1; }

mkdir -p "$TARGET_ROOT"
if [ -e "$TARGET_DIR" ] && [ ! -d "$TARGET_DIR/.git" ]; then
  BACKUP="${TARGET_DIR}-backup-$(date +%Y%m%d-%H%M%S)"
  echo "Existing non-Git folder found. Moving it to: $BACKUP"
  mv "$TARGET_DIR" "$BACKUP"
fi

if [ ! -d "$TARGET_DIR/.git" ]; then
  git clone "$REPO_URL" "$TARGET_DIR"
else
  git -C "$TARGET_DIR" remote set-url origin "$REPO_URL"
  git -C "$TARGET_DIR" pull --rebase origin main
fi

[ -f "$SOURCE_DIR/streamlit_app.py" ] || { echo "streamlit_app.py not found in source package."; exit 1; }
[ -d "$TARGET_DIR/.git" ] || { echo "Target clone is invalid."; exit 1; }

rsync -av --delete \
  --exclude='.git/' \
  --exclude='.venv/' \
  --exclude='venv/' \
  --exclude='__pycache__/' \
  --exclude='.pytest_cache/' \
  "$SOURCE_DIR/" "$TARGET_DIR/"

cd "$TARGET_DIR"

SENSITIVE=$(find . -type f \( -name '*.pem' -o -name '*.key' -o -name '.env' -o -name 'secrets.toml' \) -not -path './.git/*' -print)
if [ -n "$SENSITIVE" ]; then
  echo "Refusing to push possible secrets:"
  echo "$SENSITIVE"
  exit 1
fi

if find . -type f -size +99M -not -path './.git/*' | grep -q .; then
  echo "Refusing to push: a file exceeds GitHub's standard 100 MiB per-file limit."
  find . -type f -size +99M -not -path './.git/*' -print
  exit 1
fi

git add -A
git diff --cached --check

if git diff --cached --quiet; then
  echo "No new changes to commit."
else
  git commit -m "Add complete FlowPilot SaaS cloud economics portfolio"
fi

git pull --rebase origin main
git push -u origin main

printf '\nPush complete.\n'
git status --short
git log -1 --oneline
open "https://github.com/weiyu1029/$REPO_NAME"
open "https://share.streamlit.io/"
printf '\nStreamlit settings:\n  Repository: weiyu1029/%s\n  Branch: main\n  Main file: streamlit_app.py\n  Python: 3.12\n\n' "$REPO_NAME"
read -r -p "Press Enter to close..." _
