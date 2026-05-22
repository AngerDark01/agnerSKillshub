---
name: ui-style-extractor
description: "Connect to an existing Chrome session, collect screenshots and CSS tokens from a target product, and produce reusable style-analysis artifacts for UI design work."
---

# UI Style Extractor

Autonomously browse any product, deeply analyze its visual design language, and output a reusable SKILL.md.

## Trigger
`/ui-extract <url or product description>`

Examples:
- `/ui-extract https://linear.app`
- `/ui-extract Notion`
- `/ui-extract Vercel dashboard 风格`
- `/ui-extract claude.ai` (if already logged in, will explore authenticated UI)

---

## What Happens When You Run This

1. **Connect** to your already-open Chrome (port 9222, with all your logins intact)
2. **Navigate** — direct URL or search if description is vague
3. **Explore autonomously** — the AI decides which pages and interactions reveal the most about the design system
4. **Extract** — screenshots + CSS tokens per page
5. **Analyze** — Claude Vision reads the screenshots + data and writes a design guide
6. **Output** — `output/{product}_{timestamp}/SKILL.md` ready to use

---

## Prerequisites Check

Before running, verify:

```bash
# Chrome is running with debug port?
curl http://localhost:9222/json/version

# If not, launch it:
./launch_chrome.sh
```

If Chrome isn't running with debug port, run `./launch_chrome.sh` first.
This reuses your existing Chrome session — all your logins (Claude, Notion, Linear, etc.) are available to the AI.

---

## Run

```bash
# Activate the virtual environment first
source .venv/bin/activate        # macOS/Linux
# OR
.venv\Scripts\activate           # Windows

# Then run the collector
python scripts/collect.py multi "$URL" output/manual_run
```

Replace `$URL` with the page you want to inspect.

---

## Output Structure

```
output/{product}_{timestamp}/
├── SKILL.md              ← The style guide skill (use this in future projects)
├── raw_css_data.json     ← All extracted CSS tokens and design notes
├── homepage.png          ← Screenshots taken during exploration
├── features_page.png
└── ...
```

---

## Using the Generated SKILL.md

Once generated, you can:

1. **Reference in a project** — paste the SKILL.md content as context when building UI
2. **Install as a skill** — copy to `~/.codex/skills/` for reuse across projects
3. **Combine with ui-ux-pro-max** — use the style guide as constraints when generating UI components

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused on port 9222` | Run `./launch_chrome.sh` |
| `Page not loading` | Check if you need to manually log in first, then rerun |
| `No CSS variables found` | Product uses inline styles — CSS tokens still extracted from computed styles |
| `Screenshots are blank` | Some SPAs need a moment — the AI will retry |
| `API key error` | Set `export ANTHROPIC_API_KEY=sk-ant-...` |

---

## How the AI Decides What to Explore

The AI has full autonomy but follows this reasoning:
- Start at homepage → identify key product pages
- Prioritize pages that show the most UI variety (dashboard > marketing)
- Interact with components: hover states, modals, dropdowns, forms
- If authenticated, explore the core product experience
- Stop when it has enough to write a complete, opinionated style guide

You don't need to guide it — but you can add context:
```
/ui-extract https://linear.app — focus on the issue detail view and keyboard shortcuts UI
```
