# Install

This repository is managed by `skillshare`.

## Local Setup

```bash
skillshare init --source /home/aseit/桌面/桌面/agener_skillshub/skills --targets codex --mode copy --no-copy --no-skill
skillshare target codex --mode copy
skillshare sync --force
```

Current local config already points to:

```text
/home/aseit/桌面/桌面/agener_skillshub/skills
```

## Verify

```bash
skillshare status
skillshare list
skillshare doctor
skillshare diff
```

Expected state:

```text
65 skills
codex target synced
no sync drift
```

## Web UI

```bash
skillshare ui --port 19420 --no-open
```

Open:

```text
http://127.0.0.1:19420
```
