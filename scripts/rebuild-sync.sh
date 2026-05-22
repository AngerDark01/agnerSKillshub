#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_root="$repo_root/skills"
sync_root="$repo_root/sync/skills"

rm -rf "$sync_root"
mkdir -p "$sync_root"

find "$source_root" -mindepth 3 -maxdepth 3 -type f -name SKILL.md | sort | while IFS= read -r skill_file; do
  skill_dir="$(dirname "$skill_file")"
  skill_name="$(basename "$skill_dir")"
  rsync -a --delete "$skill_dir/" "$sync_root/$skill_name/"
done

find "$sync_root" -type d -name output -prune -exec rm -rf {} +
find "$sync_root" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$sync_root" -type f \( -name '*.pyc' -o -name '.DS_Store' \) -delete

cat > "$sync_root/.skillignore" <<'EOF'
**/.DS_Store
**/.git/**
**/output/**
**/__pycache__/**
*.pyc
EOF

count="$(find "$sync_root" -mindepth 2 -maxdepth 2 -type f -name SKILL.md | wc -l)"
printf 'Rebuilt %s skills in %s\n' "$count" "$sync_root"
