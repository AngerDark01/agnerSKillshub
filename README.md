# AngerDark01 Skill Hub

Personal AI agent skills managed through `skillshare`.

## Layout

```text
skills/       Categorized skillshare source, grouped for UI management
extras/       Skillshare extras source for rules
templates/    Skill templates
```

`skills/` is the actual skillshare source. Categories are real folders, so the CLI and web UI can manage the hub by group instead of reading a generated flat copy.

## Current Skillshare Source

```text
/home/aseit/桌面/桌面/agener_skillshub/skills
```

Configured target:

```text
codex -> /home/aseit/.codex/skills
mode: copy
target_naming: standard
```

`target_naming: standard` keeps Codex skill folders as clean names such as `skillshare` and `requesting-code-review`, even though the source is grouped under category folders.

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
