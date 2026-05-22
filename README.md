# AngerDark01 Skill Hub

Personal AI agent skills managed through `skillshare`.

## Layout

```text
skills/      Flat skill source used by skillshare
catalog/     Human-readable category index
extras/      Candidate rules, commands, prompts
agents/      Reserved for standalone agent definitions
templates/   Skill templates
```

The `skills/` directory is intentionally flat. This keeps skill names stable when syncing to Codex and other tools. Classification lives in `catalog/README.md` and `skills.yaml`.

## Current Skillshare Source

```text
/home/aseit/桌面/桌面/agener_skillshub/skills
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
git commit -m "Reorganize skill hub"
git push origin master
```

Use a normal push unless branch history must also be replaced.
