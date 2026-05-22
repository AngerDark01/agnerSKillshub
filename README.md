# AngerDark01 Skill Hub

Personal AI agent skills managed through `skillshare`.

## Layout

```text
skills/       Categorized source of truth for human review and editing
sync/skills/  Generated flat source used by skillshare, ignored by Git
catalog/      Category guide and rationale
extras/       Candidate rules, commands, prompts
agents/       Reserved for standalone agent definitions
templates/    Skill templates
scripts/      Maintenance scripts
```

`skills/` is intentionally categorized by function. `sync/skills/` is generated because skillshare turns nested source paths into names such as `category__skill-name`; Codex should keep the clean original names.

## Rebuild Sync Source

Run this after editing categorized skills:

```bash
scripts/rebuild-sync.sh
skillshare sync --dry-run
skillshare sync --force
```

## Current Skillshare Source

```text
/home/aseit/桌面/桌面/agener_skillshub/sync/skills
```

Configured target:

```text
codex -> /home/aseit/.codex/skills
```

## Common Commands

```bash
skillshare status
skillshare list
skillshare diff
skillshare sync --dry-run
skillshare sync --force
skillshare doctor
```

## Web UI

```bash
skillshare ui --port 19420 --no-open
```

Open:

```text
http://127.0.0.1:19420
```

## Publish

Use the existing remote:

```text
git@github.com:AngerDark01/agnerSKillshub.git
```

Normal publish flow:

```bash
git status
git add .
git commit -m "Organize skills by function"
git push origin master
```

Use a normal push unless branch history must also be replaced.
