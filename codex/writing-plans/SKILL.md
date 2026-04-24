---
name: writing-plans
description: "Breaks an approved design into detailed, atomic 2-5 minute implementation tasks following TDD. Every task includes exact file paths, complete code snippets, and precise verification commands. Use after brainstorming completes. Triggers: \"write a plan\", \"break this into tasks\", \"create implementation plan\", or when brainstorming hands off after design approval."
---

# Writing Plans

Transforms an approved design into a concrete, bite-sized implementation plan that any engineer or subagent can execute without needing additional context.

**Core mandate:** "Write comprehensive plans assuming the engineer has zero context about the codebase and questionable taste."

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

---

## Task Granularity

Each task must be completable in **2-5 minutes** and follow TDD:

1. Write a failing test
2. Verify the test fails (run it and show output)
3. Implement the minimal code to make it pass
4. Verify the test passes
5. Commit

No task should bundle multiple concerns. If a task feels like it has "parts A and B," split it.

---

## Required Plan Structure

### Header Section
```
## Goal
[One sentence: what this plan achieves]

## Architecture Overview
[The key design decisions from brainstorming]

## Tech Stack
[Languages, frameworks, libraries, versions]
```

### Per-Task Format

Each task must include:

| Field | Requirement |
|---|---|
| **File paths** | Exact paths for every file touched — no "update the service" |
| **Code snippets** | Complete, copy-pasteable code — no "add error handling" |
| **Commands** | Exact shell commands with expected output |
| **Verification** | Specific test command + expected pass/fail output |

**Example task:**
```
### Task 3: Add JWT validation middleware

File: src/middleware/auth.ts

Add:
\`\`\`typescript
export function validateJWT(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET!);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}
\`\`\`

Verify:
\`\`\`bash
npm test -- --grep "validateJWT"
# Expected: ✓ returns 401 with no token
# Expected: ✓ returns 401 with invalid token
# Expected: ✓ calls next() with valid token
\`\`\`

Commit: "feat: add JWT validation middleware"
```

---

## Where to Save

Save plan to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

Create the `docs/plans/` directory if it doesn't exist.

---

## After Completing the Plan

Offer two execution options:

**Option A — Subagent-Driven (current session)**
> "I can execute this plan now using `subagent-driven-development` — a fresh subagent per task with two-stage review after each (spec compliance + code quality)."

**Option B — Separate Session**
> "Open a new Claude Code session and use the `executing-plans` skill to execute this plan with human review checkpoints between task batches."

---

## Core Principles

- **DRY** — Do not plan duplicate logic; identify shared abstractions
- **YAGNI** — Do not plan features not explicitly required; include nothing extra
- **TDD** — Failing test before implementation, always, no exceptions
- **Frequent commits** — One commit per task minimum; commits are checkpoints

---

*Based on obra/superpowers — https://github.com/obra/superpowers*
