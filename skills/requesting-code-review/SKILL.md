---
name: requesting-code-review
description: "Dispatches a code-reviewer subagent to catch issues before they cascade. Mandatory after each task in subagent-driven development, after completing major features, and before merging to main. Triggers: \"request code review\", \"review this code\", \"check my implementation\", or automatically as part of subagent-driven-development workflow."
---

# Requesting Code Review

Dispatch a `code-reviewer` subagent to catch issues before they cascade.

**Core principle:** Review early, review often.

---

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing a major feature
- Before merging to main

**Optional but valuable:**
- When stuck (fresh perspective often finds the issue)
- Before refactoring (establish baseline understanding)
- After fixing a complex bug (verify nothing regressed)

---

## How to Request

### Step 1: Get git SHAs

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or: git rev-parse origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

### Step 2: Dispatch code-reviewer subagent

Use the Task tool with the template in `code-reviewer.md`. Fill in these placeholders:

| Placeholder | What to put |
|---|---|
| `{WHAT_WAS_IMPLEMENTED}` | What you just built (e.g., "JWT validation middleware") |
| `{PLAN_OR_REQUIREMENTS}` | What it should do (paste from plan or describe requirements) |
| `{BASE_SHA}` | Starting commit hash |
| `{HEAD_SHA}` | Ending commit hash |
| `{DESCRIPTION}` | One-sentence summary for context |

### Step 3: Act on Feedback

| Severity | Required Action |
|---|---|
| **Critical** | Fix immediately — do not proceed to next task |
| **Important** | Fix before moving on |
| **Minor** | Note for later; does not block progress |
| **Wrong** | Push back with technical reasoning; involve user if architectural |

---

## Example

```
[Completed Task 2: Add JWT validation middleware]

BASE_SHA=$(git log --oneline | grep "Task 1" | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code-reviewer subagent with template]
- WHAT: JWT validation middleware
- PLAN: Task 2 from docs/plans/auth-implementation.md
- BASE_SHA: a7981ec
- HEAD_SHA: 3df7661
- DESC: Added validateJWT() middleware with 401 handling

[Reviewer returns]:
- Strengths: Clean error handling, tests cover all cases
- Important: Missing rate limiting on auth endpoint
- Minor: Magic number (3600) for token expiry — use config
→ Fix Important issue → re-review → proceed to Task 3
```

---

## Integration with Workflows

**Subagent-Driven Development:** Review after **each** task — catch issues before they compound.

**Executing Plans:** Review after each batch (~3 tasks) — get feedback, apply, continue.

**Ad-Hoc Development:** Review before merging to main.

---

## Red Flags — Never Do These

- "Skip review because it's a simple change"
- Ignore Critical issues and proceed anyway
- Proceed with unfixed Important issues
- Implement review feedback without verifying it's correct for this codebase
- Argue with valid technical feedback without reasoning

---

## Reference

See `code-reviewer.md` in this directory for the full reviewer subagent prompt template.

---

*Based on obra/superpowers — https://github.com/obra/superpowers*
